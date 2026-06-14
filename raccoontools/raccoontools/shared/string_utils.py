def linefy(text: str) -> str:
    """
    Collapses a multi-line string into a single line.

    Removes all linebreaks, merges multiple sequential whitespace characters
    (spaces, tabs, newlines, etc.) into a single space, and trims leading and
    trailing whitespace.

    :param text: The text to collapse into a single line.
    :return: The text with all whitespace runs collapsed into single spaces and
    the ends trimmed. Returns an empty string if the input contains only
    whitespace.

    Example:
        >>> linefy("  Hello\\n\\tworld  \\n  again  ")
        'Hello world again'
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected a str, got {type(text).__name__}.")

    return " ".join(text.split())
