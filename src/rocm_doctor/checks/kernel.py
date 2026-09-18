from __future__ import annotations

import re

from ..system import SystemContext
from .base import CheckResult, Status

NAME = "kernel-version"


def check_kernel_version(ctx: SystemContext) -> CheckResult:
    """Heuristic: on Ubuntu 24.04, GA kernel is the 6.8.x line; HWE point
    releases go higher (6.11, 6.14, ...). Very new GPU generations (e.g.
    RDNA4-class cards) can fail amdgpu probe entirely on the GA kernel.
    This is a heuristic, not a hard GPU-generation lookup table — v0.1
    flags the pattern and lets the user judge based on their card's age.
    """
    output = ctx.run(["uname", "-r"])
    if output is None:
        return CheckResult(NAME, Status.SKIP, "could not run 'uname -r'.")

    version = output.strip()
    match = re.match(r"(\d+)\.(\d+)", version)
    if not match:
        return CheckResult(
            NAME, Status.SKIP, f"could not parse kernel version from '{version}'."
        )

    major, minor = int(match.group(1)), int(match.group(2))

    if major == 6 and minor <= 8:
        return CheckResult(
            NAME,
            Status.WARN,
            f"running kernel {version} — looks like an Ubuntu 24.04-era GA "
            "kernel (6.8.x). If your GPU is a very recent generation "
            "(e.g. RDNA4-class or newer), amdgpu may fail to probe on "
            "this kernel.",
            fix="sudo apt install linux-generic-hwe-24.04 && sudo reboot",
        )

    return CheckResult(
        NAME,
        Status.PASS,
        f"running kernel {version} — looks like a newer/HWE-class kernel.",
    )
