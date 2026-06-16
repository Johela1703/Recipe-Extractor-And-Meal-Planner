from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import Recipe
from backend.schemas import (
    ExtractRequest,
    ExtractResponse,
    RecipeDetail,
    RecipeListItem,
)
from backend.scraper import scrape_url
from backend.llm_processor import extract_recipe

router = APIRouter(prefix="/api", tags=["recipes"])


# ─── Helper: ORM → Schema ─────────────────────────────────────────────────────
def _orm_to_detail(recipe: Recipe) -> RecipeDetail:
    return RecipeDetail(
        id=recipe.id,
        url=recipe.url,
        title=recipe.title,
        cuisine=recipe.cuisine,
        difficulty=recipe.difficulty,
        prep_time=recipe.prep_time,
        cook_time=recipe.cook_time,
        total_time=recipe.total_time,
        servings=recipe.servings,
        ingredients=recipe.ingredients,
        instructions=recipe.instructions,
        nutrition=recipe.nutrition,
        substitutions=recipe.substitutions,
        shopping_list=recipe.shopping_list,
        related_recipes=recipe.related_recipes,
        created_at=recipe.created_at,
    )


# ─── POST /api/extract ────────────────────────────────────────────────────────
@router.post("/extract", response_model=ExtractResponse)
def extract_recipe_endpoint(request: ExtractRequest, db: Session = Depends(get_db)):
    """
    Accepts a recipe blog URL, scrapes it, processes via LLM, stores in DB,
    and returns structured JSON.
    """
    url = str(request.url).strip()

    # ── Caching: return existing if URL already processed ──────────────────
    existing = db.query(Recipe).filter(Recipe.url == url).first()
    if existing:
        return ExtractResponse(
            success=True,
            message="Recipe loaded from cache (already processed).",
            data=_orm_to_detail(existing),
        )

    # ── Scrape ────────────────────────────────────────────────────────────
    try:
        raw_html, page_text = scrape_url(url)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=str(e))

    # ── LLM Processing ────────────────────────────────────────────────────
    try:
        recipe_data = extract_recipe(page_text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # ── Persist to DB ─────────────────────────────────────────────────────
    db_recipe = Recipe(
        url=url,
        raw_html=raw_html,
        title=recipe_data.get("title"),
        cuisine=recipe_data.get("cuisine"),
        difficulty=recipe_data.get("difficulty"),
        prep_time=recipe_data.get("prep_time"),
        cook_time=recipe_data.get("cook_time"),
        total_time=recipe_data.get("total_time"),
        servings=recipe_data.get("servings"),
        ingredients=recipe_data.get("ingredients"),
        instructions=recipe_data.get("instructions"),
        nutrition=recipe_data.get("nutrition"),
        substitutions=recipe_data.get("substitutions"),
        shopping_list=recipe_data.get("shopping_list"),
        related_recipes=recipe_data.get("related_recipes"),
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)

    return ExtractResponse(
        success=True,
        message="Recipe extracted and stored successfully.",
        data=_orm_to_detail(db_recipe),
    )


# ─── GET /api/recipes ─────────────────────────────────────────────────────────
@router.get("/recipes", response_model=List[RecipeListItem])
def list_recipes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Return paginated list of all saved recipes for the history view."""
    recipes = (
        db.query(Recipe)
        .order_by(Recipe.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        RecipeListItem(
            id=r.id,
            url=r.url,
            title=r.title,
            cuisine=r.cuisine,
            difficulty=r.difficulty,
            created_at=r.created_at,
        )
        for r in recipes
    ]


# ─── GET /api/recipes/{id} ────────────────────────────────────────────────────
@router.get("/recipes/{recipe_id}", response_model=RecipeDetail)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Return full details for a single recipe by ID."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe with id {recipe_id} not found")
    return _orm_to_detail(recipe)
