#!/usr/bin/env python3

import functools
import string
import sys

input = sys.stdin.readlines()


def prio(item):
    if item in string.ascii_lowercase:
        return string.ascii_lowercase.index(item) + 1
    else:
        return string.ascii_uppercase.index(item) + 27


print(
    "a:",
    sum(
        prio(
            set(rucksack[: int(len(rucksack) / 2)])
            .intersection(set(rucksack[int(len(rucksack) / 2) :]))
            .pop()
        )
        for rucksack in input
    ),
)


def elf_groups():
    return [
        [set(rucksack.strip()) for rucksack in input[i : i + 3]]
        for i in range(0, len(input), 3)
    ]


print(
    "b:",
    sum(
        prio(functools.reduce(lambda a, b: a.intersection(b), group).pop())
        for group in elf_groups()
    ),
)
