#!/usr/bin/env python3

import collections
import re
import sys

rx = re.compile(
    r"Valve (\w+) has flow rate=(\d+); tunnels? leads? to valves? ([\w, ]+)"
)

layout = {
    m.group(1): (int(m.group(2)), m.group(3).split(", "))
    for m in map(rx.match, sys.stdin.readlines())
}

initial_state = {
    "t": 1,
    "at": "AA",
    "open": set(),
    "total": 0,
}


def show_flow(s, file=sys.stdout):
    if not s["open"]:
        print("No valves are open.", file=file)
    elif len(s["open"]) == 1:
        print(
            f"Valve {sorted(s['open'])[0]} is open, releasing {total_flow(s)} pressure.",
            file=file,
        )
    elif len(s["open"]) == 2:
        print(
            f"Valves {' and '.join(sorted(s['open']))} are open, releasing {total_flow(s)} pressure.",
            file=file,
        )
    else:
        print(
            f"Valves {', '.join(sorted(s['open'])[:-1])}, and {sorted(s['open'])[-1]} are open, releasing {total_flow(s)} pressure.",
            file=file,
        )
    print(
        f"Total released pressure is now {s['total']}; expected end total is {expected_total(s)}.",
        file=file,
    )


def total_flow(s):
    return sum(layout[x][0] for x in s["open"])


def release(s, verbose=False, file=sys.stdout):
    nxt = {**s, "t": s["t"] + 1, "total": s["total"] + total_flow(s)}
    if verbose:
        show_flow(nxt, file=file)
    return nxt


def move(valve, s, verbose=False, file=sys.stdout):
    assert (
        valve in layout[s["at"]][1]
    ), f'illegal to move from {s["at"]} to {valve}'

    nxt = release(s, verbose=verbose, file=file)

    if verbose:
        print(f"You move to valve {valve}.", file=file)
    return {**nxt, "at": valve}, ("move", valve)


def open(valve, s, verbose=False, file=sys.stdout):
    nxt = release(s, verbose=verbose, file=file)
    if verbose:
        print(f"You open valve {valve}.", file=file)
    return {**nxt, "open": s["open"].union((valve,))}, ("open", valve)


def key(s):
    return f"{s['at']}|{','.join(sorted(s['open']))}"


def expected_total(s):
    return s["total"] + (30 - s["t"] + 1) * total_flow(s)


def available_next_states(s):
    if s["t"] >= 30:
        return

    for neighbor in layout[s["at"]][1]:
        yield move(neighbor, s)

    if s["at"] not in s["open"]:
        yield open(s["at"], s)


def search():
    q = collections.deque()
    q.append((initial_state, []))

    seen = {}
    i = 0
    while q:
        (s, path) = q.popleft()
        i += 1

        for nxt, m in available_next_states(s):
            k = key(nxt)
            if k not in seen or seen[k][0] < expected_total(nxt):
                seen[k] = (expected_total(nxt), [*path, m])
                q.append((nxt, [*path, m]))

    return max(seen.values(), key=lambda v: v[0])


def show_path(path):
    s = initial_state

    def show_step():
        print("== Minute", s["t"], "==", file=sys.stderr)

    for m, v in path:
        show_step()
        match m:
            case "open":
                s, _ = open(v, s, verbose=True, file=sys.stderr)
            case "move":
                s, _ = move(v, s, verbose=True, file=sys.stderr)
        print(file=sys.stderr)

    while s["t"] <= 30:
        show_step()
        s = release(s, verbose=True, file=sys.stderr)
        print(file=sys.stderr)


def a():
    best_result, best_path = search()

    show_path(best_path)
    return best_result


example_best_path = [
    ("move", "DD"),
    ("open", "DD"),
    ("move", "CC"),
    ("move", "BB"),
    ("open", "BB"),
    ("move", "AA"),
    ("move", "II"),
    ("move", "JJ"),
    ("open", "JJ"),
    ("move", "II"),
    ("move", "AA"),
    ("move", "DD"),
    ("move", "EE"),
    ("move", "FF"),
    ("move", "GG"),
    ("move", "HH"),
    ("open", "HH"),
    ("move", "GG"),
    ("move", "FF"),
    ("move", "EE"),
    ("open", "EE"),
    ("move", "DD"),
    ("move", "CC"),
    ("open", "CC"),
]

print("a:", a())
