from cograster.schemas import VerificationError


def cognitive_error_rate(errors: list[VerificationError], possible_traps: int) -> float:
    """Compute Cognitive Error Rate.

    CER = number_of_detected_cognitive_spatial_errors / number_of_possible_traps

    If a task does not define possible traps, return 0.0 to avoid division by zero.
    """
    if possible_traps <= 0:
        return 0.0

    return len(errors) / possible_traps
