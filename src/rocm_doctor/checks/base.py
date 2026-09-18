from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from ..system import SystemContext


class Status(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    SKIP = "skip"


@dataclass
class CheckResult:
    name: str
    status: Status
    message: str
    fix: str | None = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "fix": self.fix,
        }


Check = Callable[[SystemContext], CheckResult]
