# AI-Powered Digital Twin for Skill Gap Analysis

A portfolio MVP built with FastAPI, SQLite, and a responsive HTML/CSS/JavaScript dashboard.

## Run locally (Windows)

1. Open Command Prompt in this folder.
2. Create and activate a virtual environment:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
4. Start the application:
   ```cmd
   uvicorn main:app --reload
   ```
5. Open http://127.0.0.1:8000
6. API docs: http://127.0.0.1:8000/docs

The SQLite database file (`digital_twin.db`) is created automatically when the app starts. This is an MVP with rule-based career profiles, not a trained AI model. Readiness is an illustrative match against the skills defined in `main.py`.
