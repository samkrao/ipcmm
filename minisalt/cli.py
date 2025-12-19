import argparse, json, time, yaml, sys
import requests
import zmq
from .ssh.runner import load_inventory, ssh_cmd, run_state_over_ssh
from .common import new_job_id

def http_cmd(args):
    job = {"type": "cmd", "cmd": args.cmd}
    r = requests.post(args.master + "/v1/enqueue", json={"target": args.target, "token": args.token, "job": job})
    r.raise_for_status()
    print(r.json()["job_id"])

def http_state(args):
    job = {"type": "state", "path": args.path}
    r = requests.post(args.master + "/v1/enqueue", json={"target": args.target, "token": args.token, "job": job})
    r.raise_for_status()
    print(r.json()["job_id"])

def http_results(args):
    r = requests.get(args.master + f"/v1/results/{args.job_id}", params={"token": args.token})
    r.raise_for_status()
    print(json.dumps(r.json(), indent=2))

def ssh_run_cmd(args):
    inv = load_inventory(args.inventory)
    hosts = inv.get("hosts", {})
    targets = [t.strip() for t in args.targets.split(",") if t.strip()]
    for t in targets:
        h = hosts.get(t)
        if not h:
            print(f"[ssh] unknown target {t}", file=sys.stderr)
            continue
        res = ssh_cmd(h, args.cmd)
        print(f"== {t} ==")
        print(res["stdout"], end="")
        if res["stderr"]:
            print(res["stderr"], file=sys.stderr, end="")

def ssh_run_state(args):
    inv = load_inventory(args.inventory)
    hosts = inv.get("hosts", {})
    targets = [t.strip() for t in args.targets.split(",") if t.strip()]
    for t in targets:
        h = hosts.get(t)
        if not h:
            print(f"[ssh] unknown target {t}", file=sys.stderr)
            continue
        res = run_state_over_ssh(h, args.path)
        print(f"== {t} ==")
        print(json.dumps(res, indent=2))

def zmq_send_cmd(args):
    ctx = zmq.Context.instance()
    pub = ctx.socket(zmq.PUB)
    pub.connect(f"tcp://{args.master}:{args.pub}")
    time.sleep(0.2)  # allow connect
    job_id = new_job_id()
    job = {"token": args.token, "job_id": job_id, "type": "cmd", "cmd": args.cmd}
    topic = args.target.encode("utf-8")
    pub.send_multipart([topic, json.dumps(job).encode("utf-8")])
    print(job_id)

def main():
    p = argparse.ArgumentParser(prog="minisalt")
    sub = p.add_subparsers(dest="mode", required=True)

    # HTTP
    p1 = sub.add_parser("http-cmd")
    p1.add_argument("--master", required=True)
    p1.add_argument("--target", required=True)
    p1.add_argument("--token", default="dev-token-change-me")
    p1.add_argument("--", dest="_", nargs="*")
    p1.add_argument("cmd", nargs=argparse.REMAINDER)
    p1.set_defaults(fn=http_cmd)

    p2 = sub.add_parser("http-state")
    p2.add_argument("--master", required=True)
    p2.add_argument("--target", required=True)
    p2.add_argument("--token", default="dev-token-change-me")
    p2.add_argument("--", dest="_", nargs="*")
    p2.add_argument("path")
    p2.set_defaults(fn=http_state)

    p3 = sub.add_parser("http-results")
    p3.add_argument("--master", required=True)
    p3.add_argument("--token", default="dev-token-change-me")
    p3.add_argument("--job", dest="job_id", required=True)
    p3.set_defaults(fn=http_results)

    # SSH
    s1 = sub.add_parser("ssh-cmd")
    s1.add_argument("--inventory", required=True)
    s1.add_argument("--targets", required=True)
    s1.add_argument("--", dest="_", nargs="*")
    s1.add_argument("cmd", nargs=argparse.REMAINDER)
    s1.set_defaults(fn=ssh_run_cmd)

    s2 = sub.add_parser("ssh-state")
    s2.add_argument("--inventory", required=True)
    s2.add_argument("--targets", required=True)
    s2.add_argument("path")
    s2.set_defaults(fn=ssh_run_state)

    # ZMQ
    z1 = sub.add_parser("zmq-cmd")
    z1.add_argument("--master", required=True)
    z1.add_argument("--pub", type=int, default=5556)
    z1.add_argument("--target", required=True)
    z1.add_argument("--token", default="dev-token-change-me")
    z1.add_argument("--", dest="_", nargs="*")
    z1.add_argument("cmd", nargs=argparse.REMAINDER)
    z1.set_defaults(fn=zmq_send_cmd)

    args = p.parse_args()
    # join remainder commands
    if hasattr(args, "cmd") and isinstance(args.cmd, list):
        args.cmd = " ".join(args.cmd).strip()
    args.fn(args)

if __name__ == "__main__":
    main()
