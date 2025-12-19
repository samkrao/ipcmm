import argparse, time
import zmq
from typing import Dict, Any
from ..common import grains, safe_shell
from ..state import apply_state

def run_job(job: Dict[str, Any]) -> Dict[str, Any]:
    jtype = job.get("type")
    if jtype == "cmd":
        cmd = str(job.get("cmd",""))
        rc, out, err = safe_shell(cmd)
        return {"type": "cmd", "cmd": cmd, "rc": rc, "stdout": out, "stderr": err}
    if jtype == "state":
        path = str(job.get("path",""))
        return {"type": "state", "path": path, "apply": apply_state(path, pillar=job.get("pillar") or {})}
    return {"error": "unknown job type", "job": job}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--master", default="127.0.0.1")
    p.add_argument("--pub", type=int, default=5556)
    p.add_argument("--push", type=int, default=5557)
    p.add_argument("--id", required=True)
    p.add_argument("--token", default="dev-token-change-me")
    args = p.parse_args()

    ctx = zmq.Context.instance()

    sub = ctx.socket(zmq.SUB)
    sub.connect(f"tcp://{args.master}:{args.pub}")
    sub.setsockopt_string(zmq.SUBSCRIBE, args.id)  # topic = minion id

    push = ctx.socket(zmq.PUSH)
    push.connect(f"tcp://{args.master}:{args.push}")

    print(f"[minion {args.id}] SUB tcp://{args.master}:{args.pub}  PUSH tcp://{args.master}:{args.push}")

    while True:
        try:
            topic, payload = sub.recv_multipart()
            job = json.loads(payload.decode("utf-8"))
            if job.get("token") != args.token:
                continue
            job_id = job.get("job_id")
            result = run_job(job)
            push.send_json({
                "token": args.token,
                "job_id": job_id,
                "minion_id": args.id,
                "grains": grains(),
                "result": result
            })
        except Exception:
            time.sleep(0.2)

if __name__ == "__main__":
    import json
    main()
