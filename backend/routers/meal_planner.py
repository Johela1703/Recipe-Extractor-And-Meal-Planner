from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Recipe
from backend.schemas import MealPlanRequest, MealPlanResponse, RecipeListItem, ShoppingList
from backend.llm_processor import generate_meal_plan

router = APIRouter(prefix="/api", tags=["meal-planner"])


@router.post("/meal-plan", response_model=MealPlanResponse)
def create_meal_plan(request: MealPlanRequest, db: Session = Depends(get_db)):
    """
    Accept a list of recipe IDs (3–5), use LLM to merge shopping lists
    and generate meal prep tips.
    """
    if len(request.recipe_ids) < 2:
        raise HTTPException(status_code=422, detail="Please select at least 2 recipes for meal planning.")
    if len(request.recipe_ids) > 5:
        raise HTTPException(status_code=422, detail="Maximum 5 recipes allowed for meal planning.")

    # Fetch recipes from DB
    recipes = db.query(Recipe).filter(Recipe.id.in_(request.recipe_ids)).all()
    if len(recipes) != len(request.recipe_ids):
        found_ids = {r.id for r in recipes}
        missing = [rid for rid in request.recipe_ids if rid not in found_ids]
        raise HTTPException(status_code=404, detail=f"Recipes not found: {missing}")

    # Build recipe dicts for LLM
    recipe_dicts = [
        {
            "title": r.title,
            "ingredients": r.ingredients or [],
        }
        for r in recipes
    ]

    # LLM call
    try:
        result = generate_meal_plan(recipe_dicts)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    merged_sl = result.get("merged_shopping_list", {})

    return MealPlanResponse(
        recipes=[
            RecipeListItem(
                id=r.id,
                url=r.url,
                title=r.title,
                cuisine=r.cuisine,
                difficulty=r.difficulty,
                created_at=r.created_at,
            )
            for r in recipes
        ],
        merged_shopping_list=ShoppingList(
            dairy=merged_sl.get("dairy", []),
            produce=merged_sl.get("produce", []),
            pantry=merged_sl.get("pantry", []),
            meat=merged_sl.get("meat", []),
            other=merged_sl.get("other", []),
        ),
        meal_prep_tips=result.get("meal_prep_tips", []),
    )
