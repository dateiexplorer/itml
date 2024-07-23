def get_leading_space(line: str) -> int:
    """Get leading whitespace of a string."""

    return len(line[: len(line) - len(line.lstrip())])
