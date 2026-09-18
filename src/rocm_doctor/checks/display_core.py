from __future__ import annotations

from ..system import SystemContext
from .base import CheckResult, Status

NAME = "display-core-init-failure"

FAILURE_SIGNATURE = "Fatal error during GPU init"


def check_display_core_failure(ctx: SystemContext) -> CheckResult:
    """Headless (no-monitor) boxes can hit a distinct amdgpu failure class:
    Display Core init fails while VRAM/compute init succeeds right up to
    it, producing this exact error even though the GPU is otherwise fine.
    """
    output = ctx.run(["dmesg"])
    if output is None:
        return CheckResult(
            NAME,
            Status.SKIP,
            "could not read dmesg (needs root, or not running on Linux).",
        )

    if FAILURE_SIGNATURE in output and "amdgpu" in output:
        return CheckResult(
            NAME,
            Status.FAIL,
            "dmesg shows a Display Core GPU init failure. On a headless "
            "(no-monitor) box, amdgpu's Display Core init can fail even "
            "though VRAM/compute init succeeds.",
            fix=(
                "echo 'options amdgpu dc=0' | sudo tee "
                "/etc/modprobe.d/amdgpu-options.conf && "
                "sudo update-initramfs -u && sudo reboot"
            ),
        )

    return CheckResult(NAME, Status.PASS, "no Display Core init failure found in dmesg.")
