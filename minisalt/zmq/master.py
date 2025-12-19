import argparse, json, time
import zmq
from typing import Dict, Any
from ..common import new_job_id, now_ms

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bind", default="127.0.0.1")
    p.add_argument("--pub", type=int, default=5556, help="PUB port (master->minions)")
    p.add_argument("--pull", type=int, default=5557, help="PULL port (minions->master results)")
    p.add_argument("--token", default="dev-token-change-me")
    args = p.parse_args()

    ctx = zmq.Context.instance()
    pub = ctx.socket(zmq.PUB)
    pub.bind(f"tcp://{args.bind}:{args.pub}")

    pull = ctx.socket(zmq.PULL)
    pull.bind(f"tcp://{args.bind}:{args.pull}")

    print(f"[master] PUB tcp://{args.bind}:{args.pub}  PULL tcp://{args.bind}:{args.pull}")

    poller = zmq.Poller()
    poller.register(pull, zmq.POLLIN)

    results: Dict[str, Any] = {}

    while True:
        events = dict(poller.poll(200))
        if pull in events:
            msg = pull.recv_json()
            if msg.get("token") != args.token:
                continue
            job_id = msg.get("job_id")
            results[job_id] = msg
            print(f"[master] result job={job_id} from={msg.get('minion_id')} ok")
        # keep running; CLI sends jobs via PUB in a separate process (see minisalt.cli)
        time.sleep(0.01)

if __name__ == "__main__":
    main()
