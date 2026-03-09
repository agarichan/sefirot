def reverse_string(s: str) -> str:
    """文字列を反転する。

    Args:
        s: 反転する文字列

    Returns:
        反転された文字列
    """
    return s[::-1]


def reverse_words(s: str) -> str:
    """単語の順序を反転する。

    単語は空白で区切られる。連続する空白は単一の空白として扱う。

    例: "hello world" → "world hello"

    Args:
        s: 反転する文字列

    Returns:
        単語順序が反転された文字列
    """
    return " ".join(s.split()[::-1])
