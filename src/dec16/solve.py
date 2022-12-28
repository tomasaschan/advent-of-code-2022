#!/usr/bin/env python3

import collections
import functools
import re
import sys

rx = re.compile(
    r"Valve (\w+) has flow rate=(\d+); tunnels? leads? to valves? ([\w, ]+)"
)

Cave = collections.namedtuple("Cave", ("rate", "tunnels"))
layout = {
    str(m.group(1)): Cave(int(m.group(2)), m.group(3).split(", "))
    for m in map(rx.match, sys.stdin.readlines())
}

all_valves = set(layout.keys())
useful_valves = set(k for k, (r, _) in layout.items() if r > 0 or k == "AA")


@functools.cache
def steps_between(start: str, end: str) -> int:
    q = collections.deque([(start, 0)])
    seen = set()
    while q:
        (here, steps) = q.popleft()
        for there in layout[here].tunnels:
            if there == end:
                return steps + 1

            if there not in seen:
                seen.add(there)
                q.append((there, steps + 1))


def a():
    State = collections.namedtuple(
        "state", ("time_left", "score", "at", "open")
    )
    initial_state = State(30, 0, "AA", set())

    def move(s: State, valve: str) -> State:
        return State(
            s.time_left - steps_between(s.at, valve),
            s.score,
            valve,
            s.open,
        )

    def open(s: State) -> State:
        return State(
            s.time_left - 1,
            s.score + (s.time_left - 1) * layout[s.at].rate,
            s.at,
            s.open | {s.at},
        )

    def search():
        q = collections.deque([(initial_state, ())])

        seen = set()
        best = (0, [])

        while q:
            s, path = q.popleft()

            if s.score > best[0]:
                best = (s.score, path)

            if s.time_left == 0:
                continue

            if s.at not in s.open and s.at in useful_valves:
                q.append((open(s), (*path, s.at)))

            for v in useful_valves:
                if v in s.open or v == s.at:
                    continue

                if s.time_left - steps_between(s.at, v) > 0:
                    p = (v, *path)
                    if p not in seen:
                        seen.add(p)
                        q.append((move(s, v), path))

        return best

    return search()[0]


print("a:", a())
