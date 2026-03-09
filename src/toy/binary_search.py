def binary_search(arr: list[int], target: int) -> int:
    """ソート済みリストから target のインデックスを返す。

    見つからなければ -1 を返す。

    Args:
        arr: ソート済みの整数リスト
        target: 検索する値

    Returns:
        target のインデックス。見つからなければ -1。
    """
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1
