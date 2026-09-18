from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .checks import ALL_CHECKS, CheckResult, Status
from .system import SystemContext

_COLOR = {
    Status.PASS: "\033[32m",  # green
    Status.WARN: "\033[33m",  # yellow
    Status.FAIL: "\033[31m",  # red
    Status.SKIP: "\033[90m",  # grey
}
_RESET = "\033[0m"
_LABEL = {
    Status.PASS: "PASS",
    Status.WARN: "WARN",
    Status.FAIL: "FAIL",
    Status.SKIP: "SKIP",
}


def run_all(ctx: SystemContext) -> list[CheckResult]:
    results = []
    for check in ALL_CHECKS:
        try:
            results.append(check(ctx))
        except Exception as exc:  # noqa: BLE001 - a broken check must never kill the run
            results.append(
                CheckResult(
                    name=getattr(check, "__name__", str(check)),
                    status=Status.SKIP,
                    message=f"check raised an unexpected error: {exc!r}",
                )
            )
    return results


def _print_text(results: list[CheckResult], use_color: bool) -> None:
    for r in results:
        color = _COLOR[r.status] if use_color else ""
        reset = _RESET if use_color else ""
        print(f"[{color}{_LABEL[r.status]}{reset}] {r.name}: {r.message}")
        if r.fix:
            print(f"       fix: {r.fix}")

    fails = sum(1 for r in results if r.status == Status.FAIL)
    warns = sum(1 for r in results if r.status == Status.WARN)
    print()
    print(f"{len(results)} checks run — {fails} failed, {warns} warned.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="rocm-doctor",
        description="Diagnostic CLI for AMD GPU (ROCm) local LLM serving setups.",
    )
    parser.add_argument("--json", action="store_true", help="output results as JSON")
    parser.add_argument(
        "--no-color", action="store_true", help="disable ANSI color in text output"
    )
    parser.add_argument(
        "--version", action="version", version=f"rocm-doctor {__version__}"
    )
    args = parser.parse_args(argv)

    ctx = SystemContext()
    results = run_all(ctx)

    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))
    else:
        _print_text(results, use_color=not args.no_color and sys.stdout.isatty())

    return 1 if any(r.status == Status.FAIL for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
