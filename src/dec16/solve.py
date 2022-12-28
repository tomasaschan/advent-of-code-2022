#!/usr/bin/env python3

import collections
import dataclasses
import functools
import re
import sys
from typing import Iterable, Union

rx = re.compile(
    r"Valve (\w+) has flow rate=(\d+); tunnels? leads? to valves? ([\w, ]+)"
)

Cave = collections.namedtuple("Cave", ("rate", "tunnels"))
layout = {
    str(m.group(1)): Cave(int(m.group(2), 10), m.group(3).split(", "))
    for m in map(rx.match, map(str, sys.stdin.readlines()))
    if m is not None
}

all_valves = set(layout.keys())
useful_valves = set(k for k, (r, _) in layout.items() if r > 0)


@functools.cache
def steps_between(start: str, end: str) -> int:
    q: collections.deque[tuple[str, int]] = collections.deque([(start, 0)])
    seen = set()
    while q:
        (here, steps) = q.popleft()
        for there in layout[here].tunnels:
            if there == end:
                return steps + 1

            if there not in seen:
                seen.add(there)
                q.append((there, steps + 1))
    else:
        raise Exception(f"No path from {start} to {end} found!")


@dataclasses.dataclass
class AtValve:
    at: str

    def step_to(self, _: int) -> "AtValve":
        return AtValve(self.at)


@dataclasses.dataclass
class InTransit:
    toward: str
    arrives: int

    def step_to(self, t: int) -> Union[AtValve, "InTransit"]:
        return (
            AtValve(self.toward)
            if t == self.arrives
            else InTransit(self.toward, self.arrives)
        )


@dataclasses.dataclass
class State:
    time_left: int
    score: int
    open: set[str]
    actors: list[Union[AtValve, InTransit]]
    path: list[tuple[str, int]]

    def __str__(self):
        open = ",".join(sorted(self.open))
        actors = " ".join(
            (
                f"@{a.at}"
                if isinstance(a, AtValve)
                else f"@{a.toward}/{self.time_left-a.arrives}"
            )
            for a in self.actors
        )
        return f"t={self.time_left:2d} s={self.score} o={{{open}}} {actors}"

    def nexts(self, seen: dict[str, int]) -> Iterable["State"]:
        if all(isinstance(a, InTransit) for a in self.actors):
            # all actors are in transit;
            # advance the time until the first one(s) arrive
            yield self.advance()

        elif any(
            isinstance(a, AtValve)
            and a.at
            in self.open | {v for v, c in layout.items() if c.rate == 0}
            for a in self.actors
        ):
            # there are actors standing at open (or useless) valves; initiate
            # their moves before potentially opening other valves.
            yield from self.move_done(seen)

        elif len({a.at for a in self.actors if isinstance(a, AtValve)}) != len(
            [a.at for a in self.actors if isinstance(a, AtValve)]
        ):
            # there are multiple actors standing at the same valve; initiate
            # moves so that only one remain at each valve.
            yield from self.move_dupes(seen)

        elif all(
            isinstance(a, InTransit)
            or (
                isinstance(a, AtValve)
                and a.at not in self.open
                and a.at in useful_valves
            )
            for a in self.actors
        ):
            # all stationary actors are at closed valves; open them!
            yield self.open_valves()

    def open_valves(self) -> "State":
        openable_valves = {
            (i, a.at)
            for i, a in enumerate(self.actors)
            if isinstance(a, AtValve)
            and a.at not in self.open
            and a.at in useful_valves
        }
        other_actors = [
            a
            for i, a in enumerate(self.actors)
            if i not in (j for j, _ in openable_valves)
        ]
        actors = [
            *(AtValve(v) for _, v in openable_valves),
            *(a.step_to(self.time_left - 1) for a in other_actors),
        ]

        # open all valves that are possible to open
        return State(
            self.time_left - 1,
            self.score
            + sum(
                (self.time_left - 1) * layout[v].rate
                for _, v in openable_valves
            ),
            self.open.union(v for _, v in openable_valves),
            actors,
            [
                *self.path,
                *((v, self.time_left - 1) for _, v in openable_valves),
            ],
        )

    def advance(self) -> "State":
        assert all(
            isinstance(a, InTransit) for a in self.actors
        ), "all actors must be moving"

        arrival = max(
            a.arrives for a in self.actors if isinstance(a, InTransit)
        )

        return State(
            arrival,
            self.score,
            self.open,
            [
                AtValve(a.toward) if a.arrives == arrival else a
                for a in self.actors
                if isinstance(a, InTransit)
            ],
            self.path,
        )

    def move_dupes(self, seen: dict[str, int]) -> Iterable["State"]:
        collisions = [
            (i, a)
            for i, a in enumerate(self.actors)
            if isinstance(a, AtValve)
            and sum(
                1
                for x in self.actors
                if isinstance(x, AtValve) and x.at == a.at
            )
            > 1
        ]
        mover = collisions[0]
        others = [a for i, a in enumerate(self.actors) if i != mover[0]]

        for vnext in useful_valves:
            if vnext in self.open | {
                a.at if isinstance(a, AtValve) else a.toward
                for a in self.actors
            }:
                continue
            if not self.move_is_useful(
                vnext, steps_between(mover[1].at, vnext), seen
            ):
                continue

            actors = [
                InTransit(
                    vnext,
                    self.time_left - steps_between(mover[1].at, vnext),
                ),
                *others,
            ]
            yield from State(
                self.time_left,
                self.score,
                self.open,
                actors,
                self.path,
            ).nexts(seen)

    def move_done(self, seen: dict[str, int]) -> Iterable["State"]:
        mover = next(
            (i, a)
            for i, a in enumerate(self.actors)
            if isinstance(a, AtValve)
            and a.at
            in self.open | {v for v, c in layout.items() if c.rate == 0}
        )
        others = [a for i, a in enumerate(self.actors) if i != mover[0]]

        for vnext in useful_valves:
            if vnext in self.open | {
                a.at if isinstance(a, AtValve) else a.toward
                for a in self.actors
            }:
                continue
            if not self.move_is_useful(
                vnext, steps_between(mover[1].at, vnext), seen
            ):
                continue

            actors = [
                InTransit(
                    vnext,
                    self.time_left - steps_between(mover[1].at, vnext),
                ),
                *others,
            ]

            yield from State(
                self.time_left,
                self.score,
                self.open,
                actors,
                self.path,
            ).nexts(seen)

    def move_is_useful(
        self, valve: str, steps_away: int, seen: dict[str, int]
    ) -> bool:
        assert valve not in self.open
        assert steps_away > 0

        if steps_away >= self.time_left:
            return False

        k = ",".join(sorted(self.open | {valve}))
        new_score = (
            self.score + (self.time_left - steps_away - 1) * layout[valve].rate
        )

        if seen.get(k, -1) >= new_score:
            return False

        seen[k] = new_score
        return True


def solve(time, *actor):
    initial_state = State(time, 0, set(), [*actor], [])
    best = (0, 0, [])
    seen = {}

    q = collections.deque([initial_state])
    while q:
        s = q.popleft()
        if s.score > best[0]:
            best = (s.score, sum(layout[v].rate for v in s.open), s.path)

        if s.time_left == 0:
            continue

        q.extend(s.nexts(seen))

    return best[0]


def a():
    return solve(30, AtValve("AA"))


def b():
    return solve(26, AtValve("AA"), AtValve("AA"))


print("a:", a())
print("b:", b())
