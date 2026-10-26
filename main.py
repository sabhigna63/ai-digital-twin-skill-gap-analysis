from pathlib import Path
import json, sqlite3
from datetime import datetime, timezone
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE=Path(__file__).resolve().parent
DB=BASE/"digital_twin.db"
STATIC=BASE/"static"
CAREERS={
"Data Analyst":["Python","SQL","Excel","Statistics","Data Visualization","Power BI"],
"Frontend Developer":["HTML","CSS","JavaScript","React","Git","API Integration"],
"Backend Developer":["Python","SQL","REST APIs","FastAPI","Git","Testing"],
"Machine Learning Engineer":["Python","Statistics","Pandas","NumPy","Machine Learning","SQL"],
"Full Stack Developer":["HTML","CSS","JavaScript","React","Python","SQL","REST APIs","Git"],
"Data Scientist":["Python","Statistics","Pandas","NumPy","SQL","Machine Learning","Data Visualization"],
"Cloud Engineer":["Linux","Networking","Git","Cloud Fundamentals","Docker","CI/CD"]}
SKILLS=sorted({s for v in CAREERS.values() for s in v}|{"Java","C++","Communication","Problem Solving","GitHub"})
app=FastAPI(title="Digital Twin Career Intelligence API",version="1.0.0",description="Skill-gap analysis and what-if career readiness simulator.")
def db():
 c=sqlite3.connect(DB,timeout=15); c.row_factory=sqlite3.Row; return c
with db() as c:
 c.execute("""CREATE TABLE IF NOT EXISTS assessments(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,target_career TEXT NOT NULL,current_skills TEXT NOT NULL,planned_skills TEXT NOT NULL,missing_skills TEXT NOT NULL,readiness REAL NOT NULL,future_readiness REAL NOT NULL,created_at TEXT NOT NULL)""")
class Request(BaseModel):
 name:str=Field(min_length=1,max_length=100)
 target_career:str
 current_skills:List[str]=[]
 planned_skills:List[str]=[]
def assess(req):
 if req.target_career not in CAREERS: raise HTTPException(400,"Please select a valid target career.")
 required=CAREERS[req.target_career]
 current=list(dict.fromkeys(x.strip() for x in req.current_skills if x.strip()))
 planned=list(dict.fromkeys(x.strip() for x in req.planned_skills if x.strip()))
 missing=[s for s in required if s not in current]
 future_missing=[s for s in missing if s not in planned]
 ready=round(100*(len(required)-len(missing))/len(required),1)
 future=round(100*(len(required)-len(future_missing))/len(required),1)
 return required,current,missing,planned,ready,future
@app.get("/")
def home(): return FileResponse(STATIC/"index.html")
@app.get("/api/health")
def health():
 with db() as c: c.execute("SELECT 1")
 return {"status":"ok","database":"sqlite"}
@app.get("/api/careers")
def careers(): return {"careers":CAREERS,"skills":SKILLS}
@app.post("/api/assessments")
def create(req:Request):
 if not req.name.strip(): raise HTTPException(400,"Please enter your name.")
 required,current,missing,planned,ready,future=assess(req)
 created=datetime.now(timezone.utc).isoformat(timespec="seconds")
 with db() as c:
  cur=c.execute("INSERT INTO assessments(name,target_career,current_skills,planned_skills,missing_skills,readiness,future_readiness,created_at) VALUES(?,?,?,?,?,?,?,?)",(req.name.strip(),req.target_career,json.dumps(current),json.dumps(planned),json.dumps(missing),ready,future,created))
  ident=cur.lastrowid
 return {"id":ident,"name":req.name.strip(),"target_career":req.target_career,"required_skills":required,"current_skills":current,"missing_skills":missing,"planned_skills":planned,"readiness":ready,"future_readiness":future,"created_at":created}
@app.get("/api/assessments")
def history():
 with db() as c: rows=c.execute("SELECT * FROM assessments ORDER BY id DESC LIMIT 50").fetchall()
 return {"assessments":[{"id":r["id"],"name":r["name"],"target_career":r["target_career"],"current_skills":json.loads(r["current_skills"]),"planned_skills":json.loads(r["planned_skills"]),"missing_skills":json.loads(r["missing_skills"]),"readiness":r["readiness"],"future_readiness":r["future_readiness"],"created_at":r["created_at"]} for r in rows]}
@app.get("/api/assessments/{ident}")
def one(ident:int):
 with db() as c: r=c.execute("SELECT * FROM assessments WHERE id=?",(ident,)).fetchone()
 if not r: raise HTTPException(404,"Assessment not found.")
 return {"id":r["id"],"name":r["name"],"target_career":r["target_career"],"current_skills":json.loads(r["current_skills"]),"planned_skills":json.loads(r["planned_skills"]),"missing_skills":json.loads(r["missing_skills"]),"readiness":r["readiness"],"future_readiness":r["future_readiness"],"created_at":r["created_at"]}
app.mount("/static",StaticFiles(directory=STATIC),name="static")
