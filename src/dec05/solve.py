#!/usr/bin/env python3

import re
import sys

input = sys.stdin.read().split("\n\n")


def parse_stacks():
    n_stacks = len(input[0].splitlines()[-1].split())
    stacks = {i: [] for i in range(1, n_stacks + 1)}

    for line in input[0].splitlines():
        for i in range(0, n_stacks * 4, 4):
            if line[i] == "[":
                stacks[(i / 4) + 1].append(line[i + 1])

    for i in stacks:
        stacks[i].reverse()

    return stacks


def parse_instructions():
    rx = re.compile(r"^move (\d+) from (\d+) to (\d+)$")

    return [
        tuple(int(g) for g in rx.fullmatch(instruction).groups())
        for instruction in input[1].splitlines()
    ]


def word(stacks):
    return "".join(
        v for _, v in sorted((i, stack.pop()) for i, stack in stacks.items())
    )


def solve(one_by_one):
    stacks, instructions = parse_stacks(), parse_instructions()
    for n, src, dst in instructions:
        stacks[dst].extend(
            reversed(stacks[src][-n:]) if one_by_one else stacks[src][-n:]
        )
        stacks[src] = stacks[src][:-n]
    return word(stacks)


print("a:", solve(one_by_one=True))
print("b:", solve(one_by_one=False))
