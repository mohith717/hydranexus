def detect_possible_leak(readings, threshold=1.0, consecutive=3):
    """Detect sustained high flow in a sequence of readings."""

    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        raise ValueError("Threshold must be numeric.")

    if threshold < 0:
        raise ValueError("Threshold cannot be negative.")

    if isinstance(consecutive, bool) or not isinstance(consecutive, int):
        raise ValueError("Consecutive count must be an integer.")

    if consecutive < 1:
        raise ValueError("Consecutive count must be at least 1.")

    count = 0

    for value in readings:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Every reading must be numeric.")

        if value < 0:
            raise ValueError("Readings cannot be negative.")

        if value > threshold:
            count += 1

            if count >= consecutive:
                return True
        else:
            count = 0

    return False