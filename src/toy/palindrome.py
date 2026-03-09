def is_palindrome(s: str) -> bool:
    """文字列が回文かどうかを返す。

    大文字小文字を無視し、空白も無視して判定する。

    Args:
        s: 判定対象の文字列

    Returns:
        回文なら True、そうでなければ False
    """
    normalized = s.lower().replace(" ", "")
    return normalized == normalized[::-1]
