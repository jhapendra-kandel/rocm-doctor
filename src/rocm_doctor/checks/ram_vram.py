from __future__ import annotations

import re

from ..system import SystemContext
from .base import CheckResult, Status

NAME = "ram-vram-headroom"


def _parse_meminfo_total_kb(meminfo: str) -> int | None:
    match = re.search(r"^MemTotal:\s+(\d+)\s+kB", meminfo, re.MULTILINE)
    return int(match.group(1)) if match else None


def _parse_vram_total_mb(rocm_smi_output: str) -> float | None:
    # rocm-smi --showmeminfo vram output includes a line like:
    #   GPU[0]  : VRAM Total Memory (B): 34342961152
    match = re.search(r"VRAM Total Memory \(B\):\s*(\d+)", rocm_smi_output)
    if not match:
        return None
    return int(match.group(1)) / (1024 * 1024)


def check_ram_vram_headroom(ctx: SystemContext) -> CheckResult:
    """On RAM-constrained boxes, Ollama (and similar loaders) disable
    lightweight mmap-based loading and make a full private RAM copy of a
    model before pushing it to VRAM when host headroom is tight relative
    to model size. That's a one-time cost per (re)load, not a sign of a
    broken setup — but if you don't know it's happening, it looks like an
    unexplained hang or swap thrash.
    """
    meminfo = ctx.read_file("/proc/meminfo")
    vram_output = ctx.run(["rocm-smi", "--showmeminfo", "vram"])

    if meminfo is None or vram_output is None:
        return CheckResult(
            NAME,
            Status.SKIP,
            "could not read /proc/meminfo and/or run 'rocm-smi' — skipping "
            "RAM/VRAM comparison.",
        )

    ram_kb = _parse_meminfo_total_kb(meminfo)
    vram_mb = _parse_vram_total_mb(vram_output)
    if ram_kb is None or vram_mb is None:
        return CheckResult(
            NAME, Status.SKIP, "could not parse RAM/VRAM totals — skipping comparison."
        )

    ram_gb = ram_kb / (1024 * 1024)
    vram_gb = vram_mb / 1024

    if ram_gb < vram_gb:
        return CheckResult(
            NAME,
            Status.WARN,
            f"system RAM ({ram_gb:.1f}GB) is smaller than GPU VRAM "
            f"({vram_gb:.1f}GB). Loading a model sized close to your VRAM "
            "may cause a slow/thrashy first load while it's copied through "
            "RAM — this is expected on this hardware ratio, not a bug.",
        )

    return CheckResult(
        NAME,
        Status.PASS,
        f"system RAM ({ram_gb:.1f}GB) comfortably exceeds GPU VRAM "
        f"({vram_gb:.1f}GB) — unlikely to hit RAM-copy thrash during model load.",
    )
