#!/usr/bin/env python3

import heapq
import re
import sys


def parse():
    rx = re.compile(
        " ".join(
            [
                r"Sensor at x=(-?\d+), y=(-?\d+):",
                r"closest beacon is at x=(-?\d+), y=(-?\d+)",
            ]
        )
    )
    sensors: list[tuple[tuple[int, int], int]] = []
    beacons: set[tuple[int, int]] = set()
    for line in sys.stdin.readlines():
        m = rx.match(line.strip())
        if not m:
            print(
                "could not parse sensor from line; skipping:",
                line,
                file=sys.stderr,
            )
            continue
        (sx, sy), (bx, by) = (
            (int(m.group(1)), int(m.group(2))),
            (int(m.group(3)), int(m.group(4))),
        )
        sensors.append(((sx, sy), abs(bx - sx) + abs(by - sy)))
        beacons.add((bx, by))
    return sensors, beacons


sensors, beacons = parse()


def one_d(xlo, xhi, y):
    q = [(xhi - xlo, xlo, xhi)]

    i = 0
    while q and i < 100:
        sz, lo, hi = heapq.heappop(q)
        if any(
            abs(sx - lo) + abs(sy - y) <= d and abs(sx - hi) + abs(sy - y) <= d
            for (sx, sy), d in sensors
        ):
            # this sensor sees the entire block; no need to look further
            continue

        if sz == 1:
            # single-coord block found; it's a candidate
            yield (lo, y)
            # but it can't be subdivided, so no need to look further
            continue

        mid = lo + (hi - lo) // 2

        heapq.heappush(q, (mid - lo + 1, lo, mid))
        heapq.heappush(q, (hi - mid + 1, mid, hi))
        i += 1


def size(xlo, xhi, ylo, yhi):
    return (xhi - xlo + 1) * (yhi - ylo + 1)


def split(xlo, xhi, ylo, yhi):
    xm = xlo + (xhi - xlo) // 2
    ym = ylo + (yhi - ylo) // 2

    yield (xlo, xm, ylo, ym)
    yield (xlo, xm, min(ym + 1, yhi), yhi)
    yield (min(xm + 1, xhi), xhi, ylo, ym)
    yield (min(xm + 1, xhi), xhi, min(ym + 1, yhi), yhi)


def seen_by(xlo, xhi, ylo, yhi, sx, sy, d):
    return (
        abs(xlo - sx) + abs(ylo - sy) <= d
        and abs(xhi - sx) + abs(ylo - sy) <= d
        and abs(xlo - sx) + abs(yhi - sy) <= d
        and abs(xhi - sx) + abs(yhi - sy) <= d
    )


def two_d(*bounds):
    q = [(size(*bounds), bounds)]

    while q:
        sz, box = heapq.heappop(q)
        if any(seen_by(*box, *s, d) for s, d in sensors):
            continue

        if sz == 1:
            yield box[0], box[2]
            continue

        for box in split(*box):
            heapq.heappush(q, (size(*box), box))


def a():
    y = 2000000
    xlo = min(sx - (d - abs(y - sy)) for (sx, sy), d in sensors)
    xhi = max(sx + (d - abs(y - sy)) for (sx, sy), d in sensors)
    candidates = list(one_d(xlo, xhi, y))

    return xhi - xlo - len(candidates)


def b():
    x, y = next(two_d(0, 4000000, 0, 4000000))
    return 4000000 * x + y


print("a:", a())
print("b:", b())
