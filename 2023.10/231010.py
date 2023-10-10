def palindrome(s: str) -> bool:
    qu = []
    stk = []

    for c in s:
        if c.isalpha():
            qu.append(c.lower())
            stk.append(c.lower())

    while qu and stk:
        if qu.pop(0) != stk.pop():
            return False
    return True


def printAllFriend(g: dict, n: str):
    qu = []
    done = set()

    qu.append(n)
    done.add(n)

    while qu:
        p = qu.pop(0)
        print(p)
        for x in g[p]:
            if x not in done:
                qu.append(x)
                done.add(x)


def solveMaze(g: dict, start: str, end: str) -> str:
    qu = []
    done = set()

    qu.append(start)
    done.add(start)

    while qu:
        p = qu.pop(0)
        v = p[-1]               # 큐에 저장된 이동 경로의 마지막 문자가 현재 처리해야 할 꼭짓점
        if v == end:            # 처리해야 할 꼭짓점이 도착점이면
            return p
        for x in g[v]:          # 대상 꼭짓점에 연결된 꼭짓점들 중에
            if x not in done:   # 아직 큐에 추가된 적 없는 꼭짓점을
                qu.append(p+x)  # 이동 경로에 새 꼭짓점으로 추가하여 큐에 저장
                done.add(x)
    return '?'


print(palindrome("Madam, I'm Adam."))

fr_info = {
    'Summer': ['John', 'Justin', 'Mike'],
    'John': ['Summer', 'Justin'],
    'Justin': ['John', 'Summer', 'Mike', 'May'],
    'Mike': ['Summer', 'Justin'],
    'May': ['Justin', 'Kim'],
    'Kim': ['May'],
    'Tom': ['Jerry'],
    'Jerry': ['Tom']
}

printAllFriend(fr_info, 'Summer')

maze = {
    'a': ['e'],
    'b': ['c', 'f'],
    'c': ['b', 'd'],
    'd': ['c'],
    'e': ['a', 'i'],
    'f': ['b', 'g', 'j'],
    'g': ['f', 'h'],
    'h': ['g', 'l'],
    'i': ['e', 'm'],
    'j': ['f', 'k', 'n'],
    'k': ['j', 'o'],
    'l': ['h', 'p'],
    'm': ['i', 'n'],
    'n': ['m', 'j'],
    'o': ['k'],
    'p': ['l']
}

print(solveMaze(maze, 'a', 'p'))