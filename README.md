# Ecomerce-fastapi
1. Install postgres.
 - If you already have a PostgreSQL database: Change DATABASE_URL in .env
 - Or using docker: Run `docker compose up -d` to start postgres container

2. Create a Python virtual Env
- python3 -m venv venv
- source venv/bin/activate

3. Install package in python
- pip install -r requirements.txt

4. Run migrations
- alembic upgrade head

6. Start application
-  uvicorn app.main:app --reload

7. Access to API documentation swagger
- Open `http://localhost:8000/docs`


# Note if have error in starting 
1. If get error like that:
venv/lib/python3.10/site-packages/passlib/handlers/bcrypt.py", line 620, in _load_backend_mixin
    version = _bcrypt.__about__.__version__
AttributeError: module 'bcrypt' has no attribute '__about__'

Please change to 
venv/lib/python3.10/site-packages/passlib/handlers/bcrypt.py line 620
    version = _bcrypt.__version__