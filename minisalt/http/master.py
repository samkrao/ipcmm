import argparse, threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn
from ..common import new_job_id, now_ms

app = FastAPI(title="mini-salt HTTP master")

# In-memory stores (trimmed)
JOBS: Dict[str, Dict[str, Any]] = {}           # job_id -> job
QUEUE: Dict[str, List[str]] = {}               # minion_id -> [job_id,...]
RESULTS: Dict[str, Dict[str, Any]] = {}        # job_id -> results payload

MASTER_TOKEN = "dev-token-change-me"

class EnqueueRequest(BaseModel):
    target: str
    token: str
    job: Dict[str, Any]   # {"type":"cmd"|"state", ...}

class PollRequest(BaseModel):
    minion_id: str
    token: str
    grains: Dict[str, Any] | None = None

class ResultRequest(BaseModel):
    minion_id: str
    token: str
    job_id: str
    result: Dict[str, Any]

@app.get("/v1/health")
def health():
    return {"ok": True}

@app.post("/v1/enqueue")
def enqueue(req: EnqueueRequest):
    if req.token != MASTER_TOKEN:
        raise HTTPException(status_code=401, detail="bad token")
    job_id = new_job_id()
    job = {"job_id": job_id, "target": req.target, "created_ms": now_ms(), **req.job}
    JOBS[job_id] = job
    QUEUE.setdefault(req.target, []).append(job_id)
    return {"job_id": job_id}

@app.post("/v1/poll")
def poll(req: PollRequest):
    if req.token != MASTER_TOKEN:
        raise HTTPException(status_code=401, detail="bad token")
    q = QUEUE.get(req.minion_id, [])
    if not q:
        return {"job": None}
    job_id = q.pop(0)
    job = JOBS.get(job_id)
    return {"job": job}

@app.post("/v1/result")
def result(req: ResultRequest):
    if req.token != MASTER_TOKEN:
        raise HTTPException(status_code=401, detail="bad token")
    RESULTS[req.job_id] = {"minion_id": req.minion_id, "received_ms": now_ms(), "result": req.result}
    return {"ok": True}

@app.get("/v1/results/{job_id}")
def get_results(job_id: str, token: str):
    if token != MASTER_TOKEN:
        raise HTTPException(status_code=401, detail="bad token")
    return {"job": JOBS.get(job_id), "result": RESULTS.get(job_id)}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--listen", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8085)
    p.add_argument("--token", default=MASTER_TOKEN)
    args = p.parse_args()
    global MASTER_TOKEN
    MASTER_TOKEN = args.token
    uvicorn.run("minisalt.http.master:app", host=args.listen, port=args.port, reload=False)

if __name__ == "__main__":
    main()
