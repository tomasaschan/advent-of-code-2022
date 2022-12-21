#!/usr/bin/env python3

import sys

instructions = [
    (d, int(s))
    for d, s in map(lambda line: line.strip().split(), sys.stdin.readlines())
]


def sgn(x):
    if x < 0:
        return -1
    if x > 0:
        return 1
    return 0


def move(state, dim, d):
    return tuple(x + d if i == dim else x for i, x in enumerate(state))


def a():
    state = {"H": (0, 0), "T": (0, 0), "seen": set()}

    def move_head(dir):
        match dir:
            case "L":
                state["H"] = move(state["H"], 0, -1)
            case "R":
                state["H"] = move(state["H"], 0, 1)
            case "U":
                state["H"] = move(state["H"], 1, 1)
            case "D":
                state["H"] = move(state["H"], 1, -1)
            case _:
                assert False, f"unsupported instruction {instruction}"

    def move_tail():
        if (
            abs(state["H"][0] - state["T"][0]) <= 1
            and abs(state["H"][1] - state["T"][1]) <= 1
        ):
            return

        state["T"] = move(state["T"], 0, -sgn(state["T"][0] - state["H"][0]))
        state["T"] = move(state["T"], 1, -sgn(state["T"][1] - state["H"][1]))
        state["seen"].add(state["T"])

    def step(instruction):
        match instruction:
            case dir, d:
                for _ in range(d):
                    move_head(dir)
                    move_tail()
            case _:
                assert False, "unsupported instruction " + instruction

    state["seen"].add(state["T"])

    for instruction in instructions:
        step(instruction)

    return len(state["seen"])


def b():
    state = {i: (0, 0) for i in range(10)}
    state["seen"] = set()

    def move_head(d):
        match d:
            case "L":
                state[0] = move(state[0], 0, -1)
            case "R":
                state[0] = move(state[0], 0, 1)
            case "U":
                state[0] = move(state[0], 1, 1)
            case "D":
                state[0] = move(state[0], 1, -1)

    def move_knot(i):
        assert 0 < i and i < 10, "invalid knot"

        if (
            abs(state[i][0] - state[i - 1][0]) <= 1
            and abs(state[i][1] - state[i - 1][1]) <= 1
        ):
            return

        state[i] = move(state[i], 0, sgn(state[i - 1][0] - state[i][0]))
        state[i] = move(state[i], 1, sgn(state[i - 1][1] - state[i][1]))

    def step(d):
        move_head(d)
        for i in range(1, 10):
            move_knot(i)
        state["seen"].add(state[9])

    for d, n in instructions:
        for _ in range(n):
            step(d)

    return len(state["seen"])


print("a:", a())
print("b:", b())
