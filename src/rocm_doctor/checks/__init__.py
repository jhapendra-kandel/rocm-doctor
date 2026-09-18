"""Check registry.

Each check is a small, independent function: (SystemContext) -> CheckResult.
A failing or erroring check never blocks the others from running — see
cli.py's run loop.
"""

from __future__ import annotations

from .base import Check, CheckResult, Status
from .blacklist import check_blacklist_leftover
from .display_core import check_display_core_failure
from .kernel import check_kernel_version
from .ollama_host import check_ollama_host_binding
from .ollama_processor import check_ollama_processor
from .ram_vram import check_ram_vram_headroom
from .rocminfo import check_rocminfo

ALL_CHECKS: list[Check] = [
    check_kernel_version,
    check_display_core_failure,
    check_blacklist_leftover,
    check_rocminfo,
    check_ollama_host_binding,
    check_ollama_processor,
    check_ram_vram_headroom,
]

__all__ = ["ALL_CHECKS", "Check", "CheckResult", "Status"]
