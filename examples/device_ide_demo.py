"""Paste this directly into the KT2's built-in Python IDE (/apps/ide/) and press Run.

Not meant to run on your computer - q, car, actions etc. only exist on the
robot itself. See ../docs/kt2/python-api.md for the full API.

Only uses actions confirmed working on real hardware (see
../docs/kt2/python-api.md#naming-and-what-actually-exists). If your robot
uses the older Gen A editor (kt2 / __actions instead of q / actions), see
the Gen A notes in that same doc - the call shapes differ.
"""
import actions

car.buzzer.hello()                                          # boot chirp
actions.one_key_reset(q)                                     # neutral pose
sleep(1)

q.play(actions.walk(q, ofs=actions.ofs_stand), 5, dly=0.1)    # forward 5 steps
actions.c_pivot(q, 3)                                         # turn left
q.play(actions.left_kick(q), dly=0.1)                         # kick

print("done")
