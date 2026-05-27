from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class VerificationError:
    error_type: str
    layer: str | None
    message: str
    expected: Any | None = None
    actual: Any | None = None


@dataclass(frozen=True)
class VerificationReport:
    task_id: str
    workflow_id: str
    passed: bool
    errors: list[VerificationError]
    cognitive_error_rate: float
