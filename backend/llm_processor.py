import json
import re
from pathlib import Path

from openai import OpenAI

from backend.config import settings

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")


def _call_llm(prompt_text: str) -> str:
    

    client = OpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )

    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt_text
            }
        ]
    )

    return response.choices[0].message.content


def _parse_json(text: str) -> dict | list:
    

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text.strip(),
        flags=re.IGNORECASE
    )

    text = re.sub(r"\s*```$", "", text.strip())
    text = text.strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError as e:
        match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)

        if match:
            return json.loads(match.group(1))

        raise ValueError(
            f"LLM returned invalid JSON: {e}\n\nRaw output:\n{text[:500]}"
        )


def extract_recipe(page_content: str) -> dict:
    

    template = _load_prompt("recipe_extraction.txt")
    prompt_text = template.replace("{page_content}", page_content)

    try:
        raw_output = _call_llm(prompt_text)

    except Exception as e:
        raise ValueError(f"LLM call failed: {str(e)}")

    result = _parse_json(raw_output)

    if not isinstance(result, dict):
        raise ValueError("LLM returned a non-dict JSON object")

    if not result.get("title"):
        raise ValueError(
            "LLM could not identify a recipe in the provided content"
        )

    result.setdefault("ingredients", [])
    result.setdefault("instructions", [])

    result.setdefault(
        "nutrition",
        {
            "calories": "N/A",
            "protein": "N/A",
            "carbs": "N/A",
            "fat": "N/A"
        }
    )

    result.setdefault("substitutions", [])

    result.setdefault(
        "shopping_list",
        {
            "dairy": [],
            "produce": [],
            "pantry": [],
            "meat": [],
            "other": []
        }
    )

    result.setdefault("related_recipes", [])

    return result


def generate_meal_plan(recipes: list[dict]) -> dict:
    

    template = _load_prompt("meal_planning.txt")

    recipe_summary = ""

    for i, recipe in enumerate(recipes, start=1):
        ingredients_text = "\n".join(
            f"  - {ing.get('quantity', '')} "
            f"{ing.get('unit', '')} "
            f"{ing.get('item', '')}"
            for ing in (recipe.get("ingredients") or [])
        )

        recipe_summary += (
            f"\nRecipe {i}: {recipe.get('title', 'Unknown')}\n"
            f"Ingredients:\n{ingredients_text}\n"
        )

    prompt_text = template.replace(
        "{recipes}",
        recipe_summary
    )

    try:
        raw_output = _call_llm(prompt_text)

    except Exception as e:
        raise ValueError(
            f"LLM meal plan call failed: {str(e)}"
        )

    result = _parse_json(raw_output)

    if not isinstance(result, dict):
        raise ValueError(
            "LLM returned invalid response for meal planning"
        )

    result.setdefault(
        "merged_shopping_list",
        {
            "dairy": [],
            "produce": [],
            "pantry": [],
            "meat": [],
            "other": []
        }
    )

    result.setdefault("meal_prep_tips", [])

    return result