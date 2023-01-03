#!/usr/bin/env python3

import collections
import functools
import itertools
import re
import sys
from typing import Iterable


rx = re.compile(r"([A-Z]{2})|(\d+)")

cave = {
    m[0][0]: (int(m[1][1]), {v for v, _ in m[2:]})
    for m in (rx.findall(line) for line in sys.stdin.readlines())
}


@functools.cache
def steps_between(start: str, end: str) -> int:
    q: collections.deque[tuple[str, int]] = collections.deque([(start, 0)])
    seen = set()
    while q:
        (here, steps) = q.popleft()
        for there in cave[here][1]:
            if there == end:
                return steps + 1

            if there not in seen:
                seen.add(there)
                q.append((there, steps + 1))
    else:
        raise Exception(f"No path from {start} to {end} found!")


useful_valves = {v for v, (f, _) in cave.items() if f > 0}


@functools.cache
def solve_for(time_limit, valves):
    valves = set(valves.split(","))
    q: list[tuple[int, int, set[str], str]] = [(0, 0, set(), "AA")]
    best = 0

    while q:
        time, score, open, here = q.pop()

        if score > best:
            best = score

        if time == time_limit:
            continue

        if valves <= open:
            continue

        for valve in valves - open:
            dt = steps_between(here, valve) + 1

            if time + dt > time_limit:
                continue

            q.append(
                (
                    time + dt,
                    score + (time_limit - time - dt) * cave[valve][0],
                    open | {valve},
                    valve,
                )
            )

    return best


def partition(valves: set[str]) -> Iterable[tuple[set[str], set[str]]]:
    for n in range(1, len(valves)):
        for subset in itertools.combinations(valves, n):
            yield set(subset), {v for v in valves if v not in subset}


def a():
    return solve_for(30, ",".join(useful_valves))


def b():
    best = 0
    for me, elephant in partition(useful_valves):
        me = ",".join(sorted(me))
        elephant = ",".join(sorted(elephant))

        mine = solve_for(26, me) if me else 0
        elephants = solve_for(26, elephant) if elephant else 0

        score = mine + elephants

        if score > best:
            best = score

    return best


print("a:", a())
print("b:", b())
