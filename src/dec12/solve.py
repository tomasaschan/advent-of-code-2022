#!/usr/bin/env python3

import heapq
import sys


def parse():
    heightmap = {}
    S, E = None, None
    for y, line in enumerate(sys.stdin.readlines()):
        for x, e in enumerate(line.strip()):
            if e == "S":
                S = (x, y)
            if e == "E":
                E = (x, y)
            heightmap[x, y] = e.replace("S", "a").replace("E", "z")

    return heightmap, S, E


heightmap, S, E = parse()


def distance(a, b):
    return abs(b[0] - a[0]) + abs(b[1] - a[1])


def elevation(e):
    return ord("z") - ord(heightmap[e])


def solve_from(S):
    q: list[tuple[int, int, int, tuple[tuple[int, int]]]] = []
    seen = set([S])

    heapq.heappush(q, (0, distance(S, E), elevation(S), S))

    while q:
        steps, _, h, (x, y) = heapq.heappop(q)

        if (x, y) == E:
            return steps

        for p in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if p not in heightmap:
                continue
            if h - elevation(p) > 1:
                continue
            if p in seen:
                continue

            seen.add(p)
            heapq.heappush(
                q,
                (
                    steps + 1,
                    distance(p, E),
                    elevation(p),
                    p,
                ),
            )


def b():
    return min(
        filter(
            None,
            map(solve_from, (p for p, e in heightmap.items() if e == "a")),
        )
    )


print("a:", solve_from(S))
print("b:", b())
