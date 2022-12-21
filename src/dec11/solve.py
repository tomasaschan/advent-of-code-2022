#!/usr/bin/env python3

import sys
import collections
from typing import Callable, Iterable, TypedDict

input = sys.stdin.read()
sys.set_int_max_str_digits(10000)


class Monkey(TypedDict):
    items: collections.deque[int]
    op: Callable[[int], int]
    test: tuple[int, int, int]
    inspected: int


def parse(input) -> Iterable[tuple[int, Monkey]]:
    def ix(monkey):
        return int(monkey[0].split()[-1].strip(":"))

    def starting_items(monkey):
        return collections.deque(
            [
                int(x.strip(","))
                for x in monkey[1].split()
                if x.strip(",").isnumeric()
            ]
        )

    def operation(monkey):
        expr = monkey[2].split()[-3:]

        def oprnd(x, a):
            match a:
                case "old":
                    return x
                case d:
                    return int(d)

        def eval(x):
            a, b = oprnd(x, expr[0]), oprnd(x, expr[2])
            match expr[1]:
                case "*":
                    return a * b
                case "+":
                    return a + b

        return eval

    def test(monkey):
        denominator = int(monkey[3].split()[-1])
        if_true = int(monkey[4].split()[-1])
        if_false = int(monkey[5].split()[-1])
        return (denominator, if_true, if_false)

    for monkey in input.split("\n\n"):
        monkey = monkey.splitlines()
        yield (
            ix(monkey),
            {
                "items": starting_items(monkey),
                "op": operation(monkey),
                "test": test(monkey),
                "inspected": 0,
            },
        )


def throw(monkeys, i, relax):
    monkey = monkeys[i]
    divisor = 1
    for m in monkeys.values():
        divisor *= m["test"][0]

    while monkey["items"]:
        monkey["inspected"] += 1
        item = monkey["items"].popleft()
        item = monkey["op"](item)
        if relax:
            item //= 3
        item %= divisor
        if item % monkey["test"][0] == 0:
            monkeys[monkey["test"][1]]["items"].append(item)
        else:
            monkeys[monkey["test"][2]]["items"].append(item)


def monkey_business(monkeys):
    hi, snd = -1, -1
    for x in (m["inspected"] for m in monkeys.values()):
        if x > hi:
            snd, hi = hi, x
        elif x > snd:
            snd = x

    return hi * snd


def a():
    monkeys = dict(parse(input))

    for _ in range(20):
        for i in monkeys.keys():
            throw(monkeys, i, relax=True)

    return monkey_business(monkeys)


def b():
    monkeys = dict(parse(input))

    for _ in range(10000):
        for i in monkeys.keys():
            throw(monkeys, i, relax=False)

    return monkey_business(monkeys)


print("a:", a())
print("b:", b())
