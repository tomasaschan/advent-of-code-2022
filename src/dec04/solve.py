#!/usr/bin/env python3

import sys


def section(s):
    lo, hi = s.split("-", 1)
    return set(range(int(lo), int(hi) + 1))


def assignment(line):
    a, b = line.strip().split(",", 1)
    return section(a), section(b)


assignments: list[tuple[set, set]] = [
    assignment(line) for line in sys.stdin.readlines()
]

print("a:", sum(1 for a, b in assignments if a <= b or b <= a))
print("b:", sum(1 for a, b in assignments if a.intersection(b)))
