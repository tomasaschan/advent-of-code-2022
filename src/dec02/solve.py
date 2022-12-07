#!/usr/bin/env python3

import sys

input = sys.stdin.readlines()
moves = ["🤘", "📜", "✂️"]
score = [3, 6, 0]


def score_round(them, me):
    return moves.index(me) + 1 + score[(moves.index(me) - moves.index(them)) % 3]


def strategy(my_move):
    for round in input:
        t, m = round.split()
        them = moves["ABC".index(t.strip())]
        me = my_move(them, m.strip())
        yield them, me


def a():
    def my_move(them, me):
        return {"X": "🤘", "Y": "📜", "Z": "✂️"}[me]

    total_score = sum(score_round(*round) for round in strategy(my_move))
    print("a:", total_score)


def b():
    def my_move(them, me):
        move = moves[(moves.index(them) + {"X": -1, "Y": 0, "Z": 1}[me]) % 3]
        return move

    total_score = sum(score_round(*round) for round in strategy(my_move))
    print("b:", total_score)


a()
b()
