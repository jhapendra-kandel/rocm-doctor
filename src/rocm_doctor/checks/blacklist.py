from __future__ import annotations

from ..system import SystemContext
from .base import CheckResult, Status

NAME = "blacklist-amdgpu-leftover"

ACTIVE_PATH = "/etc/modprobe.d/blacklist-amdgpu.conf"
DISABLED_PATH = "/etc/modprobe.d/blacklist-amdgpu.conf.disabled"


def _has_active_blacklist_line(content: str) -> bool:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "blacklist" in stripped and "amdgpu" in stripped:
            return True
    return False


def check_blacklist_leftover(ctx: SystemContext) -> CheckResult:
    """A failed/abandoned amdgpu-dkms install can leave a blacklist file
    behind that silently keeps the in-tree amdgpu driver from loading on
    every subsequent boot — a very confusing thing to hit later since
    nothing about it is obviously connected to the original install
    attempt.
    """
    active = ctx.read_file(ACTIVE_PATH)
    if active is not None and _has_active_blacklist_line(active):
        return CheckResult(
            NAME,
            Status.FAIL,
            f"{ACTIVE_PATH} exists and actively blacklists amdgpu — "
            "likely a leftover from an abandoned amdgpu-dkms install/purge.",
            fix=(
                f"sudo mv {ACTIVE_PATH} {DISABLED_PATH} && "
                "sudo update-initramfs -u && sudo reboot"
            ),
        )

    if ctx.file_exists(DISABLED_PATH):
        return CheckResult(
            NAME,
            Status.PASS,
            f"found {DISABLED_PATH} — already disabled, no action needed.",
        )

    return CheckResult(NAME, Status.PASS, "no amdgpu blacklist file found.")
