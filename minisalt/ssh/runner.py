import os, subprocess, shlex, yaml
from typing import Dict, Any, List, Tuple
from ..state import apply_state

def load_inventory(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def ssh_cmd(host: Dict[str, Any], cmd: str) -> Dict[str, Any]:
    user = host.get("user","")
    addr = host.get("host")
    port = int(host.get("port", 22))
    ident = host.get("identity_file","")
    target = f"{user+'@' if user else ''}{addr}"
    ssh = ["ssh", "-p", str(port), "-o", "StrictHostKeyChecking=accept-new"]
    if ident:
        ssh += ["-i", ident]
    ssh += [target, "--", cmd]
    p = subprocess.Popen(ssh, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return {"rc": p.returncode, "stdout": out, "stderr": err, "target": target}

def scp_to(host: Dict[str, Any], local_path: str, remote_path: str) -> Dict[str, Any]:
    user = host.get("user","")
    addr = host.get("host")
    port = int(host.get("port", 22))
    ident = host.get("identity_file","")
    target = f"{user+'@' if user else ''}{addr}:{remote_path}"
    scp = ["scp", "-P", str(port), "-o", "StrictHostKeyChecking=accept-new"]
    if ident:
        scp += ["-i", ident]
    scp += [local_path, target]
    p = subprocess.Popen(scp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return {"rc": p.returncode, "stdout": out, "stderr": err, "target": target}

def run_state_over_ssh(host: Dict[str, Any], state_path: str) -> Dict[str, Any]:
    # simplest: copy state file to /tmp and run a tiny inline python state apply using local engine? 
    # Instead: run commands encoded in state by interpreting locally then sending commands/file content remotely.
    # For trimmed version: support cmd.run + file.managed by SSH commands.
    import yaml
    with open(state_path, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f) or []
    results = []
    for step in doc:
        (fun, args), = step.items()
        args = args or {}
        if fun == "cmd.run":
            cmd = str(args.get("name") or args.get("cmd") or "")
            results.append({"fun": fun, "res": ssh_cmd(host, cmd)})
        elif fun == "file.managed":
            path = str(args["path"])
            content = str(args.get("content",""))
            # create file using cat heredoc (safe-ish)
            heredoc = f"sudo mkdir -p {shlex.quote(os.path.dirname(path) or '.')} && sudo tee {shlex.quote(path)} >/dev/null <<'__MINISALT__'\n{content}\n__MINISALT__\n"
            results.append({"fun": fun, "res": ssh_cmd(host, heredoc)})
        else:
            results.append({"fun": fun, "error": "unsupported in ssh-mode (trimmed)", "step": step})
    return {"ok": True, "steps": results}
