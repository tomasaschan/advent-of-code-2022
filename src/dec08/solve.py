#!/usr/bin/env python3

import itertools
import sys


input = sys.stdin.readlines()

forest = {
    (x, y): int(h)
    for y, line in enumerate(input)
    for x, h in enumerate(line.strip())
}
xhi, yhi = max(x for x, _ in forest.keys()), max(y for y, _ in forest.keys())


def show(forest: dict[tuple[int, int], int]):
    for y in range(yhi + 1):
        print("".join(str(forest[(x, y)]) for x in range(xhi + 1)))


def a():
    mapped = {}

    # map highest to the left of
    for y in range(yhi + 1):
        hi = -1
        for x in range(xhi + 1):
            h = forest.get((x - 1, y), -1)
            hi = max(h, hi)
            mapped[(x, y)] = {"l": hi}
    # map highest to the right of
    for y in range(yhi + 1):
        hi = -1
        for x in range(xhi, -1, -1):
            h = forest.get((x + 1, y), -1)
            hi = max(h, hi)
            mapped[(x, y)]["r"] = hi
    # map highest above
    for x in range(xhi + 1):
        hi = -1
        for y in range(yhi + 1):
            h = forest.get((x, y - 1), -1)
            hi = max(h, hi)
            mapped[(x, y)]["u"] = hi
    # map highest below
    for x in range(xhi + 1):
        hi = -1
        for y in range(yhi, -1, -1):
            h = forest.get((x, y + 1), -1)
            hi = max(h, hi)
            mapped[(x, y)]["d"] = hi

    return sum(
        1
        for p in forest.keys()
        if forest[p] > mapped[p]["l"]
        or forest[p] > mapped[p]["r"]
        or forest[p] > mapped[p]["u"]
        or forest[p] > mapped[p]["d"]
    )


def b():
    mapped = {}

    # looking left
    for y in range(yhi + 1):
        for x in range(xhi + 1):
            distance = 0
            for n in range(x - 1, -1, -1):
                distance += 1
                if forest[(n, y)] >= forest[(x, y)]:
                    break
            mapped[(x, y)] = {"l": distance}

    # looking right
    for y in range(yhi + 1):
        for x in range(xhi, -1, -1):
            distance = 0
            for n in range(x + 1, xhi + 1):
                distance += 1
                if forest[(n, y)] >= forest[(x, y)]:
                    break
            mapped[(x, y)]["r"] = distance

    # looking up
    for x in range(xhi + 1):
        for y in range(yhi + 1):
            distance = 0
            for n in range(y + 1, yhi + 1):
                distance += 1
                if forest[(x, n)] >= forest[(x, y)]:
                    break
            mapped[(x, y)]["u"] = distance

    # looking down
    for x, y in itertools.product(range(xhi + 1), range(yhi, -1, -1)):
        distance = 0
        for n in range(y - 1, -1, -1):
            distance += 1
            if forest[(x, n)] >= forest[(x, y)]:
                break
        mapped[(x, y)]["d"] = distance

    return max(v["l"] * v["r"] * v["u"] * v["d"] for v in mapped.values())


print("a:", a())
print("b:", b())
