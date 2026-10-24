from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
import json
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "digital_twin.db"

CAREERS = {
    "Data Analyst": {
        "skills": ["Python", "SQL", "Excel", "Statistics", "Data Visualization", "Power BI"],
        "description": "Turn data into useful business insights and reports."
    },
    "Frontend Developer": {
        "skills": ["HTML", "CSS", "JavaScript", "React", "Git", "API Integration"],
        "description": "Build responsive, interactive user interfaces for the web."
    },
    "Backend Developer": {
        "skills": ["Python", "SQL", "REST APIs", "FastAPI", "Git", "Testing"],
        "description": "Build server-side applications, APIs, and data systems."
    },
    "Machine Learning Engineer": {
        "skills": ["Python", "Statistics", "Pandas", "NumPy", "Machine Learning", "SQL"],
        "description": "Develop and evaluate models that learn patterns from data."
    },
    "Full Stack Developer": {
        "skills": ["HTML", "CSS", "JavaScript", "React", "Python", "SQL", "REST APIs", "Git"],
        "description": "Build both the frontend and backend of web applications."
    }
}

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                target_career TEXT NOT NULL,
                current_skills TEXT NOT NULL,
                missing_skills TEXT NOT NULL,
                readiness INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Digital Twin Career Intelligence API",
    description="Skill-gap analysis and what-if career readiness simulator.",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

class AssessmentRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    target_career: str
    current_skills: list[str] = Field(default_factory=list)
    planned_skills: list[str] = Field(default_factory=list)

def normalize(items):
    return list(dict.fromkeys(s.strip() for s in items if s and s.strip()))

def analyse(career, current_skills, planned_skills=None):
    if career not in CAREERS:
        raise HTTPException(status_code=400, detail="Please select a supported target career.")
    required = CAREERS[career]["skills"]
    current = normalize(current_skills)
    planned = normalize(planned_skills or [])
    current_lower = {s.casefold() for s in current}
    future_lower = current_lower | {s.casefold() for s in planned}
    missing = [s for s in required if s.casefold() not in current_lower]
    future_missing = [s for s in required if s.casefold() not in future_lower]
    readiness = round(100 * (len(required) - len(missing)) / len(required))
    future_readiness = round(100 * (len(required) - len(future_missing)) / len(required))
    return {
        "target_career": career,
        "career_description": CAREERS[career]["description"],
        "required_skills": required,
        "current_skills": current,
        "missing_skills": missing,
        "matched_skills": [s for s in required if s.casefold() in current_lower],
        "readiness_score": readiness,
        "future_readiness_score": future_readiness,
        "planned_skills": planned,
        "future_missing_skills": future_missing,
        "skills_to_learn": missing[:3],
        "message": (
            "Strong starting point—keep building practical experience."
            if readiness >= 75 else
            "You have a foundation. Focus on the highest-priority missing skills."
            if readiness >= 40 else
            "Start with the fundamentals, then build a small project to demonstrate them."
        )
    }

@app.get("/")
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")

@app.get("/api/careers")
def list_careers():
    return [
        {"name": name, "description": data["description"], "required_skills": data["skills"]}
        for name, data in CAREERS.items()
    ]

@app.post("/api/analyze")
def analyze_skills(payload: AssessmentRequest):
    result = analyse(payload.target_career, payload.current_skills, payload.planned_skills)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """INSERT INTO assessments
            (name, target_career, current_skills, missing_skills, readiness, created_at)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                payload.name.strip(),
                payload.target_career,
                json.dumps(result["current_skills"]),
                json.dumps(result["missing_skills"]),
                result["readiness_score"],
                datetime.utcnow().isoformat(timespec="seconds")
            )
        )
        conn.commit()
        result["assessment_id"] = cursor.lastrowid
    return result

@app.get("/api/assessments")
def list_assessments():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """SELECT id, name, target_career, current_skills, missing_skills,
                      readiness, created_at
               FROM assessments ORDER BY id DESC LIMIT 50"""
        ).fetchall()
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "target_career": row["target_career"],
            "current_skills": json.loads(row["current_skills"]),
            "missing_skills": json.loads(row["missing_skills"]),
            "readiness_score": row["readiness"],
            "created_at": row["created_at"]
        }
        for row in rows
    ]

@app.get("/api/health")
def health():
    return {"status": "ok", "database": "sqlite"}
