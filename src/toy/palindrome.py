def is_palindrome(s: str) -> bool:
    """文字列が回文かどうかを返す。

    大文字小文字を無視し、空白も無視して判定する。
    英数字以外の文字（句読点等）も無視する。

    Args:
        s: 判定対象の文字列

    Returns:
        回文なら True
    """
    normalized = [c.lower() for c in s if c.isalnum()]
    return normalized == normalized[::-1]
