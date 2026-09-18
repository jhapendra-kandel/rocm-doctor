from __future__ import annotations

from ..system import SystemContext
from .base import CheckResult, Status

NAME = "ollama-processor-fallback"


def check_ollama_processor(ctx: SystemContext) -> CheckResult:
    """The unambiguous tell that a model silently fell back to CPU
    inference (looks like a hang/perf-bug otherwise) is 'ollama ps''s
    PROCESSOR column showing 100% CPU instead of 100% GPU.
    """
    output = ctx.run(["ollama", "ps"])
    if output is None:
        return CheckResult(
            NAME, Status.SKIP, "'ollama' not found on PATH, or the service isn't running."
        )

    stripped = output.strip()
    if not stripped or stripped.splitlines() == []:
        return CheckResult(NAME, Status.PASS, "no models currently loaded — nothing to check.")

    if "100% CPU" in output:
        return CheckResult(
            NAME,
            Status.WARN,
            "at least one loaded model is running 100% CPU instead of GPU "
            "— likely a driver regression, not a performance bug. Check "
            "'dmesg | grep amdgpu' and this tool's other checks.",
        )

    lines = [line for line in stripped.splitlines() if line.strip()]
    if len(lines) <= 1:
        return CheckResult(NAME, Status.PASS, "no models currently loaded — nothing to check.")

    return CheckResult(NAME, Status.PASS, "all loaded models are running on GPU.")
