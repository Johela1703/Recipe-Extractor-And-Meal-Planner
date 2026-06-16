import requests
from bs4 import BeautifulSoup
from backend.config import settings
import json


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}


def scrape_url(url: str) -> tuple[str, str]:
    """
    Scrape a recipe blog URL.
    Returns (raw_html, cleaned_text).
    If scraping is blocked, returns a fallback prompt so the LLM
    generates the recipe from its own knowledge of the URL.
    """
    session = requests.Session()

    # Best-effort homepage visit to grab cookies
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        homepage = f"{parsed.scheme}://{parsed.netloc}"
        session.get(homepage, headers=HEADERS, timeout=8, allow_redirects=True)
    except Exception:
        pass

    try:
        response = session.get(
            url,
            headers=HEADERS,
            timeout=settings.REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        response.raise_for_status()
        raw_html = response.text
        cleaned_text = _extract_text(raw_html, url)
        return raw_html, cleaned_text

    except requests.exceptions.Timeout:
        raise ConnectionError(f"Request timed out after {settings.REQUEST_TIMEOUT}s: {url}")
    except requests.exceptions.TooManyRedirects:
        raise ValueError(f"Too many redirects for URL: {url}")
    except (requests.exceptions.HTTPError, requests.exceptions.RequestException):
        # Site blocked scraping — fall back to URL-based generation
        fallback_text = (
            f"The recipe is from this URL: {url}\n"
            f"The website blocked direct scraping (403 Forbidden).\n"
            f"Please use your culinary knowledge to generate a complete, "
            f"accurate recipe for the dish described in this URL. "
            f"Infer the recipe name and details from the URL path."
        )
        return "", fallback_text


def _extract_text(html: str, url: str) -> str:
    """
    Parse HTML — tries JSON-LD schema first (most reliable),
    then falls back to visible text extraction.
    """
    soup = BeautifulSoup(html, "lxml")

    # ── Strategy 1: JSON-LD Recipe Schema ──────────────────────────────────
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            items = data if isinstance(data, list) else data.get("@graph", [data])
            for item in items:
                if isinstance(item, dict) and "Recipe" in str(item.get("@type", "")):
                    parts = []
                    if item.get("name"):
                        parts.append(f"Recipe: {item['name']}")
                    if item.get("description"):
                        parts.append(f"Description: {item['description']}")
                    if item.get("prepTime"):
                        parts.append(f"Prep Time: {item['prepTime']}")
                    if item.get("cookTime"):
                        parts.append(f"Cook Time: {item['cookTime']}")
                    if item.get("totalTime"):
                        parts.append(f"Total Time: {item['totalTime']}")
                    if item.get("recipeYield"):
                        parts.append(f"Servings: {item['recipeYield']}")
                    if item.get("recipeCuisine"):
                        parts.append(f"Cuisine: {item['recipeCuisine']}")
                    if item.get("recipeCategory"):
                        parts.append(f"Category: {item['recipeCategory']}")

                    ingredients = item.get("recipeIngredient", [])
                    if ingredients:
                        parts.append("\nIngredients:")
                        for ing in ingredients:
                            parts.append(f"- {ing}")

                    instructions = item.get("recipeInstructions", [])
                    if instructions:
                        parts.append("\nInstructions:")
                        for i, step in enumerate(instructions, 1):
                            text = step.get("text", "") if isinstance(step, dict) else str(step)
                            parts.append(f"{i}. {text}")

                    nutrition = item.get("nutrition", {})
                    if nutrition:
                        parts.append("\nNutrition:")
                        for k, v in nutrition.items():
                            if k != "@type":
                                parts.append(f"{k}: {v}")

                    result = "\n".join(parts)
                    if len(result) > 100:
                        return result[:12000]
        except Exception:
            continue

    # ── Strategy 2: Visible HTML text ──────────────────────────────────────
    for tag in soup(["script", "style", "nav", "footer", "header",
                     "aside", "noscript", "iframe", "form"]):
        tag.decompose()

    content = (
        soup.find(attrs={"class": lambda c: c and any(
            k in " ".join(c if isinstance(c, list) else [c]).lower()
            for k in ["recipe", "wprm", "tasty", "mv-recipe", "recipe-content"]
        )})
        or soup.find("article")
        or soup.find("main")
        or soup.find("body")
    )

    text = (content or soup).get_text(separator="\n", strip=True)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    cleaned = "\n".join(lines)

    # If still not enough content, fall back to URL-based generation
    if len(cleaned) < 100:
        return (
            f"The recipe is from this URL: {url}\n"
            f"Please use your culinary knowledge to generate a complete, "
            f"accurate recipe for the dish described in this URL."
        )

    return cleaned[:12000]