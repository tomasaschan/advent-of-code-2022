#!/usr/bin/env python3

import sys

instructions = [tuple(line.strip().split()) for line in sys.stdin.readlines()]


def step(state):
    match instructions[state["p"]]:
        case ("noop",):
            yield {
                **state,
                "t": state["t"] + 1,
                "p": (state["p"] + 1) % len(instructions),
            }
        case ("addx", V):
            yield {**state, "t": state["t"] + 1}
            yield {
                **state,
                "t": state["t"] + 2,
                "x": state["x"] + int(V),
                "p": (state["p"] + 1) % len(instructions),
            }


def loop(signal, stops):
    stops = list(stops)
    state = {"x": 1, "t": 1, "p": 0}

    def emit_signal(s):
        if stops and s["t"] == stops[0]:
            yield signal(s)
            stops.remove(stops[0])

    while stops and state["t"] < stops[-1]:
        for s in step(state):
            yield from emit_signal(s)
        state = s


def pixel(s):
    y, x = divmod(s["t"] - 1, 40)
    return (x, y), abs(s["x"] - x) < 2


def draw_crt():
    pixelmap = {p: lit for p, lit in loop(pixel, range(2, 241))}
    pixelmap[0, 0] = True
    return "\n".join(
        "".join("#" if pixelmap[(x, y)] else "." for x in range(40))
        for y in range(6)
    )


print("a:", sum(loop(lambda s: s["x"] * s["t"], range(20, 221, 40))))
print("b:", draw_crt(), sep="\n")
