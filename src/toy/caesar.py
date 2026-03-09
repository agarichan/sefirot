def encrypt(text: str, shift: int) -> str:
    """シーザー暗号で暗号化する。

    英字（a-z, A-Z）のみシフトし、他の文字はそのまま。
    大文字は大文字のまま、小文字は小文字のまま。

    Args:
        text: 暗号化する文字列
        shift: シフト量（正: 右シフト、負: 左シフト）

    Returns:
        暗号化された文字列
    """
    result = []
    for ch in text:
        if ch.isascii() and ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            result.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            result.append(ch)
    return "".join(result)


def decrypt(text: str, shift: int) -> str:
    """シーザー暗号を復号する。

    encrypt(text, shift) の逆操作。

    Args:
        text: 復号する文字列
        shift: encrypt 時に使用したシフト量

    Returns:
        復号された文字列
    """
    return encrypt(text, -shift)
