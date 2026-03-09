def encrypt(text: str, shift: int) -> str:
    """シーザー暗号で暗号化する。

    英字のみシフトし、他の文字（数字、記号、空白等）はそのまま残す。
    大文字・小文字は保持する。

    Args:
        text: 平文
        shift: シフト量（正の値で右シフト）

    Returns:
        暗号文
    """
    result: list[str] = []
    for ch in text:
        if ch.isascii() and ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            result.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            result.append(ch)
    return "".join(result)


def decrypt(text: str, shift: int) -> str:
    """シーザー暗号を復号する。

    encrypt の逆操作。decrypt(encrypt(text, n), n) == text が成立する。

    Args:
        text: 暗号文
        shift: シフト量

    Returns:
        平文
    """
    return encrypt(text, -shift)
