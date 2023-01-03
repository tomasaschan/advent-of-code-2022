def a():
    return 30, [
        (2, "me", "DD"),
        (5, "me", "BB"),
        (9, "me", "JJ"),
        (17, "me", "HH"),
        (21, "me", "EE"),
        (24, "me", "CC"),
    ]


def b():
    return 26, [
        (2, "elephant", "DD"),
        (3, "me", "JJ"),
        (7, "me", "BB"),
        (7, "elephant", "HH"),
        (9, "me", "CC"),
        (11, "elephant", "EE"),
    ]


flows = {"BB": 13, "CC": 2, "DD": 20, "EE": 3, "HH": 22, "JJ": 21}
T, opens = b()
for i in range(len(opens)):
    score = 0

    for t, _, v in opens[0 : (i + 1)]:
        # print(
        #     "valve",
        #     v,
        #     "emits",
        #     flows[v],
        #     "for",
        #     30 - t,
        #     "minutes, yielding a total score of",
        #     (30 - t + flows[v]),
        # )

        score += (T - t) * flows[v]

    print(
        "total score up to time",
        opens[i][0],
        "with valves",
        sorted(v for _, _, v in opens[0 : i + 1]),
        "is",
        score,
    )

print(",".join(map(str, a()[1])))
