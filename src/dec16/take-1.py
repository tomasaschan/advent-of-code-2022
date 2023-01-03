#!/usr/bin/env python3

import collections
import dataclasses
import functools
import re
import sys
from typing import Iterable, Union, cast

rx = re.compile(
    r"Valve (\w+) has flow rate=(\d+); tunnels? leads? to valves? ([\w, ]+)"
)
VERBOSE = False

Cave = collections.namedtuple("Cave", ("rate", "tunnels"))
layout = {
    cast(str, m.group(1)): Cave(int(m.group(2), 10), m.group(3).split(", "))
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
    actors: dict[str, Union[AtValve, InTransit]]
    path: list[tuple[int, str, str]]

    def __str__(self):
        open = ",".join(sorted(self.open))
        actors = " ".join(
            (
                f"{k}@{a.at}"
                if isinstance(a, AtValve)
                else f"{k}@{a.toward}/{self.time_left-a.arrives}"
            )
            for k, a in sorted(self.actors.items())
        )
        return f"t={self.time_left:2d} s={self.score} o={{{open}}} {actors}"

    def nexts(self, seen: dict[str, int]) -> Iterable["State"]:
        if VERBOSE:
            print(
                "finding next states with",
                sorted(self.open),
                "open and actors",
                self.actors,
                "and seen",
                seen,
            )

        if all(
            (
                isinstance(a, InTransit)
                or (
                    isinstance(a, AtValve)
                    and {}
                    == useful_valves
                    - (
                        self.open
                        | {
                            x.toward
                            for x in self.actors.values()
                            if isinstance(x, InTransit)
                        }
                    )
                )
            )
            for a in self.actors.values()
        ):
            # all actors are in transit;
            # advance the time until the first one(s) arrive
            if VERBOSE:
                print("all travelling; advancing time", self.actors)
            yield self.advance()
        elif any(
            isinstance(a, AtValve)
            and (a.at in self.open or a.at not in useful_valves)
            for a in self.actors.values()
        ):
            # there are actors standing at open (or useless) valves; initiate
            # their moves before potentially opening other valves.
            yield from self.move_done(seen)

        elif all(
            isinstance(a, InTransit)
            or (
                isinstance(a, AtValve)
                and a.at not in self.open
                and a.at in useful_valves
            )
            for a in self.actors.values()
        ):
            if VERBOSE:
                print("opening valves")

            # all stationary actors are at closed valves; open them!
            yield self.open_valves()

    def open_valves(self) -> "State":
        openable_valves = {
            k: a
            for k, a in self.actors.items()
            if isinstance(a, AtValve)
            and a.at not in self.open
            and a.at in useful_valves
        }

        other_actors = {
            k: a.step_to(self.time_left - 1)
            for k, a in self.actors.items()
            if k not in openable_valves.keys()
        }
        actors = {
            **openable_valves,
            **other_actors,
        }

        # open all valves that are possible to open
        return State(
            self.time_left - 1,
            self.score
            + sum(
                (self.time_left - 1) * layout[a.at].rate
                for a in openable_valves.values()
            ),
            self.open.union(a.at for a in openable_valves.values()),
            actors,
            [
                *self.path,
                *(
                    (self.time_left - 1, k, a.at)
                    for k, a in openable_valves.items()
                ),
            ],
        )

    def advance(self) -> "State":
        arrival = max(
            a.arrives for a in self.actors.values() if isinstance(a, InTransit)
        )

        return State(
            arrival,
            self.score,
            self.open,
            {k: a.step_to(arrival) for k, a in self.actors.items()},
            self.path,
        )

    def move_done(self, seen: dict[str, int]) -> Iterable["State"]:
        mover = next(
            k
            for k, a in self.actors.items()
            if isinstance(a, AtValve)
            and (a.at in self.open or a.at not in useful_valves)
        )
        if VERBOSE:
            print(
                "actors at open/useless valves; moving",
                mover,
                "from",
                self.actors[mover],
                f"(all actors: {self.actors})",
            )

        yield from self.move_one(mover, seen)

    def move_one(
        self, actor_key: str, seen: dict[str, int]
    ) -> Iterable["State"]:
        mover = self.actors[actor_key]
        assert isinstance(
            mover, AtValve
        ), "can't move already travelling actor"

        for vnext in useful_valves:
            if vnext in self.open | {
                a.at if isinstance(a, AtValve) else a.toward
                for a in self.actors.values()
            }:
                continue
            # if not self.move_is_useful(actor_key, vnext, seen):
            #     continue

            actors = {
                actor_key: InTransit(
                    vnext, self.time_left - steps_between(mover.at, vnext)
                ),
                **{k: a for k, a in self.actors.items() if k != actor_key},
            }

            yield State(
                self.time_left, self.score, self.open, actors, self.path
            )

    def move_is_useful(
        self, actor: str, valve: str, seen: dict[str, int]
    ) -> bool:
        assert valve not in self.open
        assert isinstance(self.actors[actor], AtValve)

        steps_away = steps_between(cast(AtValve, self.actors[actor]).at, valve)
        assert steps_away > 0

        if steps_away >= self.time_left:
            return False

        if layout[valve].rate == 0:
            return False

        def key():
            opened = {}
            for _, k, v in self.path:
                if k in opened:
                    opened[k].append(v)
                else:
                    opened[k] = [v]

            for k, v in self.actors.items():
                if isinstance(v, InTransit):
                    if k in opened:
                        opened[k].append(v.toward)
                    else:
                        opened[k] = [v.toward]

            if actor in opened:
                opened[actor].append(valve)
            else:
                opened[actor] = [valve]

            return "|".join(
                sorted(
                    f"{k}:{','.join(sorted(vs))}" for k, vs in opened.items()
                )
            )

        k = key()

        new_score = (
            # current score
            self.score
            # additions from already travelling actors
            + sum(
                (a.arrives - 1) * layout[a.toward].rate
                for a in self.actors.values()
                if isinstance(a, InTransit)
            )
            # additions from this move
            + (self.time_left - steps_away - 1) * layout[valve].rate
        )

        if k not in seen or seen[k] < new_score:
            seen[k] = new_score
            return True

        print(
            "moving",
            actor,
            "to",
            valve,
            "in",
            steps_away,
            "steps is not useful; key",
            k,
            "best score:",
            seen[k],
            "this score:",
            new_score,
        )
        return False


def solve(time, **actor):
    initial_state = State(time, 0, set(), {**actor}, [])
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

    if VERBOSE:
        print(
            "best path was",
            sorted((time - t, a, v) for t, a, v in best[2]),
            "yielding a final rate of",
            best[1],
            "and a score of",
            best[0],
        )
    return best[0]


def a():
    if VERBOSE:
        print("solving a")
    return solve(30, me=AtValve("AA"))


def b():
    if VERBOSE:
        print("solving b")
    return solve(26, me=AtValve("AA"), elephant=AtValve("AA"))


print("a:", a())
print("b:", b())


expected_best = [
    (2, "elephant", "DD"),
    (3, "me", "JJ"),
    (7, "me", "BB"),
    (7, "elephant", "HH"),
    (9, "me", "CC"),
    (11, "elephant", "EE"),
]


def show_level(state, level, max_level, seen):
    if state.time_left == 0:
        return

    # if all(
    #     (ma, aa, va) == (26 - m, a, v)
    #     for (ma, aa, va), (m, a, v) in zip(state.path, expected_best)
    # ):
    print(
        f'{"  " * level}{state}',
        [(26 - (m), a, v) for m, a, v in state.path],
    )
    for n in state.nexts(seen):
        show_level(n, level + 1, max_level, seen)

    # else:
    # if True:
    # print(
    #     "  " * level,
    #     "  path mismatch",
    #     [
    #         (i, (ma, aa, va), (26 - m, a, v))
    #         for (i, ((ma, aa, va), (m, a, v))) in enumerate(
    #             zip(state.path, expected_best)
    #         )
    #         if (ma, va) != (26 - m, v)
    #     ],
    # )


# show_level(
#     State(26, 0, set(), {"me": AtValve("AA"), "elephant": AtValve("AA")}, []),
#     0,
#     8,
#     {},
# )
# initial_state = State(
#     26, 0, set(), {"me": AtValve("AA"), "elephant": AtValve("AA")}, []
# )
# seen = {}
# print(initial_state)
# for n in list(initial_state.nexts(seen)):
#     print("\t", n)
#     for n2 in list(n.nexts(seen)):
#         print("\t\t", n2)
#         for n3 in list(n2.nexts(seen)):
#             print("\t\t\t", n3)
#             for n4 in list(n3.nexts(seen)):
#                 print("\t\t\t\t", n4)
