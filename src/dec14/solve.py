#!/usr/bin/env python3

import operator
import sys


underground = set()

for path in sys.stdin.readlines():
    coords = [tuple(map(int, p.split(","))) for p in path.split(" -> ")]

    for i in range(1, len(coords)):
        byx = sorted([coords[i - 1], coords[i]], key=operator.itemgetter(0))
        byy = sorted([coords[i - 1], coords[i]], key=operator.itemgetter(1))
        for x in range(byx[0][0], byx[1][0] + 1):
            for y in range(byy[0][1], byy[1][1] + 1):
                underground.add((x, y))

xlo, xhi, ylo, yhi = None, None, None, None
for (x, y) in underground:
    if xlo is None or x < xlo:
        xlo = x
    if xhi is None or x > xhi:
        xhi = x
    if ylo is None or y < ylo:
        ylo = y
    if yhi is None or y > yhi:
        yhi = y


def show(sand, floor=None):
    xlo, xhi, ylo, yhi = None, None, None, None
    for (x, y) in underground.union(sand):
        if xlo is None or x < xlo:
            xlo = x
        if xhi is None or x > xhi:
            xhi = x
        if ylo is None or y < ylo:
            ylo = y
        if yhi is None or y > yhi:
            yhi = y
    if floor:
        yhi = floor
    print(
        " " * len(str(yhi)),
        xlo // 100,
        " " * (500 - xlo - 3),
        5,
        " " * (xhi - 500 - 3),
        xhi // 100,
    )
    print(
        " " * len(str(yhi)),
        (xlo % 100) // 10,
        " " * (500 - xlo - 3),
        0,
        " " * (xhi - 500 - 3),
        (xhi % 100) // 10,
    )
    print(
        " " * len(str(yhi)),
        (xlo % 10),
        " " * (500 - xlo - 3),
        0,
        " " * (xhi - 500 - 3),
        xhi % 10,
    )
    print(
        "\n".join(
            f"{y:{len(str(yhi))}d} "
            + "".join(
                "+"
                if (x, y) == (500, 0)
                else "o"
                if (x, y) in sand
                else "#"
                if (x, y) in underground or (floor and y == floor)
                else "."
                for x in range(xlo, xhi + 1)
            )
            for y in range(min(ylo, 0), yhi + 1)
        )
    )


def produce_one(sand, floor=None):
    (x, y) = (500, 0)

    resting = underground.union(sand)

    def at_rest():
        return all(map(lambda d: (x + d, y + 1) in resting, (-1, 0, 1))) or (
            floor and y + 1 == floor
        )

    while not at_rest():
        if not floor and y >= yhi:
            return False

        if not (x, y + 1) in resting:
            y += 1
        elif not (x - 1, y + 1) in resting:
            x -= 1
            y += 1
        elif not (x + 1, y + 1) in resting:
            x += 1
            y += 1

    sand.add((x, y))
    return (x, y) != (500, 0)


def a():
    sand = set()
    while produce_one(sand):
        pass
    return len(sand)


def b():
    sand = set()
    while produce_one(sand, floor=yhi + 2):
        pass
    return len(sand)


print("a:", a())
print("b:", b())
