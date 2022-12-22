#!/usr/bin/env python3

import functools
import sys


def pair(lines):
    for line in lines.strip().split("\n"):
        yield eval(line.strip())


pairs = list(map(list, map(pair, sys.stdin.read().split("\n\n"))))


def lt(a, b):
    match a, b:
        case [], []:
            return 0
        case [], [_, *_]:
            return -1
        case [_, *_], []:
            return 1
        case [x, *xs], [y, *ys]:
            return lt(x, y) or lt(xs, ys)
        case x, [*ys]:
            return lt([x], ys)
        case [*xs], y:
            return lt(xs, [y])
        case x, y:
            if x < y:
                return -1
            if x > y:
                return 1
            if x == y:
                return 0
        case _:
            raise Exception(f"unhandled: comparing {a} to {b}")


def a():
    return sum(i + 1 for i, (a, b) in enumerate(pairs) if lt(a, b) == -1)


def b():
    a, b = [[2]], [[6]]
    packets = sorted(
        [*(item for p in pairs for item in p), a, b],
        key=functools.cmp_to_key(lt),
    )

    return (1 + packets.index(a)) * (1 + packets.index(b))


print("a:", a())
print("b:", b())
