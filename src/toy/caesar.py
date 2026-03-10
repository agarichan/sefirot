def encrypt(text: str, shift: int) -> str:
    """シーザー暗号で暗号化する。

    英字のみシフトし、他の文字（数字、記号、空白等）はそのまま保持する。
    大文字は大文字のまま、小文字は小文字のままシフトする。

    Args:
        text: 平文
        shift: シフト量（正の値で右シフト）

    Returns:
        暗号文
    """
    shift = shift % 26
    result: list[str] = []
    for ch in text:
        if ch.islower():
            result.append(chr((ord(ch) - ord("a") + shift) % 26 + ord("a")))
        elif ch.isupper():
            result.append(chr((ord(ch) - ord("A") + shift) % 26 + ord("A")))
        else:
            result.append(ch)
    return "".join(result)


def decrypt(text: str, shift: int) -> str:
    """シーザー暗号を復号する。

    encrypt の逆操作。encrypt(text, shift) を decrypt(result, shift) で元に戻せる。

    Args:
        text: 暗号文
        shift: 暗号化時に使ったシフト量

    Returns:
        平文
    """
    return encrypt(text, -shift)
