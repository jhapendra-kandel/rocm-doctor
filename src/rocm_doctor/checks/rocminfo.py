from __future__ import annotations

from ..system import SystemContext
from .base import CheckResult, Status

NAME = "rocminfo-gpu-agent"


def check_rocminfo(ctx: SystemContext) -> CheckResult:
    output = ctx.run(["rocminfo"])
    if output is None:
        return CheckResult(
            NAME,
            Status.SKIP,
            "'rocminfo' not found on PATH — ROCm userspace tools may not "
            "be installed.",
        )

    if "Device Type:" in output and "GPU" in output:
        return CheckResult(NAME, Status.PASS, "rocminfo reports at least one GPU agent.")

    return CheckResult(
        NAME,
        Status.WARN,
        "rocminfo ran but no GPU agent was found — the driver may not be "
        "bound. Check 'lspci -vvv' for the amdgpu kernel driver.",
    )
