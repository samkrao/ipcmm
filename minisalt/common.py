import os, json, time, uuid, subprocess, platform, socket, shlex
from dataclasses import dataclass
from typing import Any, Dict, Tuple, Optional, List

def now_ms() -> int:
    return int(time.time() * 1000)

def new_job_id() -> str:
    return uuid.uuid4().hex

def safe_shell(cmd: str) -> Tuple[int, str, str]:
    # Execute via /bin/sh -lc to support pipelines; keep minimal.
    p = subprocess.Popen(["/bin/sh", "-lc", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out, err

def grains() -> Dict[str, Any]:
    return {
        "id": socket.gethostname(),
        "hostname": socket.gethostname(),
        "fqdn": socket.getfqdn(),
        "platform": platform.system(),
        "platform_release": platform.release(),
        "arch": platform.machine(),
        "python": platform.python_version(),
        "time": int(time.time()),
        "os_release": _read_os_release(),
        "has_systemctl": os.path.exists("/bin/systemctl") or os.path.exists("/usr/bin/systemctl"),
        "pkg_mgr": _detect_pkg_mgr(),
    }

def _read_os_release() -> Dict[str, str]:
    path = "/etc/os-release"
    d: Dict[str, str] = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line=line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k,v=line.split("=",1)
                d[k]=v.strip().strip('"')
    except Exception:
        pass
    return d

def _detect_pkg_mgr() -> str:
    for name in ("apt-get", "dnf", "yum", "pacman", "zypper"):
        if shutil_which(name):
            return name
    return "unknown"

def shutil_which(cmd: str) -> Optional[str]:
    # tiny which
    for p in os.environ.get("PATH","").split(os.pathsep):
        candidate = os.path.join(p, cmd)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None

@dataclass
class StepResult:
    ok: bool
    changed: bool
    name: str
    comment: str
    data: Dict[str, Any]

def summarize(results: List[StepResult]) -> Dict[str, Any]:
    return {
        "ok": all(r.ok for r in results),
        "changed": any(r.changed for r in results),
        "steps": [
            {"name": r.name, "ok": r.ok, "changed": r.changed, "comment": r.comment, "data": r.data}
            for r in results
        ],
    }
