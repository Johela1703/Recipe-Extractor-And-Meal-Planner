# 🍽️ KlarityBytes — AI Recipe Extractor & Meal Planner

A full-stack AI-powered application that extracts structured recipe information from recipe blog URLs, stores recipes in PostgreSQL, and generates intelligent meal plans with consolidated shopping lists and meal-prep recommendations.

Built using **FastAPI**, **PostgreSQL**, **BeautifulSoup**, **OpenRouter LLM**, and a responsive frontend.

---

# 📌 Project Overview

The application performs the following tasks:

* Scrapes recipe blog URLs
* Extracts structured recipe data using AI
* Stores recipes in PostgreSQL
* Displays saved recipes with detailed views
* Generates consolidated shopping lists
* Creates meal prep guidelines from multiple recipes

---

# 🛠️ Tech Stack

| Layer        | Technology            |
| ------------ | --------------------- |
| Backend      | FastAPI               |
| Database     | PostgreSQL            |
| ORM          | SQLAlchemy            |
| Web Scraping | BeautifulSoup4        |
| AI Provider  | OpenRouter            |
| AI SDK       | OpenAI SDK            |
| Frontend     | HTML, CSS, JavaScript |
| Server       | Uvicorn               |

---

# 📂 Project Structure

```text
recipe-extractor/
│
├── backend/
│   ├── config.py
│   ├── database.py
│   ├── llm_processor.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── scraper.py
│   └── routers/
│       ├── recipes.py
│       └── meal_planner.py
│
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── styles.css
│
├── prompts/
│   ├── recipe_extraction.txt
│   └── meal_planning.txt
│
├── assets/
│   ├── extract-recipe.png
│   ├── saved-recipes.png
│   ├── backend-output.png
│   └── meal-planner.png
│
├── .env
├── requirements.txt
└── README.md
```

---

# ⚙️ Setup Guide

## 1. Clone Repository

```bash
git clone <repository-url>
cd recipe-extractor
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

or

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary beautifulsoup4 openai python-dotenv pydantic-settings requests
```

---

## 4. PostgreSQL Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE recipe_db;
```

---

## 5. Configure Environment Variables

Create a `.env` file in the project root.

```env
OPENROUTER_API_KEY=your_openrouter_api_key

DATABASE_URL=postgresql://postgres:your_password@localhost:5432/recipe_db

LLM_MODEL=openai/gpt-4o-mini
```

---

## 6. Run Application

```bash
uvicorn backend.main:app --reload
```

Application URLs:

```text
Frontend: http://127.0.0.1:8000
Swagger Docs: http://127.0.0.1:8000/docs
```

---

# 🚀 Application Workflow

## 2.1 Recipe Extraction

#### Output

![Recipe Extraction](assets/extract-recipe.png)

---

## 2.3 Backend Processing

#### Output

![Backend Logs](assets/backend-output.png)

---

## 2.4 Saved Recipes

#### Output

![Saved Recipes](assets/saved-recipe.png)

---

## 2.5 Meal Planner

#### Output

![Meal Planner](assets/meal-planner.png)

---

# 📖 API Endpoints

## 3.1 Extract Recipe

### POST

```http
/api/extract
```

Request:

```json
{
  "url": "https://www.allrecipes.com/recipe/219082/classic-caprese-salad/"
}
```

---

## 3.2 Get Saved Recipes

### GET

```http
/api/recipes
```

Returns all stored recipes.

---

## 3.3 Get Recipe By ID

### GET

```http
/api/recipes/{id}
```

Returns detailed recipe information.

---

## 3.4 Generate Meal Plan

### POST

```http
/api/meal-plan
```

Request:

```json
{
  "recipe_ids": [1, 2]
}
```

Generates:

* Consolidated shopping list
* Meal prep guidelines

---

# 🧪 Sample Recipe URL

```text
https://www.allrecipes.com/recipe/219082/classic-caprese-salad/
```

---

# 🔐 Environment Variables

| Variable           | Description                  |
| ------------------ | ---------------------------- |
| OPENROUTER_API_KEY | OpenRouter API Key           |
| DATABASE_URL       | PostgreSQL Connection String |
| LLM_MODEL          | AI Model Name                |

---

# 💾 Database

PostgreSQL stores:

* Recipe Metadata
* Ingredients
* Instructions
* Nutrition Information
* Shopping Lists
* Related Recipes

---

# 🌟 Key Features

✅ AI Recipe Extraction

✅ Nutrition Estimation

✅ Shopping List Generation

✅ Recipe History

✅ PostgreSQL Integration

✅ Meal Planning

✅ Responsive Frontend

✅ FastAPI REST API

---

# 🚀 Future Enhancements

* User Authentication
* Recipe Favorites
* Weekly Meal Scheduling
* Export Shopping Lists to PDF
* Nutrition Goal Tracking
* Recipe Image Generation

---

# 👨‍💻 Author

Developed using:

* FastAPI
* PostgreSQL
* SQLAlchemy
* BeautifulSoup4
* OpenRouter
* OpenAI SDK

---


