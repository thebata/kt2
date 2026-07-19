"""Paste this into the KT2's built-in Python IDE (/apps/ide/) and press Run.

There is no built-in "dance" move - `dance` isn't even in the vendor's
Blockly generators (see ../docs/kt2/python-api.md#naming-and-what-actually-exists),
so actions.dance(q) will raise AttributeError on the device.

This first checks whether your specific unit happens to expose one anyway
(firmware varies between units), and otherwise plays a custom "dance"
built only from actions confirmed to work on real hardware: kicks,
punches, flips and turns, with buzzer + LED for effect.
"""
import actions
import _led

if hasattr(actions, "dance"):
    q.play(actions.dance(q), dly=0.1)
else:
    car.buzzer.music("1=")
    _led.blink(led, hex_color=0xFF00FF, dur=2, interval=0.02, brightness=100)

    actions.one_key_reset(q)
    sleep(0.3)

    q.play(actions.left_kick(q), dly=0.1)
    q.play(actions.right_kick(q), dly=0.1)
    q.play(actions.left_punch(q), dly=0.1)
    q.play(actions.right_punch(q, y=1), dly=0.1)
    q.play(actions.left_flip(q), dly=0.1)
    q.play(actions.right_flip(q), dly=0.1)

    actions.c_pivot(q, 2)
    actions.c_pivot(q, -2)

    actions.one_key_reset(q)

print("done")
