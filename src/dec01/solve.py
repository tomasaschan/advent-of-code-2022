#!/usr/bin/env python3

import sys

packs = sorted(
    (
        sum(int(line) for line in pack.split("\n") if line.strip())
        for pack in sys.stdin.read().split("\n\n")
    ),
    reverse=True,
)

print("a:", packs[0])
print("b:", sum(packs[:3]))
