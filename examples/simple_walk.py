"""Simple example: connect to a KT2 and make it walk, turn and kick.

Usage:
    python simple_walk.py <robot-ip>

Only uses actions confirmed working on real hardware (see
../docs/kt2/python-api.md#naming-and-what-actually-exists): walk, c_pivot,
one_key_reset, left_kick. This assumes the "Gen B" API (q / actions); if your
robot uses the older Gen A editor (kt2 / __actions), see the README in this
folder.
"""
import sys
import time

from kt2_client import KT2

CODE = """
import actions
actions.one_key_reset(q)
q.play(actions.walk(q, ofs=actions.ofs_stand), 5, dly=0.1)
actions.c_pivot(q, 3)
q.play(actions.left_kick(q), dly=0.1)
print("done")
"""


def main():
    if len(sys.argv) != 2:
        print("usage: python simple_walk.py <robot-ip>", file=sys.stderr)
        raise SystemExit(1)

    bot = KT2(sys.argv[1])
    bot.hi()  # short chirp so you know the robot received something
    print("battery:", bot.battery())

    bot.py(CODE, wait=0)
    # Walking + turning + kicking takes a few seconds - poll /log with slack
    # instead of assuming the first response means it's finished.
    for _ in range(20):
        out = bot.log()
        if "done" in out:
            print(out)
            break
        time.sleep(0.5)
    else:
        print("timed out waiting for the robot to finish")


if __name__ == "__main__":
    main()
