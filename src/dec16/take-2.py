#!/usr/bin/env python3

import collections
import dataclasses
import functools
import heapq
import re
import sys
import timeit

from typing import Iterable, Union


@dataclasses.dataclass(frozen=True)
class Cave:
    layout: dict[str, tuple[int, list[str]]]
    valves: set[str]
    useful_valves: set[str]
    useless_valves: set[str]

    @classmethod
    def parse(cls, input: str):
        rx: re.Pattern[str] = re.compile(
            r"Valve (\w+) has flow rate=(\d+); tunnels? leads? to valves? ([\w, ]+)"  # noqa: E501
        )

        layout: dict[str, tuple[int, list[str]]] = {}
        for line in input.splitlines():
            m = rx.match(line)
            if not m:
                print("failed to parse line:", line)
                continue
            layout[m.group(1)] = (int(m.group(2)), m.group(3).split(", "))

        return Cave(
            layout,
            {*layout.keys()},
            {v for v, (r, _) in layout.items() if r > 0},
            {v for v, (r, _) in layout.items() if r == 0},
        )

    def rate(self, valve: str) -> int:
        return self.layout[valve][0]

    def neighbors(self, valve: str) -> list[str]:
        return self.layout[valve][1]


cave = Cave.parse(sys.stdin.read())


@functools.cache
def steps_between(start: str, end: str) -> int:
    q: collections.deque[tuple[str, int]] = collections.deque([(start, 0)])
    seen = set()
    while q:
        (here, steps) = q.popleft()
        for there in cave.neighbors(here):
            if there == end:
                return steps + 1

            if there not in seen:
                seen.add(there)
                q.append((there, steps + 1))
    else:
        raise Exception(f"No path from {start} to {end} found!")


@dataclasses.dataclass
class At:
    valve: str

    def step_to(self, _: int) -> Union["At", "Moving"]:
        return At(self.valve)

    def is_movable(self, open: set[str]) -> bool:
        return self.valve in open | cave.useless_valves

    def is_openable(self, open: set[str]) -> bool:
        return self.valve in cave.useful_valves - open

    def __str__(self):
        return f"{self.valve}"


@dataclasses.dataclass
class Moving:
    to: str
    arriving: int

    def step_to(self, time: int) -> Union[At, "Moving"]:
        assert time <= self.arriving, "stepping too far!"
        return (
            At(self.to)
            if time == self.arriving
            else Moving(self.to, self.arriving)
        )

    def is_movable(self, _: set[str]) -> bool:
        return False

    def is_openable(self, _: set[str]) -> bool:
        return False

    def __str__(self) -> str:
        return f"{self.to}/{self.arriving}"


@dataclasses.dataclass
class Actors:
    actors: collections.OrderedDict[str, Union[At, Moving]]

    def __str__(self) -> str:
        return f'[{" ; ".join(f"{k} @ {a}" for k, a in self.actors.items())}]'

    def covered_valves(self, open: set[str]) -> set[str]:
        return open | {
            a.to if isinstance(a, Moving) else a.valve
            for a in self.actors.values()
        }

    def openable(self, open: set[str]) -> dict[str, At]:
        return {
            k: a
            for k, a in self.actors.items()
            if isinstance(a, At) and a.is_openable(open)
        }

    def no_more_moves(self, open: set[str]) -> bool:
        return cave.useful_valves <= self.covered_valves(open)

    def can_open(self, open: set[str]) -> bool:
        return any(a.is_openable(open) for a in self.actors.values())

    def can_move(self, open: set[str]) -> bool:
        return any(
            a.is_movable(open) for a in self.actors.values()
        ) and not self.no_more_moves(open)

    def can_advance_time(self, open: set[str]) -> bool:
        return any(
            isinstance(a, Moving) for a in self.actors.values()
        ) or self.no_more_moves(open)

    def advance_time(self, to: int) -> "Actors":
        return Actors(
            collections.OrderedDict(
                {k: a.step_to(to) for k, a in self.actors.items()}
            )
        )


@dataclasses.dataclass
class State:
    time: int
    limit: int
    open: set[str]
    actors: Actors
    path: list[tuple[int, str, str]]

    def score(self):
        return sum((self.limit - t) * cave.rate(v) for (t, _, v) in self.path)

    def evolve(self) -> Iterable["State"]:
        if self.time == self.limit:
            return

        if self.actors.can_move(self.open):
            for n in self.move_one():
                yield from n.evolve()
        elif self.actors.can_open(self.open):
            yield self.open_all()
        elif self.actors.can_advance_time(self.open):
            yield from self.advance_time().evolve()

    def __str__(self):
        return " ".join(
            (
                f"t={self.time:2d}",
                f"s={self.score():4d}",
                f"a={self.actors}",
                f"o={{{','.join(sorted(self.open))}}}",
                f"p=[{','.join(map(str, self.path))}]",
            )
        )

    def advance_time(self) -> "State":
        time = min(
            (
                a.arriving
                for a in self.actors.actors.values()
                if isinstance(a, Moving)
            ),
            default=self.limit,
        )
        return State(
            time,
            self.limit,
            self.open,
            self.actors.advance_time(to=time),
            self.path,
        )

    def move_one(self) -> Iterable["State"]:
        mover, at = next(
            (k, a.valve)
            for k, a in self.actors.actors.items()
            if isinstance(a, At) and a.is_movable(self.open)
        )

        for nxt in sorted(cave.useful_valves, reverse=True):
            if nxt in self.actors.covered_valves(self.open):
                continue

            if steps_between(at, nxt) > (self.limit - self.time):
                continue

            actors = self.actors.actors.copy()
            actors[mover] = Moving(nxt, self.time + steps_between(at, nxt))
            yield State(
                self.time,
                self.limit,
                self.open,
                Actors(actors),
                self.path,
            )

    def open_all(self) -> "State":
        return State(
            self.time + 1,
            self.limit,
            self.open
            | {a.valve for a in self.actors.openable(self.open).values()},
            self.actors.advance_time(self.time + 1),
            [
                *self.path,
                *(
                    (self.time, k, a.valve)
                    for k, a in self.actors.openable(self.open).items()
                ),
            ],
        )


def solve(time, **actors):
    initial_state = State(
        time=1,
        limit=time,
        open=set(),
        actors=Actors(
            collections.OrderedDict({k: At(v) for k, v in actors.items()})
        ),
        path=[],
    )

    # q: list[tuple[int, int, int, State]] = [(0, 0, 0, initial_state)]
    q = [initial_state]
    best = 0
    # seen = {}
    # i = 0
    while q:
        # _, _, d, s = heapq.heappop(q)
        s = q.pop()

        state_str = f"{' '*d}{s}"
        print(f"{state_str:150}{s.score()}", file=sys.stderr)

        if s.score() > best:
            best = s.score()

        if s.time >= time:
            continue

        q.extend(s.evolve())
        # for n in s.evolve():
        # k = ",".join(sorted(n.open))
        # if seen.get(k, -1) > n.score():
        #     st = f"{' '* d}{n} pruned"
        #     print(f"{st:150}{n.score()}", file=sys.stderr)
        #     continue

        # i += 1
        # heapq.heappush(q, (n.time, i, d + 1, n))
        # seen[k] = n.score()

    return best


def time_it(f):
    x = {}

    def run():
        x["x"] = f()

    t = timeit.timeit(setup="gc.enable()", stmt=lambda: run(), number=1)

    return x["x"], t


def a():
    return time_it(lambda: solve(30, me="AA"))


def b():
    return time_it(lambda: solve(26, me="AA", elephant="AA"))


if __name__ == "__main__":
    print("a:", a())
    print("b:", b())
