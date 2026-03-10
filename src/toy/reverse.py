def reverse_string(s: str) -> str:
    """文字列を反転する。

    Args:
        s: 入力文字列

    Returns:
        反転した文字列
    """
    return s[::-1]


def reverse_words(s: str) -> str:
    """単語の順序を反転する。

    単語は空白で区切られる。"hello world" → "world hello"

    Args:
        s: 入力文字列

    Returns:
        単語順を反転した文字列
    """
    return " ".join(s.split()[::-1])
