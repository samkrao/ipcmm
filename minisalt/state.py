import os
import yaml
from typing import Any, Dict, List
from .common import StepResult, safe_shell, grains

def apply_state(path: str, pillar: Dict[str, Any] | None = None) -> Dict[str, Any]:
    pillar = pillar or {}
    with open(path, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f) or []
    if not isinstance(doc, list):
        raise ValueError("State file must be a YAML list of steps")

    res: List[StepResult] = []
    for i, step in enumerate(doc):
        if not isinstance(step, dict) or len(step) != 1:
            res.append(StepResult(False, False, f"step[{i}]", "Invalid step format", {"step": step}))
            continue
        (fun, args), = step.items()
        try:
            r = _run_step(fun, args, pillar)
            res.append(r)
        except Exception as e:
            res.append(StepResult(False, False, fun, f"Exception: {e}", {"args": args}))
    return {
        "grains": grains(),
        "result": {
            "ok": all(r.ok for r in res),
            "changed": any(r.changed for r in res),
            "steps": [r.__dict__ for r in res],
        }
    }

def _run_step(fun: str, args: Any, pillar: Dict[str, Any]) -> StepResult:
    args = args or {}
    if fun == "cmd.run":
        cmd = _render(str(args.get("name") or args.get("cmd") or ""), pillar)
        rc, out, err = safe_shell(cmd)
        ok = (rc == 0)
        return StepResult(ok, True, fun, f"rc={rc}", {"cmd": cmd, "stdout": out, "stderr": err})
    if fun == "file.managed":
        path = _render(str(args["path"]), pillar)
        content = _render(str(args.get("content","")), pillar)
        mode = args.get("mode")
        changed = _ensure_file(path, content, mode)
        return StepResult(True, changed, fun, "file ensured", {"path": path, "mode": mode})
    if fun == "pkg.install":
        name = _render(str(args["name"]), pillar)
        changed, ok, comment, data = _pkg_install(name)
        return StepResult(ok, changed, fun, comment, data)
    if fun == "service.running":
        name = _render(str(args["name"]), pillar)
        enable = bool(args.get("enable", True))
        changed, ok, comment, data = _service_running(name, enable)
        return StepResult(ok, changed, fun, comment, data)

    return StepResult(False, False, fun, "Unknown function", {"args": args})

def _render(s: str, pillar: Dict[str, Any]) -> str:
    # Very small templating: {{ pillar.key }}
    out = s
    for k, v in (pillar or {}).items():
        out = out.replace("{{ pillar."+k+" }}", str(v))
    return out

def _ensure_file(path: str, content: str, mode: str | None) -> bool:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    prev = None
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            prev = f.read()
    if prev != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        if mode:
            os.chmod(path, int(str(mode), 8))
        return True
    if mode:
        os.chmod(path, int(str(mode), 8))
    return False

def _pkg_install(name: str):
    g = grains()
    mgr = g.get("pkg_mgr", "unknown")
    # idempotency: check presence via command exists for common tools; fallback to install attempt
    if mgr == "apt-get":
        rc, out, err = safe_shell(f"dpkg -s {name} >/dev/null 2>&1 || sudo apt-get update -y && sudo apt-get install -y {name}")
        ok = (rc == 0)
        return True, ok, "attempted apt install", {"mgr": mgr, "stdout": out, "stderr": err}
    if mgr in ("dnf","yum"):
        rc, out, err = safe_shell(f"rpm -q {name} >/dev/null 2>&1 || sudo {mgr} install -y {name}")
        ok = (rc == 0)
        return True, ok, f"attempted {mgr} install", {"mgr": mgr, "stdout": out, "stderr": err}
    if mgr == "pacman":
        rc, out, err = safe_shell(f"pacman -Qi {name} >/dev/null 2>&1 || sudo pacman -S --noconfirm {name}")
        ok = (rc == 0)
        return True, ok, "attempted pacman install", {"mgr": mgr, "stdout": out, "stderr": err}
    return False, False, "No supported package manager detected", {"mgr": mgr}

def _service_running(name: str, enable: bool):
    g = grains()
    if not g.get("has_systemctl"):
        return False, False, "systemctl not found", {}
    changed = False
    if enable:
        rc1, out1, err1 = safe_shell(f"sudo systemctl enable {name} >/dev/null 2>&1 || true")
        changed = True
    rc2, out2, err2 = safe_shell(f"sudo systemctl start {name} >/dev/null 2>&1 || true")
    changed = True or changed
    rc3, out3, err3 = safe_shell(f"systemctl is-active {name} >/dev/null 2>&1")
    ok = (rc3 == 0)
    return changed, ok, "service ensured running", {"active": ok}
