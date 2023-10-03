import collections
from typing import List


def intSum(n: int) -> int:
    return n * (n + 1) // 2


def findMaxInt(n: List[int], length: int) -> int:
    if length == 1:
        return n[0]
    return max(n[length - 1], findMaxInt(n, length - 1))


def findSameNames(names: List[str]) -> set:
    sameNames = set()
    for item in collections.Counter(names).most_common():
        if item[1] > 1:
            sameNames.add(item[0])
    return sameNames


def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def gcd(a: int, b: int) -> int:
    if b == 0:
        return a
    return gcd(b, a % b)


def fibonacci(n: int) -> int:
    if n == 1 or n == 2:
        return 1
    return fibonacci(n - 2) + fibonacci(n - 1)


def hanoi(n, src, dst, aux):
    if n == 1:
        print(f'{src} -> {dst}')
        return

    hanoi(n - 1, src, aux, dst)
    print(f'{src} -> {dst}')
    hanoi(n - 1, aux, dst, src)


def linearSearch(n: List[int], x: int) -> List[int]:
    arr = []
    for idx, item in enumerate(n):
        if item == x:
            arr.append(idx)
    return arr


def selSort(n: List[int]) -> List[int]:
    result = []
    while n:
        min_idx = n.index(min(n))
        value = n.pop(min_idx)
        result.append(value)
    return result


def findInsIdx(result: List[int], value: int) -> int:
    for i in range(0, len(result)):
        if value < result[i]:
            return i
    return len(result)


def insSort(n: List[int]) -> List[int]:
    result = []
    while n:
        value = n.pop(0)
        ins_idx = findInsIdx(result, value)
        result.insert(ins_idx, value)
    return result


print(intSum(100))

nums = [13, 45, 78, 65, 8, 73, 83, 23, 47, 3]
print(findMaxInt(nums, len(nums)))

names = ["Tom", "Jerry", "Mike", "Tom", "Mike"]
print(findSameNames(names))

print(factorial(10))
print(gcd(81, 27))
print(fibonacci(9))
hanoi(3, 1, 3, 2)

print(linearSearch(nums, 8))
print(insSort(nums))
