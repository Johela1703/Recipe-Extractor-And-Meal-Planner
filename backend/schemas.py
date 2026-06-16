from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl


# ─── Ingredient ───────────────────────────────────────────────────────────────
class Ingredient(BaseModel):
    quantity: str
    unit: str
    item: str


# ─── Nutrition ────────────────────────────────────────────────────────────────
class Nutrition(BaseModel):
    calories: str
    protein: str
    carbs: str
    fat: str


# ─── Substitution ─────────────────────────────────────────────────────────────
class Substitution(BaseModel):
    original: str
    substitute: str
    note: str


# ─── Shopping List ────────────────────────────────────────────────────────────
class ShoppingList(BaseModel):
    dairy: List[str] = []
    produce: List[str] = []
    pantry: List[str] = []
    meat: List[str] = []
    other: List[str] = []


# ─── Related Recipe ───────────────────────────────────────────────────────────
class RelatedRecipe(BaseModel):
    title: str
    description: str
    estimated_time: Optional[str] = None


# ─── Recipe Detail (Full) ─────────────────────────────────────────────────────
class RecipeDetail(BaseModel):
    id: int
    url: str
    title: Optional[str]
    cuisine: Optional[str]
    difficulty: Optional[str]
    prep_time: Optional[str]
    cook_time: Optional[str]
    total_time: Optional[str]
    servings: Optional[str]
    ingredients: Optional[List[Ingredient]]
    instructions: Optional[List[str]]
    nutrition: Optional[Nutrition]
    substitutions: Optional[List[Substitution]]
    shopping_list: Optional[ShoppingList]
    related_recipes: Optional[List[RelatedRecipe]]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Recipe List Item (for history table) ─────────────────────────────────────
class RecipeListItem(BaseModel):
    id: int
    url: str
    title: Optional[str]
    cuisine: Optional[str]
    difficulty: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Extract Request ──────────────────────────────────────────────────────────
class ExtractRequest(BaseModel):
    url: str


# ─── Extract Response ─────────────────────────────────────────────────────────
class ExtractResponse(BaseModel):
    success: bool
    message: str
    data: Optional[RecipeDetail] = None


# ─── Meal Plan Request ────────────────────────────────────────────────────────
class MealPlanRequest(BaseModel):
    recipe_ids: List[int]


# ─── Meal Plan Response ───────────────────────────────────────────────────────
class MealPlanResponse(BaseModel):
    recipes: List[RecipeListItem]
    merged_shopping_list: ShoppingList
    meal_prep_tips: List[str]
