from __future__ import annotations

from ..system import SystemContext
from .base import CheckResult, Status

NAME = "ollama-host-binding"

OVERRIDE_PATH = "/etc/systemd/system/ollama.service.d/override.conf"


def check_ollama_host_binding(ctx: SystemContext) -> CheckResult:
    """Ollama defaults to binding 127.0.0.1, which is invisible from
    inside a Docker container with no error message — it just looks like
    Ollama isn't running.
    """
    content = ctx.read_file(OVERRIDE_PATH)
    if content is None:
        return CheckResult(
            NAME,
            Status.SKIP,
            f"no systemd override at {OVERRIDE_PATH} — Ollama is using its "
            "default bind (127.0.0.1). Fine unless you need to reach it "
            "from Docker or another host.",
        )

    if "OLLAMA_HOST=0.0.0.0" in content:
        return CheckResult(
            NAME, Status.PASS, "Ollama is bound to 0.0.0.0 — reachable from Docker/other hosts."
        )

    return CheckResult(
        NAME,
        Status.WARN,
        f"{OVERRIDE_PATH} exists but doesn't set OLLAMA_HOST=0.0.0.0 — "
        "Ollama defaults to 127.0.0.1, which is invisible from inside "
        "Docker containers.",
        fix=(
            'echo -e "[Service]\\nEnvironment=\\"OLLAMA_HOST=0.0.0.0:11434\\"" | '
            f"sudo tee {OVERRIDE_PATH} && "
            "sudo systemctl daemon-reload && sudo systemctl restart ollama"
        ),
    )
