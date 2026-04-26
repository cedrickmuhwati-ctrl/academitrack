"""
algorithms.py  —  AcademiTrack
Sorting and searching algorithms for the group project.

Each sort function receives:
    data    – list of dicts
    key     – field name (string) to sort on
    reverse – True for descending order

Each search function receives:
    data        – list of dicts
    search_term – string to find (case-insensitive, checks all fields)
"""

import math

# ═══════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════
def _get(record, key):
    """Return a comparable value for sorting (lowercases strings)."""
    val = record.get(key, '')
    if isinstance(val, str):
        return val.lower()
    return val if val is not None else ''


def _matches(record, term):
    """Return True if term appears in ANY field of the record."""
    term = term.lower()
    return any(term in str(v).lower() for v in record.values())


# ═══════════════════════════════════════════════════════════════════
#  SORTING ALGORITHMS
# ═══════════════════════════════════════════════════════════════════

def bubble_sort(data, key='name', reverse=False):
    """O(n²) — repeatedly swaps adjacent out-of-order elements."""
    arr = data[:]
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            a, b = _get(arr[j], key), _get(arr[j + 1], key)
            if (a > b) if not reverse else (a < b):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def selection_sort(data, key='name', reverse=False):
    """O(n²) — finds the min/max and moves it to the front each pass."""
    arr = data[:]
    n = len(arr)
    for i in range(n):
        idx = i
        for j in range(i + 1, n):
            a, b = _get(arr[j], key), _get(arr[idx], key)
            if (a < b) if not reverse else (a > b):
                idx = j
        arr[i], arr[idx] = arr[idx], arr[i]
    return arr


def insertion_sort(data, key='name', reverse=False):
    """O(n²) — builds a sorted portion by inserting each element."""
    arr = data[:]
    for i in range(1, len(arr)):
        current = arr[i]
        j = i - 1
        while j >= 0 and (
            (_get(arr[j], key) > _get(current, key)) if not reverse
            else (_get(arr[j], key) < _get(current, key))
        ):
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = current
    return arr


def merge_sort(data, key='name', reverse=False):
    """O(n log n) — divides the array and merges sorted halves."""
    if len(data) <= 1:
        return data[:]
    mid   = len(data) // 2
    left  = merge_sort(data[:mid], key, reverse)
    right = merge_sort(data[mid:], key, reverse)
    return _merge(left, right, key, reverse)


def _merge(left, right, key, reverse):
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        a, b = _get(left[i], key), _get(right[j], key)
        if (a <= b) if not reverse else (a >= b):
            result.append(left[i]);  i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def quick_sort(data, key='name', reverse=False):
    """O(n log n) average — partitions around a pivot element."""
    arr = data[:]
    _quick(arr, 0, len(arr) - 1, key, reverse)
    return arr


def _quick(arr, low, high, key, reverse):
    if low < high:
        p = _partition(arr, low, high, key, reverse)
        _quick(arr, low, p - 1,  key, reverse)
        _quick(arr, p + 1, high, key, reverse)


def _partition(arr, low, high, key, reverse):
    pivot = _get(arr[high], key)
    i = low - 1
    for j in range(low, high):
        a = _get(arr[j], key)
        if (a <= pivot) if not reverse else (a >= pivot):
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


# ═══════════════════════════════════════════════════════════════════
#  SEARCHING ALGORITHMS
# ═══════════════════════════════════════════════════════════════════

def linear_search(data, search_term):
    """O(n) — checks every record for the search term in all fields."""
    return [r for r in data if _matches(r, search_term)]


def binary_search(data, search_term):
    """
    O(log n) — requires sorted data; searches the 'name' field first,
    then falls back to all fields for non-name matches.
    """
    term        = search_term.lower()
    sorted_data = sorted(data, key=lambda x: _get(x, 'name'))
    results     = []
    lo, hi      = 0, len(sorted_data) - 1

    while lo <= hi:
        mid = (lo + hi) // 2
        val = _get(sorted_data[mid], 'name')
        if term in val:
            results.append(sorted_data[mid])
            left = mid - 1
            while left >= 0 and term in _get(sorted_data[left], 'name'):
                results.append(sorted_data[left]); left -= 1
            right = mid + 1
            while right < len(sorted_data) and term in _get(sorted_data[right], 'name'):
                results.append(sorted_data[right]); right += 1
            break
        elif val < term:
            lo = mid + 1
        else:
            hi = mid - 1

    # Also catch matches in other fields not found above
    extra = [r for r in data if _matches(r, search_term) and r not in results]
    return results + extra


def jump_search(data, search_term):
    """
    O(√n) — jumps ahead by √n steps then does a linear scan backward.
    Sorted by 'name'; also checks all other fields.
    """
    term        = search_term.lower()
    sorted_data = sorted(data, key=lambda x: _get(x, 'name'))
    n           = len(sorted_data)
    step        = int(math.sqrt(n)) if n > 0 else 1
    results     = []

    prev = 0
    while prev < n and _get(sorted_data[min(step, n) - 1], 'name') < term:
        prev  = step
        step += int(math.sqrt(n))
        if prev >= n:
            break

    for i in range(prev, min(step, n)):
        if term in _get(sorted_data[i], 'name'):
            results.append(sorted_data[i])

    extra = [r for r in data if _matches(r, search_term) and r not in results]
    return results + extra
