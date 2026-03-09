def binary_search(arr: list[int], target: int) -> int:
    """ソート済みリストから target を二分探索する。

    Args:
        arr: 昇順にソートされた整数リスト
        target: 探索対象の値

    Returns:
        見つかった場合はそのインデックス、見つからない場合は -1
    """
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1
