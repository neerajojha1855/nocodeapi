# NoCodeAPI: Natural Language Dynamic API Generation Engine

NoCodeAPI is an enterprise-grade engine that allows users to instantly provision production-ready, relational REST APIs using simple natural language prompts. 

The system translates plain English requests (e.g., *"I need an API to track employee certifications"*) into optimized database schemas, physically creates the tables in PostgreSQL, and exposes standardized CRUD endpoints—all without writing or deploying a single line of backend code, and with **zero server downtime**.

## Core Architecture

This project utilizes a unique **In-Memory Meta-Programming Architecture**:
1. **LLM Compiler:** Uses Google Gemini (via `google-genai` and `Pydantic`) to parse natural language into strict JSON schemas.
2. **The Control Plane:** Saves the schema blueprints (`DynamicAPI` and `APIField`) to a central database.
3. **Dynamic DDL Execution:** Bypasses `makemigrations` and uses Django's `schema_editor` to execute raw PostgreSQL `CREATE TABLE` statements on the fly.
4. **Ghost Models:** When a request hits an endpoint, Python's `type()` function instantly constructs a temporary, in-memory Django Model class that matches the database table perfectly.
5. **Dynamic Gateway Routing:** A catch-all Django REST Framework ViewSet (`/api/v1/dynamic/<slug>/`) intercepts traffic, mounts the in-memory ghost model, and processes standard HTTP requests (`GET`, `POST`, `PUT`, `DELETE`).

## Tech Stack
* **Framework:** Django & Django REST Framework (DRF)
* **Database:** PostgreSQL (with `psycopg2-binary`)
* **AI Provider:** Google Gemini (`google-genai`)
* **Data Validation:** Pydantic

## Local Setup

1. **Clone and Install Dependencies**
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Create a `.env` file in the root directory:
   ```env
   DEBUG=True
   ALLOWED_HOSTS=*
   
   GEMINI_API_KEY=your_google_ai_studio_key
   
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=db_name
   DB_USER=db_user
   DB_PASSWORD=db_password
   DB_HOST=db_host
   DB_PORT=db_port
   ```

3. **Initialize the Control Panel**
   ```bash
   python manage.py makemigrations engine
   python manage.py migrate
   python manage.py createsuperuser
   ```

## Usage

### 1. Generate an API using AI
You can instantly generate a live API from your terminal using the custom management command:

```bash
# Generating API for inventory management
python manage.py generate_api "Create an API to track inventory items with quantity and price"

# Employee Management
python manage.py generate_api "Create an API to track employees with their first name, last name, email address, department, date joined, and a boolean for whether they are currently active"

# Library Management
python manage.py generate_api "I need an API to manage library books tracking the ISBN, book title, author, publication year, genre, and whether it is currently checked out"

# Tech Blog Management
python manage.py generate_api "Build an API for a tech blog. It should store the article title, author name, published date, a long text field for the content, and the number of views"
```

### 2. Test the Endpoint
Once the AI returns a success message, open your browser and navigate to the generated slug:
`http://127.0.0.1:8000/api/v1/dynamic/<slug_name>/`

You will see a fully interactive Django REST Framework interface where you can immediately begin sending `POST` and `GET` requests to your new dynamic table.