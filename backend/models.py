from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from backend.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), unique=True, index=True, nullable=False)
    raw_html = Column(Text, nullable=True)  # bonus: store raw HTML

    # Core recipe fields
    title = Column(String(500), nullable=True)
    cuisine = Column(String(200), nullable=True)
    difficulty = Column(String(50), nullable=True)  # easy / medium / hard
    prep_time = Column(String(100), nullable=True)
    cook_time = Column(String(100), nullable=True)
    total_time = Column(String(100), nullable=True)
    servings = Column(String(100), nullable=True)

    # Structured JSON fields
    ingredients = Column(JSON, nullable=True)     # list of {quantity, unit, item}
    instructions = Column(JSON, nullable=True)    # list of strings

    # LLM-generated fields
    nutrition = Column(JSON, nullable=True)       # {calories, protein, carbs, fat}
    substitutions = Column(JSON, nullable=True)   # list of {original, substitute, note}
    shopping_list = Column(JSON, nullable=True)   # {dairy: [], produce: [], pantry: []}
    related_recipes = Column(JSON, nullable=True) # list of {title, description, url}

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
