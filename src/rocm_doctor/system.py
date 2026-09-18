"""System-access layer.

Every check talks to the host only through a SystemContext instance rather
than calling subprocess/open() directly. That keeps every check testable
with a fake context and fixture text, with no real GPU, root access, or
Linux host required to run the test suite.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field


@dataclass
class SystemContext:
    """Real system access: runs actual commands, reads actual files."""

    def run(self, argv: list[str]) -> str | None:
        """Run a command, return combined stdout+stderr, or None if the
        binary doesn't exist / the command fails to execute at all."""
        try:
            proc = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None
        return proc.stdout + proc.stderr

    def read_file(self, path: str) -> str | None:
        try:
            with open(path, "r") as f:
                return f.read()
        except OSError:
            return None

    def file_exists(self, path: str) -> bool:
        import os

        return os.path.exists(path)


@dataclass
class FakeSystemContext:
    """Test double: pre-loaded command outputs and file contents.

    Usage:
        ctx = FakeSystemContext(
            commands={("uname", "-r"): "6.14.0-generic"},
            files={"/etc/modprobe.d/blacklist-amdgpu.conf": None},
        )
    """

    commands: dict[tuple[str, ...], str | None] = field(default_factory=dict)
    files: dict[str, str | None] = field(default_factory=dict)

    def run(self, argv: list[str]) -> str | None:
        return self.commands.get(tuple(argv))

    def read_file(self, path: str) -> str | None:
        return self.files.get(path)

    def file_exists(self, path: str) -> bool:
        return self.files.get(path) is not None
