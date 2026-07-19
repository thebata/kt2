"""Paste this into the KT2's built-in Python IDE (/apps/ide/) and press Run.

Idle-mode loop: forever picks a random move from the set of actions
confirmed to work on real hardware (see
../docs/kt2/python-api.md#naming-and-what-actually-exists) and performs
it, with a short random pause in between.

To stop it from outside without power-cycling the robot:
    GET http://<ip>/api?p=/py/vm/break
(see ../docs/kt2/device-api.md#execute-python---the-important-one)
"""
import random
import actions

MOVES = [
    ("left_kick", lambda: q.play(actions.left_kick(q), dly=0.1)),
    ("right_kick", lambda: q.play(actions.right_kick(q), dly=0.1)),
    ("left_punch", lambda: q.play(actions.left_punch(q), dly=0.1)),
    ("right_punch", lambda: q.play(actions.right_punch(q, y=1), dly=0.1)),
    ("left_flip", lambda: q.play(actions.left_flip(q), dly=0.1)),
    ("right_flip", lambda: q.play(actions.right_flip(q), dly=0.1)),
    ("walk", lambda: q.play(actions.walk(q, ofs=actions.ofs_stand), 3, dly=0.1)),
    ("turn_left", lambda: actions.c_pivot(q, 2)),
    ("turn_right", lambda: actions.c_pivot(q, -2)),
]

actions.one_key_reset(q)

while True:
    name, move = MOVES[random.randint(0, len(MOVES) - 1)]
    print(name)
    move()
    sleep(random.randint(1, 3))
