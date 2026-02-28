DEFAULT_THRESHOLD: int = 10


def is_value_in_positive_range(value: int) -> bool:
    """Checks if a given value is strictly positive and less than 100.

    Args:
        value: The integer value to check.

    Returns:
        True if the value is greater than 0 and less than 100, False otherwise.
    """
    return 0 < value < 100