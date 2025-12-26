FastAPI Todo Backend

A secure Todo API built with FastAPI and PostgreSQL.

Features
- JWT Auth: Secure user login/signup (`auth.py`).
- Database: SQLAlchemy models and migrations (`models.py`).
- Docker: Containerized for easy deployment.

Setup
1. Create .env file:
   DATABASE_URL=your_db_url
   SECRET_KEY=your_secret_key

2. pip install -r requirements.txt
3. fastapi dev todo_app.py
