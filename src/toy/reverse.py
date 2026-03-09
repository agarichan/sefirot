def reverse_string(s: str) -> str:
    """文字列を反転する。

    Args:
        s: 対象の文字列

    Returns:
        反転した文字列
    """
    return s[::-1]


def reverse_words(s: str) -> str:
    """単語の順序を反転する。

    "hello world" → "world hello"
    単語は空白で区切られたものとする。

    Args:
        s: 対象の文字列

    Returns:
        単語順が反転した文字列
    """
    return " ".join(s.split()[::-1])
