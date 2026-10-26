# AI-Powered Digital Twin for Skill Gap Analysis

Runnable FastAPI + SQLite MVP with responsive dashboard, skill-gap analysis, what-if learning simulation, saved assessment history, and API endpoints.

## Run locally
1. Python 3.10+ required.
2. `python -m pip install -r requirements.txt`
3. `python -m uvicorn main:app --reload`
4. Open http://127.0.0.1:8000 (API docs: /docs).

SQLite database is created automatically. No .env or external database required.

## API
- GET /api/health
- GET /api/careers
- POST /api/assessments
- GET /api/assessments
- GET /api/assessments/{id}

## PythonAnywhere note
The included WSGI adapter is a configuration example, not a guarantee of compatibility with every PythonAnywhere account/plan. Update YOUR_USERNAME and the project path to match your account, install dependencies in the web app's selected Python environment, configure the WSGI file, then reload. The project is not deployed to your account by this zip alone.
