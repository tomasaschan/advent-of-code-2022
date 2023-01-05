#!/usr/bin/env python3

import sys


shapes: list[set[tuple[int, int]]] = [
    {(0, 0), (1, 0), (2, 0), (3, 0)},
    {(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)},
    {(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)},
    {(0, 0), (0, 1), (0, 2), (0, 3)},
    {(0, 0), (1, 0), (0, 1), (1, 1)},
]

jets = [c for c in sys.stdin.read().strip()]


def bottom(shape):
    return min(y for _, y in shape)


def top(shape):
    return max((y for _, y in shape), default=0)


def left(shape):
    return min(x for x, _ in shape)


def right(shape):
    return max(x for x, _ in shape)


def move(shape, x, y):
    return {(a + x, b + y) for a, b in shape}


def prune(cave: set[tuple[int, int]], keep: int):
    return {(x, y) for x, y in cave if y > top(cave) - keep}


def hash(cave: set[tuple[int, int]]) -> int:
    zero = bottom(cave)
    return sum((x + 7 * (y - zero) for x, y in cave), start=0)


def drop_rock(
    cave: set[tuple[int, int]],
    rock: set[tuple[int, int]],
    t: int,
    keep=50,
) -> tuple[int, set[tuple[int, int]]]:
    rock = move(rock, 2, top(cave) + 4)
    while True:
        if jets[t % len(jets)] == "<":
            if left(rock) > 0 and not cave.intersection(move(rock, -1, 0)):
                rock = move(rock, -1, 0)
        if jets[t % len(jets)] == ">":
            if right(rock) < 6 and not cave.intersection(move(rock, 1, 0)):
                rock = move(rock, 1, 0)

        t += 1

        if bottom(rock) > 1 and not cave.intersection(move(rock, 0, -1)):
            rock = move(rock, 0, -1)
        else:
            return t, rock | prune(cave, keep=keep)


def drop_rocks(
    cave: set[tuple[int, int]],
    s: tuple[int, int],
    n: int,
    keep=50,
) -> tuple[int, set[tuple[int, int]]]:
    t, r0 = s

    for r in range(n):
        t, cave = drop_rock(
            cave,
            shapes[(r0 + r) % len(shapes)],
            t,
            keep=keep,
        )

    return t, cave


def a():
    _, cave = drop_rocks(set(), (0, 0), 2022)
    return top(cave)


def b():
    def find_cycle(keep=50):
        t, cave = 0, set()
        seen = {}

        for n in range(20_000):
            t, cave = drop_rock(cave, shapes[n % len(shapes)], t, keep=keep)
            k = (t % len(jets), n % len(shapes), hash(cave))

            if k in seen.keys():
                return (
                    seen[k],
                    (n, top(cave)),
                )

            seen[k] = (n, top(cave))
        else:
            raise Exception(
                "Could not find a cycle within the first 10k rocks"
            )

    def drop_without_cycle(N, cycle, keep=50):
        (n0, h0), (n1, h1) = cycle
        t, cave = drop_rocks(set(), (0, 0), n1, keep=keep)

        nc, nr = divmod(N - n1, n1 - n0)
        H = nc * (h1 - h0)
        cave = {(x, y + H) for x, y in cave}

        t, cave = drop_rocks(cave, (t, n1), nr, keep=keep)

        return t, cave

    keep = 40
    cycle = find_cycle(keep=keep)
    _, cave = drop_without_cycle(1000000000000, cycle, keep=keep)

    return top(cave)


print("a:", a())
print("b:", b())
