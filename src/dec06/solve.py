#!/usr/bin/env python3

import sys

input = sys.stdin.read().strip()


def find_marker(problem, n):
    for i in range(n - 1, len(problem)):
        if len(set(problem[i - n : i])) == n:
            return i


print("a:", find_marker(input, 4))
print("b:", find_marker(input, 14))
