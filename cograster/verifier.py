from typing import Any

from cograster.metrics import cognitive_error_rate
from cograster.schemas import VerificationError, VerificationReport


def verify(task: dict[str, Any], workflow: dict[str, Any]) -> VerificationReport:
    """Verify semantic correctness of a raster-algebra workflow.

    This MVP checks workflow JSON against task JSON.
    It does not execute raster code.
    """
    errors: list[VerificationError] = []

    errors.extend(_check_expected_operations(task, workflow))
    errors.extend(_check_forbidden_operations(task, workflow))
    errors.extend(_check_required_checks(task, workflow))
    errors.extend(_check_index_semantics(task, workflow))

    possible_traps = _count_possible_traps(task)
    cer = cognitive_error_rate(errors, possible_traps)

    return VerificationReport(
        task_id=str(task.get("task_id", "unknown_task")),
        workflow_id=str(workflow.get("workflow_id", "unknown_workflow")),
        passed=len(errors) == 0,
        errors=errors,
        cognitive_error_rate=cer,
    )


def _operation_map(workflow: dict[str, Any]) -> dict[str, str]:
    ans: dict[str, str] = {}

    for item in workflow.get("operations", []):
        layer = item.get("layer")
        operation = item.get("operation")

        if isinstance(layer, str) and isinstance(operation, str):
            ans[layer] = operation

    return ans


def _check_expected_operations(
    task: dict[str, Any],
    workflow: dict[str, Any],
) -> list[VerificationError]:
    errors: list[VerificationError] = []
    actual_operations = _operation_map(workflow)

    for expected in task.get("expected_operations", []):
        layer = expected.get("layer")
        expected_operation = expected.get("operation")

        if not isinstance(layer, str) or not isinstance(expected_operation, str):
            continue

        actual_operation = actual_operations.get(layer)

        if actual_operation is None:
            errors.append(
                VerificationError(
                    error_type=_error_type_for_missing_or_wrong_operation(
                        layer=layer,
                        expected_operation=expected_operation,
                    ),
                    layer=layer,
                    message=f"Missing required operation for layer '{layer}': expected '{expected_operation}'.",
                    expected=expected_operation,
                    actual=None,
                )
            )
            continue

        if actual_operation != expected_operation:
            errors.append(
                VerificationError(
                    error_type=_error_type_for_missing_or_wrong_operation(
                        layer=layer,
                        expected_operation=expected_operation,
                    ),
                    layer=layer,
                    message=(
                        f"Wrong operation for layer '{layer}': "
                        f"expected '{expected_operation}', got '{actual_operation}'."
                    ),
                    expected=expected_operation,
                    actual=actual_operation,
                )
            )

    return errors


def _check_forbidden_operations(
    task: dict[str, Any],
    workflow: dict[str, Any],
) -> list[VerificationError]:
    errors: list[VerificationError] = []
    actual_operations = _operation_map(workflow)

    for forbidden in task.get("forbidden_operations", []):
        layer = forbidden.get("layer")
        forbidden_operation = forbidden.get("operation")

        if not isinstance(layer, str) or not isinstance(forbidden_operation, str):
            continue

        actual_operation = actual_operations.get(layer)

        if actual_operation == forbidden_operation:
            errors.append(
                VerificationError(
                    error_type=_error_type_for_forbidden_operation(layer, forbidden_operation),
                    layer=layer,
                    message=(
                        f"Forbidden operation for layer '{layer}': "
                        f"workflow uses '{forbidden_operation}'."
                    ),
                    expected=f"not {forbidden_operation}",
                    actual=actual_operation,
                )
            )

    return errors


def _check_required_checks(
    task: dict[str, Any],
    workflow: dict[str, Any],
) -> list[VerificationError]:
    errors: list[VerificationError] = []

    required_checks = set(task.get("required_checks", []))
    actual_checks = set(workflow.get("checks", []))
    missing_checks = sorted(required_checks - actual_checks)

    for check in missing_checks:
        errors.append(
            VerificationError(
                error_type=_error_type_for_missing_check(check),
                layer=None,
                message=f"Missing required check: '{check}'.",
                expected=check,
                actual=None,
            )
        )

    return errors


def _check_index_semantics(
    task: dict[str, Any],
    workflow: dict[str, Any],
) -> list[VerificationError]:
    """Check spectral-index formulas if task defines expected_formula."""
    errors: list[VerificationError] = []

    expected_formula = task.get("expected_formula")
    actual_formula = workflow.get("formula")

    if expected_formula is None:
        return errors

    if actual_formula != expected_formula:
        errors.append(
            VerificationError(
                error_type="E7_index_semantics_error",
                layer=None,
                message=(
                    "Wrong spectral index formula: "
                    f"expected '{expected_formula}', got '{actual_formula}'."
                ),
                expected=expected_formula,
                actual=actual_formula,
            )
        )

    return errors


def _count_possible_traps(task: dict[str, Any]) -> int:
    error_traps = task.get("error_traps", [])

    if isinstance(error_traps, list) and error_traps:
        return len(error_traps)

    # Fallback: count expected/forbidden/check requirements.
    return (
        len(task.get("expected_operations", []))
        + len(task.get("forbidden_operations", []))
        + len(task.get("required_checks", []))
        + (1 if task.get("expected_formula") is not None else 0)
    )


def _error_type_for_missing_or_wrong_operation(layer: str, expected_operation: str) -> str:
    if expected_operation == "inverse_normalize":
        return "E1_factor_direction_error"

    if expected_operation == "reclassify":
        return "E5_categorical_continuous_confusion"

    if expected_operation == "mask":
        return "E6_constraint_factor_confusion"

    if layer in {"red", "green", "blue", "nir", "swir"}:
        return "E7_index_semantics_error"

    return "E0_operation_semantics_error"


def _error_type_for_forbidden_operation(layer: str, operation: str) -> str:
    if operation == "min_max_normalize":
        return "E5_categorical_continuous_confusion"

    if operation == "weighted_sum" or layer in {"protected_areas", "cloud_mask"}:
        return "E6_constraint_factor_confusion"

    return "E0_forbidden_operation_error"


def _error_type_for_missing_check(check: str) -> str:
    if check in {"same_transform", "same_resolution", "same_extent"}:
        return "E2_grid_alignment_error"

    if check == "nodata_preserved":
        return "E4_nodata_semantic_error"

    if check in {"unit_consistency", "same_units"}:
        return "E3_unit_confusion"

    return "E0_missing_required_check"
