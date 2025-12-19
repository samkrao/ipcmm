# mini-salt-triple (Linux)
A **trimmed SaltStack-like** Python toolkit with **three modes** in one repo:

1) **Agent-based HTTP pull** (Salt-like): minions poll master for jobs and post results  
2) **Agentless SSH** (Ansible-like): master runs commands/states over SSH (no minions)  
3) **ZeroMQ** (Salt-internal-like): master pushes jobs via ZMQ, minions subscribe/pull and return results

## Quick start (recommended: Mode 1 HTTP Pull)
### Install deps
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Terminal A: start master
```bash
python -m minisalt.http.master --listen 0.0.0.0 --port 8085
```

### Terminal B: start a minion (same machine for demo)
```bash
python -m minisalt.http.minion --master http://127.0.0.1:8085 --id demo-minion
```

### Queue a job from master CLI
```bash
python -m minisalt.cli http-cmd --master http://127.0.0.1:8085 --target demo-minion -- cmd.run "uname -a"
python -m minisalt.cli http-state --master http://127.0.0.1:8085 --target demo-minion -- state.apply examples/state_basic.yml
python -m minisalt.cli http-results --master http://127.0.0.1:8085 --job <JOB_ID_FROM_COMMAND>
```

---

## Mode 2: Agentless SSH
Requires SSH access to targets.

```bash
python -m minisalt.cli ssh-cmd --inventory examples/inventory.yml --targets web1,web2 -- cmd.run "uptime"
python -m minisalt.cli ssh-state --inventory examples/inventory.yml --targets web1 -- state.apply examples/state_basic.yml
```

Inventory format in `examples/inventory.yml`.

---

## Mode 3: ZeroMQ
### Terminal A: master
```bash
python -m minisalt.zmq.master --bind 0.0.0.0 --pub 5556 --pull 5557
```

### Terminal B: minion
```bash
python -m minisalt.zmq.minion --master 127.0.0.1 --pub 5556 --push 5557 --id demo-minion
```

### Queue job
```bash
python -m minisalt.cli zmq-cmd --master 127.0.0.1 --pub 5556 --target demo-minion -- cmd.run "id"
```

---

## Notes
- This is intentionally minimal (a learning/reference tool).
- Security is **basic**: HTTP mode uses a shared token; ZMQ mode also uses a shared token.
  For real deployments, add TLS/mTLS, per-minion credentials, and audit logging.
