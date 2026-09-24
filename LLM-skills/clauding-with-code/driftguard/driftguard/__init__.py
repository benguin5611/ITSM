"""driftguard: reference-integrity and drift checks for a markdown doc set.

Every check is a function ``(Context) -> list[Finding]``. The CLI prints one line per finding
(``path:line: CHECK-ID: message``) and exits 0 when clean, 1 on findings, 2 on misconfiguration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__version__ = "0.1.0"


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    check: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.check}: {self.message}"


@dataclass
class Context:
    """What every check receives: the loaded config, the scanned doc set, and (when the run is
    diff-scoped) the git diff. ``skipped`` collects checks that could not run (an unreachable
    external tool) so a non-result is reported as such, never as a pass."""

    cfg: Any
    docs: Any
    diff: Any = None
    skipped: list[str] = field(default_factory=list)
