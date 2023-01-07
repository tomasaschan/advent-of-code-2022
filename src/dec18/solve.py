#!/usr/bin/env python3

import sys
import time

cells = {
    tuple((int(d) for d in line.strip().split(",")))
    for line in sys.stdin.readlines()
}

xlo, xhi, ylo, yhi, zlo, zhi = (
    min(x for x, _, _ in cells) - 1,
    max(x for x, _, _ in cells) + 1,
    min(y for _, y, _ in cells) - 1,
    max(y for _, y, _ in cells) + 1,
    min(z for _, _, z in cells) - 1,
    max(z for _, _, z in cells) + 1,
)


def step(p, dx=0, dy=0, dz=0):
    u, v, w = p
    return (u + dx, v + dy, w + dz)


def neighbors(p):
    return (
        step(p, dx=-1),
        step(p, dy=-1),
        step(p, dz=-1),
        step(p, dx=1),
        step(p, dy=1),
        step(p, dz=1),
    )


def a():
    n = len(cells) * 6
    for cell in cells:
        for neighbor in neighbors(cell):
            if neighbor in cells:
                n -= 1

    return n


def visualize(cells, z, if_in, if_out):
    return "\n".join(
        "".join(
            if_in if (x, y, z) in cells else if_out for x in range(xlo, xhi)
        )
        for y in range(ylo, yhi)
    )


def b():
    q = [(xlo, ylo, zlo)]
    N = 0
    seen = set()

    while q:
        p = q.pop()

        for (x, y, z) in neighbors(p):
            if (x, y, z) in cells:
                N += 1
            elif (
                (x, y, z) not in seen
                and xlo <= x <= xhi
                and ylo <= y <= yhi
                and zlo <= z <= zhi
            ):
                seen.add((x, y, z))
                q.append((x, y, z))

    return N, seen


def visualize_all():
    def side_by_side(columns, *, width=30):
        return "\n".join(
            "".join(c.ljust(width) for c in cs)
            for cs in zip(*(col.splitlines(keepends=False) for col in columns))
        )

    _, seen = b()

    for z in range(zlo, zhi + 1):
        print("\033c", end="")
        print("z =", z)
        print(
            side_by_side(
                [
                    "\n".join(
                        [
                            "exact shape",
                            visualize(
                                {
                                    (x, y, zp)
                                    for (x, y, zp) in cells
                                    if zp == z
                                },
                                z,
                                if_in="#",
                                if_out=".",
                            ),
                        ]
                    ),
                    "\n".join(
                        [
                            "as seen in part b",
                            visualize(seen, z, if_in=".", if_out="#"),
                        ]
                    ),
                ]
            )
        )

        time.sleep(1)


print("a:", a())
print("b:", b()[0])

# visualize_all()
