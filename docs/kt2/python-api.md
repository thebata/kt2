# KT2 Python API

> **[Verified]** — every signature below was read out of the vendor's Blockly **code generators**
> at `https://guidan.com/b4/blk/modules/<edition>/<category>/generators.js`. Those generators are
> the source of truth for what the blocks emit, so the call shapes are exact.
>
> **But**: the `actions` and `imu` *modules themselves* live on the device at `/sys/bot/*.py` and
> could not be read. So parameter **ranges, units, defaults and return types are [Unknown]** unless
> noted. See [README.md](README.md) for provenance.
>
> **Update 2026-07-17:** tested against a physical unit for the first time. Confirmed live: this
> robot runs **Gen B** (`q`/`actions`), and a real servo calibration file resolved several
> `[Unknown]`s below — pin numbers, sign convention, and value range. Also confirmed: several
> actions documented in the generators **do not exist** on the device (e.g., `sit`, `dance`,
> `left_chop`). The generated call sites are aspirational or from a different firmware version —
> see [Naming and what actually exists](#naming-and-what-actually-exists). See the callouts marked
> **[Verified — hardware]**.

## Two API generations

The vendor ships **two incompatible Python APIs** for the KT2, from two different Blockly editors.
**[Verified]** — both are live right now.

| | **Gen B — `q` / `actions`** | **Gen A — `kt2` / `__actions`** |
|---|---|---|
| Editor | `/b4/blk/` — **linked from the KT2 hub** | `/kt2/` — standalone |
| Bundle | `app250506` (2025-05-06) | `app250103` (2025-01-03) |
| Config id | `b4-basic`, `b4-advanced` | `kt2` (module set `kt2-en`) |
| Robot object | **`q`** | **`kt2`** |
| Import | `import actions` | `import __actions` |
| LED import | `import _led` | `import __led` |
| Play | `q.play(frames, n, dly=0.1)` | `kt2.play(frames, n, wait=True)` + explicit `sleep(0.1)` |
| **Walk backward** | **`walk(q, x=-1)`** | **`walk(kt2, x=1)`** ⚠️ |
| Turn right | `c_pivot(q, -1*n)` | `c_pivot(kt2, n, y=1)` |
| Left/right variants | `left_punch` / `right_punch` | `punch(kt2)` / `punch(kt2, y=1)` |
| Posture offsets | `actions.ofs_*` ✅ | ❌ none |
| Raw frames | `q.f(...)` ✅ | ❌ none |
| Buzzer | `car.buzzer.*` — **identical in both** | `car.buzzer.*` |

**The `x` conflict is the dangerous one.** Gen B walks backward with `x=-1`; Gen A walks backward
with `x=1`. These directly contradict. **[Inferred]**: in Gen A `x` is a *reverse flag*, in Gen B
it's a *direction multiplier*. So `x=1` on Gen B means **forward**, but on Gen A means
**backward** — the same call does opposite things.

**Which one applies to you is [Unknown] without a device** — but for at least one unit, it's
settled. **[Verified — hardware, 2026-07-17]:**

```python
>>> print(q)
<Quadruped object at 3d816020>
>>> print(kt2)
NameError
>>> import actions          # OK — loaded from /sys/bot/actions.mpy
>>> import __actions        # ImportError: no module named '__actions'
```

That unit runs **Gen B**. `q` is an instance of a class literally named `Quadruped`, and `actions`
is precompiled bytecode (`.mpy`, not `.py`) on the firmware partition — which is also why it was
never readable as source over the file API; there's no source on the device to read, compiled or
not. This is one data point, not a guarantee for every unit — the evidence still favours Gen B in
general: it's newer, and the B4-KT2 product hub links to `/b4/blk/`, not `/kt2/`. But `/kt2/` is
the only **English** module set (`kt2-en`) and is named for the product. It may be a legacy build,
a localisation branch, or for older firmware.

**The rest of this page documents Gen B.** Gen A differences are noted inline. If your robot
rejects `q`, try `kt2`; if `import actions` fails, try `import __actions`. The quickest test, via
[device-api.md](device-api.md):

```python
bot.py("print(q)")           # Gen B?
bot.py("print(kt2)")         # Gen A?
```

Gen A also has **three actions Gen B doesn't**: `__actions.wave`, `__actions.punch` (the unmirrored
base), and `__actions.push_turn_over`. And its LED API is a different shape — see
[the LED section](#rgb-led).

## The runtime environment

Generated code runs with these already in scope — no import needed. **[Verified]** — no generator
ever emits an import for them:

| Name | What it is |
|---|---|
| `q` | **The quadruped.** The central motion object. |
| `car` | Board peripherals — `car.buzzer`, `car.led`, `car.motion` |
| `led` | The RGB LED (also reachable as `car.led`) |
| `sleep(s)` | Sleep, seconds. Global — *not* `time.sleep`. |
| `print(...)` | Logs back to the editor console |

Modules you **do** import (the generators emit these):

```python
import actions    # the action library
import imu        # inertial sensing
import process    # the agent framework
import _led       # LED animations
```

## Motion

### The two primitives

Everything reduces to these. **[Verified]**

```python
q.play(frames, [count], dly=0.1)
```

Plays an action. `frames` comes from an `actions.*` call or `q.f(...)`. The optional positional
second argument is a **repeat count** (used by walk/bound). `dly` is the inter-frame delay in
seconds; every generator passes `dly=0.1` except the instantaneous-pose block, which omits it.

```python
q.f(d1, d2, d3, d4, dur, ofs=..., x=..., y=..., z=..., auto=...)
```

Builds a **single frame**: four servo positions plus a duration.

| Param | Meaning |
|---|---|
| `d1`–`d4` | The four leg servos. **[Verified — hardware]** GPIO pins `39, 38, 41, 40`; likely degrees, range `-180..180`. See [Servo calibration](#servo-calibration--real-values-from-hardware). |
| `dur` | Transition duration in seconds. `0` = instantaneous. |
| `ofs` | Posture offset — one of the `actions.ofs_*` constants, or a raw 4-list |
| `x` | Direction multiplier. `-1` reverses. **[Inferred]** from `x=-1` meaning backward throughout. ⚠️ Opposite meaning in Gen A — see [above](#two-api-generations). |
| `y` | **Left/right mirror flag.** `y=1` mirrors to the right. **[Inferred]** — see below. |
| `z` | **[Unknown]** — appears only as `z=1` |
| `auto` | **[Unknown]** — appears only as `auto=1` in the agent walk |

### What `y=1` means

Gen A resolves this. **[Verified]** — in the `/kt2/` editor, left/right pairs are **one function
plus a mirror flag**:

```python
__actions.punch(kt2)            # left punch
__actions.punch(kt2, y=1)       # right punch
__actions.left_split(kt2)       # left chop
__actions.left_split(kt2, y=1)  # right chop
__actions.c_pivot(kt2, n)       # turn left
__actions.c_pivot(kt2, n, y=1)  # turn right
```

So **`y=1` = "do it on the right side"**. **[Inferred]**, but strongly: it's the consistent
mechanism across three unrelated action families in Gen A.

This explains the oddity in Gen B, where `right_punch` passes a seemingly pointless `y=1`:

```python
q.play(actions.left_punch(q), dly=0.1)         # no y
q.play(actions.right_punch(q, y=1), dly=0.1)   # y=1 — vestigial mirror flag
```

**[Inferred]:** Gen B wrapped the mirrored calls into named `left_*`/`right_*` functions but left
the `y=1` in place on `right_punch` — either vestigial, or because `right_punch` is still a thin
mirror wrapper. Gen B's other right-side actions (`right_kick`, `right_split`, `right_flip`) pass
**no** `y`, which makes `right_punch` the odd one out and favours "vestigial".

**Leg order is `d1..d4` = left-front, right-front, left-rear, right-rear.** **[Inferred]** — from
the vendor's own label list, in this order: 左前腿 (Left Front Leg), 右前腿 (Right Front Leg),
左后腿 (Left Rear Leg), 右后腿 (Right Rear Leg).

### Servo calibration — real values from hardware

**[Verified — hardware, 2026-07-17]** — read from `/my/bot/user_config.json` on a physical unit
(via `GET /file?path=...`; see [device-api.md](device-api.md)):

```json
{
  "servo_pins":      [39, 38, 41, 40],
  "servo_dirs":      [-1, 1, -1, 1],
  "servo_range":     [-180, 180],
  "servo_degs_up":   [99, 94, -83, -100],
  "servo_degs_down": [-92, -99, 110, 89],
  "servo_corrs":     [3.5, -2.5, 13.5, -5.499992],
  "servo_k":         [1.061111, 1.072222, 1.072222, 1.05],
  "stylized_action": "kungfu"
}
```

This is a genuine, previously-undocumented file, and it resolves most of what was `[Unknown]`
about `q.f()`'s arguments:

- **`servo_pins: [39, 38, 41, 40]`** — the actual GPIO pins driving the four leg servos, in
  `d1..d4` order. No pinout for the KT2 existed anywhere before this.
- **`servo_dirs: [-1, 1, -1, 1]`** — alternating sign, confirming the mirrored left/right
  convention that was only **[Inferred]** before, from `ofs=[-75, -75, 75, 75]` in the agent walk
  (see [agent.md](agent.md#agent-walk)). Front/rear pairing and left/right mirroring both check
  out against this.
- **`servo_range: [-180, 180]`** — `d1..d4` values are very likely **degrees** in this range.
  Not 100% pinned down (this is the *installation* range, not necessarily the *runtime* clamp),
  but it's now evidence rather than a guess. Units were previously `[Unknown]`.
- **`servo_degs_up` / `servo_degs_down`** — per-servo calibrated target angles for "head up" and
  "head down" poses. This is almost certainly the calibration data behind `actions.ofs_head_up` /
  `actions.ofs_head_down`, though I did not read the compiled `actions.mpy` to confirm the constant
  values match exactly — **[Inferred]**, strongly, but not proven byte-for-byte.
- **`servo_corrs`** and **`servo_k`** — per-servo trim offset and scale factor. Individual-unit
  calibration data (from `/b4/calibration/`, the "安装校准" installation-calibration app), not
  firmware constants — expect these to differ between physical units.
- **`"stylized_action": "kungfu"`** — a personality/style setting with no prior mention anywhere.
  Lines up with the "Kung Fu Basics" (功夫基础) category label on the action blocks, previously
  read only as a menu heading. Its effect on behaviour is **[Unknown]** — not explored further.

This file lives at `/my/bot/user_config.json`, discovered via `/data/dir/list` on `/my` — see the
filesystem table in [device-api.md](device-api.md#on-device-filesystem), now updated with this path.

`q.frame(...)` also exists, used by the agent walk. Its relationship to `q.f(...)` is **[Unknown]**.

### Posture offsets

Named constants on `actions`. **[Verified]**

| Constant | Vendor's English label |
|---|---|
| `actions.ofs_stand` | Stand |
| `actions.ofs_stand_low` | Get Down (趴下) |
| `actions.ofs_head_down` | Bow Down (低头) |
| `actions.ofs_head_up` | Raise Head (仰头) |

Apply one as a pose, or pass it to `walk()` to change gait posture:

```python
q.play(q.f(0, 0, 0, 0, ofs=actions.ofs_stand), dly=0.1)      # stand
q.play(q.f(0, 0, 0, 0), dly=0.1)                             # horizontal (no ofs)
q.play(actions.walk(q, ofs=actions.ofs_head_up), 5, dly=0.1) # walk with head up
```

### Walking and turning

```python
actions.walk(q, x=1, ofs=actions.ofs_stand)   # gait generator; x=-1 walks backward
actions.c_pivot(q, n)                          # turn; n<0 turns the other way
actions.one_key_reset(q)                       # reset to neutral
actions.stand(q)                               # stand up
```

Note the asymmetry: `walk` produces frames for `q.play`, but **`c_pivot` and `one_key_reset` are
called directly** — they are not wrapped in `q.play`. **[Verified]**

```python
q.play(actions.walk(q, ofs=actions.ofs_stand), 5, dly=0.1)          # forward 5 steps
q.play(actions.walk(q, x=-1, ofs=actions.ofs_stand), 5, dly=0.1)    # backward 5 steps
actions.c_pivot(q, 3)                                               # turn left 3
actions.c_pivot(q, -1 * 3)                                          # turn right 3
```

The vendor emits `-1*n` literally for "turn right" rather than negating the constant.

### Naming and what actually exists

**[Verified — hardware, 2026-07-17]** The generators document far more actions than actually exist on
one tested unit. Confirmed working via `q.play(...)`:

```python
# Tested and confirmed working:
q.play(actions.left_kick(q), dly=0.1)
q.play(actions.right_kick(q), dly=0.1)
q.play(actions.left_punch(q), dly=0.1)
q.play(actions.right_punch(q, y=1), dly=0.1)
q.play(actions.left_flip(q), dly=0.1)
q.play(actions.right_flip(q), dly=0.1)
```

Confirmed working without `q.play(...)`:

```python
# Tested and confirmed working:
actions.one_key_reset(q)
actions.walk(q, x=1, ofs=actions.ofs_stand)  # returns frames for q.play(...)
actions.c_pivot(q, 1)                         # execute directly, no q.play()
```

**Confirmed NOT on this device** (documented in generators, `AttributeError` when called):

- `stand` — 恢复站立
- `sit` — *(not in generators, but expected)*
- `dance` — *(not in generators, but expected)*
- `play_dead` / `faint` — 晕倒
- `left_chop`, `right_chop` / `left_split`, `right_split` — 左/右劈掌
- (and likely the entire "named sequence" family: `shake_hand`, `spring`, `xtrans`, `seesaw`,
  `bound`, `push`, `pounce`, `turn_over`, `back_flip`, `folded_flip`, `double_flip`, `slide`,
  `throw`)

**Unknown** (documented in generators, not tested or unclear):

- `bark`, and all other named sequences in the table below (very few actions actually exist on this
  device — it's a **major firmware subset**).

This suggests the actual `/sys/bot/actions.mpy` is:
1. **A drastically smaller subset** than the generators describe (far fewer than the ~30 actions
   documented)
2. **Firmware-specific** — different builds may have different action libraries
3. **Possibly older** — generators may be from a newer firmware version with actions not yet added to
   this hardware

The table below lists all actions from the generators; treat **all but the six confirmed kicks/punches/flips and
the three walk/pivot/reset functions as firmware-variant [Unknown]** rather than universally available.
Not reliable to depend on.

### The action library

All below are from the generators **[Verified]**. Unless noted, the call is
`q.play(actions.<name>(q), dly=0.1)`.

English names are the vendor's own where they publish one; ones I translated are marked *(mine)*.

| `actions.*` | Vendor English | Chinese |
|---|---|---|
| `stand` | Stand | 恢复站立 |
| `walk` | *(gait — see above)* | 前进 |
| `c_pivot` | Turn Left / Turn Right | 左转 / 右转 |
| `one_key_reset` | One-Key Reset | 一键复位 |
| `bark` | Bark | 狗叫 |
| `shake_hand` | Handshake | 握手 |
| `spring` | Spring | 弹簧 |
| `xtrans` | Forward and Backward | 前后 |
| `seesaw` | Pitch | 俯仰 |
| `bound` | *jump (mine)* | 小跳 |
| `faint` | *faint / play dead (mine)* | 晕倒 |
| `left_kick` / `right_kick` | *left / right kick (mine)* | 左踢 / 右踢 |
| `push` | Push | 推 |
| `push(q, x=-1)` | Push Back | 向后推 |
| `pounce` | Pounce | 扑 |
| `pounce(q, x=-1)` | Back Pounce | 后扑 |
| `turn_over` | Lift | 掀 |
| `turn_over(q, x=-1)` | Back Lift | 后掀 |
| `flip` | Flip | 翻 |
| `back_flip` | Back Flip | 后翻 |
| `left_flip` / `right_flip` | Left Flip / Right Flip | 左翻 / 右翻 |
| `left_back_flip` / `right_back_flip` | Left / Right Backward Flip | 左后翻 / 右后翻 |
| `folded_flip` | Fold and Flip | 折叠翻 |
| `double_flip` | Double Flip | 连翻 |
| `left_punch` | Left Punch | 左冲拳 |
| `right_punch(q, y=1)` | Right Punch | 右冲拳 |
| `left_split` / `right_split` | Left Chop / Right Chop | 左劈掌 / 右劈掌 |
| `slide` | Slide | 滑 |
| `throw` | Throw | 抛 |

Two quirks, both **[Verified]**:

- **`right_punch` passes `y=1` but `left_punch` passes nothing.** Explained by the mirror flag —
  see [What `y=1` means](#what-y1-means).
- **`bound` hardcodes a repeat of 3**: `q.play(actions.bound(q), 3, dly=0.1)`.

**Gen A has three actions missing from this table** **[Verified]** — `__actions.wave(kt2)`,
`__actions.punch(kt2)` (the unmirrored base of left/right punch), and
`__actions.push_turn_over(kt2)`. Whether Gen B dropped them or merely stopped exposing blocks for
them is **[Unknown]** — the underlying `/sys/bot/actions.py` may still define them.

### Compound gaits

Some blocks emit **two** statements — a walk followed by a corrective pose. **[Verified]**

```python
# "Look Up and Move Forward" (仰头前进)
q.play(actions.walk(q, ofs=actions.ofs_head_up), 5, dly=0.1)
q.play(q.f(0, 0, 0, 0, 0.1, ofs=actions.ofs_head_down, x=-1), dly=0.1)
```

Note the trailing frame uses the **opposite** offset (`head_down` closing a `head_up` walk). This
looks intentional — a settle/counterpose — but it is **[Unknown]** why.

There is a likely **vendor bug** here. The two "look down" blocks are crossed **[Verified]**:

```python
# block: actions_walk_ofs_head_down  ("Look Down and Move Forward")
q.play(actions.walk(q, ofs=actions.ofs_head_down), cnt, dly=0.1)     # ✓ head_down

# block: actions_walk_back_ofs_head_down  ("Look Down and Move Backward")
q.play(actions.walk(q, x=-1, ofs=actions.ofs_head_up), cnt, dly=0.1) # ✗ head_UP?
```

The "look **down** and move backward" block walks with `ofs_head_up`. Its `head_up` counterpart is
symmetrically crossed (`actions_walk_back_ofs_head_up` uses `ofs_head_down`). Either the offset
names mean something non-obvious when walking backward, or the pairs got swapped. **[Unknown]** —
worth checking on hardware before copying.

## IMU (Advanced edition only)

```python
import imu
```

All **[Verified]**. Vendor's English descriptions.

### Orientation

| Call | Meaning | Range |
|---|---|---|
| `imu.get_r()` | Roll | -180°–180° |
| `imu.trans_r(imu.get_r())` | Roll, transformed | -90°–90° |
| `imu.get_p()` | Pitch | -90°–90° |
| `imu.get_y()` | Yaw | -180°–180° |
| `imu.reset_y()` | Reset yaw to zero | — |

### Acceleration — in **g**

| Call | Axis |
|---|---|
| `imu.get_ax()` | Forward/backward |
| `imu.get_ay()` | Left/right |
| `imu.get_az()` | Up/down |

`imu.get_ex()` / `get_ey()` / `get_ez()` are the same three **relative to the ground** — i.e.
gravity-compensated / earth-frame. **[Inferred]** from the label "Relative to Ground"; `e` for
"earth". **[Verified]** that they exist and are labelled that way.

### Angular velocity — degrees/second

`imu.get_gx()` (roll rate) · `imu.get_gy()` (pitch rate) · `imu.get_gz()` (yaw rate)

### A real bug in the IMU blocks

**[Verified]** — `imu_reset_rpy` is **defined twice** in `b4-advanced/imu/generators.js`. The
second definition silently overwrites the first:

```js
// First definition — honours a dropdown, emits car.motion.reset_rpy(...)
Blockly.Python['imu_reset_rpy'] = function (block) {
    var dropdown_name = block.getFieldValue('NAME');
    if (dropdown_name == "r")      code = "car.motion.reset_rpy(r=0)\n";
    else if (dropdown_name == "p") code = "car.motion.reset_rpy(p=0)\n";
    ...
};

// Second definition — same key. Wins. Ignores the dropdown entirely.
Blockly.Python['imu_reset_rpy'] = function (block) {
    return "imu.reset_y()\n";
};
```

**Consequence:** the reset block ignores its own dropdown and *always* emits `imu.reset_y()`,
resetting yaw regardless of whether you picked roll, pitch, or all three. If you need roll/pitch
reset, call `car.motion.reset_rpy(r=0)` / `(p=0)` / `()` directly — it appears to exist, since the
dead branch calls it, though it's **[Unknown]** whether that path still works.

## Buzzer

**[Verified]** — note these are on `car.buzzer`, not a bare module.

```python
car.buzzer.music('''1=''')          # play a tune string; '1=' is the "Hi" chirp
car.buzzer.hello()                  # boot sound
car.buzzer.fire()                   # fire-alarm sound
car.buzzer.mars(500, 2000, 0.02, 0.02, 15)   # "Martian language" noise
car.buzzer.freq(hz, seconds)        # tone at a frequency
car.buzzer.close()                  # stop
```

`freq()` is **asynchronous** — it returns immediately. The vendor's "play and wait" block emits a
manual sleep after it **[Verified]**:

```python
car.buzzer.freq(440, 0.5)
sleep(0.5)          # only emitted when the block's async flag is off
```

`mars()`'s five arguments are **[Unknown]**; the block hardcodes them, and always follows with
`sleep(0.5)`. The `music()` string grammar is **[Unknown]** beyond `'1='` — it's a numbered-notation
(简谱) dialect. Same string as the `/hw/buzzer/music` HTTP endpoint.

## RGB LED

**[Verified]**

```python
led.on(color, brightness)      # note: bare `led`
car.led.off()                  # note: car.led — the vendor is inconsistent here

import _led
_led.breathe(led, hex_color=0xFF0000, dur=2, interval=0.02, brightness_max=100)
_led.blink(led,   hex_color=0xFF0000, dur=2, interval=0.02, brightness=100)
_led.gradient(led, color1, color2, dur=2, interval=0.02, brightness=100)
```

Three things worth flagging, all **[Verified]**:

- **`led.on(...)` vs `car.led.off()`** — the on and off blocks disagree about the object path.
  Both presumably reach the same LED (**[Inferred]**: `led` is an alias of `car.led`), but the
  inconsistency is in the vendor's shipped code, not a transcription error.
- **The animation helpers take `led` as their first argument** — `_led` is a function library
  operating *on* the LED object, not a driver.
- **`breathe` uses `brightness_max`; `blink` and `gradient` use `brightness`.** Not a typo here —
  that's what they emit.

Colour is a hex int (e.g. `0xFF0000`). Brightness units are **[Unknown]**.

### Gen A's LED API is a different shape

**[Verified]** — the `/kt2/` editor emits a distinct, simpler LED interface:

```python
import __led
__led.on(color, brightness)
car.led.off()                       # same as Gen B
__led.breathe(color, dt=0.02)       # note: dt, and no led argument
__led.blink(color, dt)
__led.flow(__led.color_wheel)       # "flow" — no Gen B equivalent
__led.breathe(__led.color_wheel)
```

Three differences worth noting: the helpers **don't take the `led` object** as a first argument;
timing is a single **`dt`** rather than `dur`/`interval`/`brightness`; and Gen A adds
**`__led.flow()`** plus a **`__led.color_wheel`** constant, neither of which exists in Gen B.

## Control flow

The `control` category mostly wraps stock Python, with one KT2-specific detail. **[Verified]**

```python
sleep(seconds)
print(text)
```

**Loops get an injected `sleep(0.02)`:**

```python
# "repeat N times"
for i in range(n):
    <body>
    sleep(0.02)

# "loop forever"
while True:
    <body>
    sleep(0.02)
```

**[Inferred]** — this is a cooperative-yield so the MicroPython VM stays responsive (and so
`/py/vm/break` can interrupt). If you hand-write a tight loop with no sleep, expect it to be
harder to interrupt and potentially to starve the runtime. Worth imitating.

The "random task" block picks one of N branches:

```python
import random
idx = random.randint(0, n)      # note: inclusive upper bound — see below
if idx == 0:
    ...
elif idx == 1:
    ...
```

**Possible off-by-one [Verified]:** the generator emits `random.randint(0, cnt)` where `cnt` is the
branch count, but only emits branches `0..cnt-1`. Python's `randint` is inclusive on both ends, so
`idx == cnt` is reachable and matches no branch — that iteration silently does nothing. With 3
branches you'd get a 1-in-4 no-op.

## Math (Advanced edition only)

The whole category is two blocks. **[Verified]**

```python
-num          # "negate"
abs(num)      # "absolute value" — but see below
```

**The `abs` block is broken.** **[Verified]** — the generator does string concatenation without
parentheses:

```js
Blockly.Python['math_abs'] = function (block) {
    var num = Blockly.Python.valueToCode(block, 'number', Blockly.Python.ORDER_ATOMIC);
    var code = 'abs' + num;        // ← no parens
    return [code, Blockly.Python.ORDER_NONE];
};
```

With an atomic input, `valueToCode` returns bare `5`, so the block emits **`abs5`** — a
`NameError`, not a call. The sibling `math_minus_sign` block does the same concatenation but is
correct by luck, because `-` is valid prefix syntax where `abs` is not. **[Inferred]** the block
only works when its input happens to be parenthesized. Write `abs(x)` by hand instead.

## Label caveats

The vendor's own English catalog has at least one **mistranslation** **[Verified]**:

```js
Lang.Msg["前进"] = "Back and Forth";     // 前进 means "move forward"
Lang.Msg["后退"] = "Move Backward";      // correct
```

`actions_walk` (前进 / forward) is labelled **"Back and Forth"** in English. The generator is
unambiguous — it emits `actions.walk(q, ofs=...)` with no `x`, i.e. forward, while the backward
block passes `x=-1`. **Trust the generator, not the English label.** A separate block (`xtrans`,
前后) is genuinely "Forward and Backward".

Five actions have no vendor English at all — 恢复站立, 左踢, 右踢, 小跳, 晕倒. Those are my
translations, marked *(mine)* in the table above.
