import argparse, time
import requests
from typing import Dict, Any
from ..common import grains, safe_shell
from ..state import apply_state

def run_job(job: Dict[str, Any], pillar: Dict[str, Any] | None = None) -> Dict[str, Any]:
    jtype = job.get("type")
    if jtype == "cmd":
        cmd = str(job.get("cmd",""))
        rc, out, err = safe_shell(cmd)
        return {"type": "cmd", "cmd": cmd, "rc": rc, "stdout": out, "stderr": err}
    if jtype == "state":
        path = str(job.get("path",""))
        return {"type": "state", "path": path, "apply": apply_state(path, pillar=pillar or {})}
    return {"error": "unknown job type", "job": job}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--master", required=True, help="e.g. http://127.0.0.1:8085")
    p.add_argument("--id", required=True, help="minion id (target)")
    p.add_argument("--token", default="dev-token-change-me")
    p.add_argument("--interval", type=float, default=2.0)
    p.add_argument("--pillar", default="", help="optional JSON pillar string for demo")
    args = p.parse_args()

    pillar = {}
    if args.pillar:
        import json
        pillar = json.loads(args.pillar)

    while True:
        try:
            r = requests.post(args.master + "/v1/poll", json={
                "minion_id": args.id,
                "token": args.token,
                "grains": grains()
            }, timeout=10)
            r.raise_for_status()
            job = r.json().get("job")
            if job:
                job_id = job.get("job_id")
                result = run_job(job, pillar=pillar)
                requests.post(args.master + "/v1/result", json={
                    "minion_id": args.id,
                    "token": args.token,
                    "job_id": job_id,
                    "result": result
                }, timeout=10)
        except Exception:
            pass
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
