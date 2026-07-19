# KT2 Gamepad Programming

> **[Verified]** — from `/b4/blk/modules/b4-advanced/gamepad/{generators,blocks,index.xml}` and
> the vendor's English message catalog. See [README.md](README.md) for provenance.

## The naming contract

Gamepad handlers are **functions named after the button and its state**. The runtime dispatches by
name — you never register a callback.

```python
def GAMEPAD_<BUTTON>_1():    # pressed
    ...

def GAMEPAD_<BUTTON>_0():    # released
    ...
```

> ### ⚠️ This differs from the A3
>
> If you have seen the [A3 manual](../a3/gamepad-programming.md), note that the KT2 prefixes every
> handler with `GAMEPAD_` and calls the D-pad **`HAT`**, not `CROSS`:
>
> | | A3 | **KT2** |
> |---|---|---|
> | Button Y pressed | `Y_1` | **`GAMEPAD_Y_1`** |
> | D-pad up | `CROSS_0` | **`GAMEPAD_HAT_0`** |
> | D-pad released | `CROSS_15` | **`GAMEPAD_HAT_15`** |
>
> A3 handler names will not fire on a KT2.

Handlers are saved to `/my/gamepad/gamepad_config.py` (with the Blockly source alongside at
`gamepad_config.bpy`). **[Inferred]**, by analogy with the A3: **save, then reboot the board** for
changes to take effect.

## The full handler set

All 33 confirmed **[Verified]** — extracted from the generator definitions.

### Face buttons

`GAMEPAD_A_1` / `GAMEPAD_A_0` · `GAMEPAD_B_1` / `GAMEPAD_B_0` ·
`GAMEPAD_X_1` / `GAMEPAD_X_0` · `GAMEPAD_Y_1` / `GAMEPAD_Y_0`

### Shoulder buttons (背键 / "Back Buttons")

`GAMEPAD_L1_1` / `GAMEPAD_L1_0` · `GAMEPAD_L2_1` / `GAMEPAD_L2_0` ·
`GAMEPAD_R1_1` / `GAMEPAD_R1_0` · `GAMEPAD_R2_1` / `GAMEPAD_R2_0`

### Function keys

`GAMEPAD_SELECT_1` / `GAMEPAD_SELECT_0` · `GAMEPAD_START_1` / `GAMEPAD_START_0`

### D-pad — `HAT`

The suffix is a **direction**, not a state. Eight positions, **0 at the top, numbered clockwise**,
with **15 meaning released**.

| Handler | Direction | Has a block? |
|---|---|---|
| `GAMEPAD_HAT_0` | **Up** (上) | ✅ |
| `GAMEPAD_HAT_1` | Upper right | ❌ generator only |
| `GAMEPAD_HAT_2` | **Right** (右) | ✅ |
| `GAMEPAD_HAT_3` | Lower right | ❌ generator only |
| `GAMEPAD_HAT_4` | **Down** (下) | ✅ |
| `GAMEPAD_HAT_5` | Lower left | ❌ generator only |
| `GAMEPAD_HAT_6` | **Left** (左) | ✅ |
| `GAMEPAD_HAT_7` | Upper left | ❌ generator only |
| `GAMEPAD_HAT_15` | **Released** (松开) | ✅ |

```
   7   0   1
   6       2
   5   4   3
```

**Worth knowing:** the four diagonals (1, 3, 5, 7) have **working code generators but no blocks in
the toolbox** — `index.xml` only lists 0/2/4/6/15. **[Verified]**. The cardinal labels are the
vendor's own (上/右/下/左); the diagonal meanings are **[Inferred]** from the clockwise numbering.

So diagonals are reachable **only from Python**, by defining `GAMEPAD_HAT_1` yourself. Whether the
firmware actually emits diagonal values is **[Unknown]** — the generators exist, which is
suggestive but not proof.

### Joysticks — these take arguments

Unlike every other handler, joystick handlers **receive the stick position**. **[Verified]**

```python
def GAMEPAD_JOYSTICK_L_1(x, y):     # left stick moved
    ...

def GAMEPAD_JOYSTICK_R_1(x, y):     # right stick moved
    ...

def GAMEPAD_JOYSTICK_L_0():         # released — no args
    ...
```

The vendor's blocks don't hand you `x`/`y` raw; they bucket the vector into a direction using two
globals — `vector2dir4` and `vector2dir8` **[Verified]**:

```python
# 4-direction variant
def GAMEPAD_JOYSTICK_L_1(x, y):
    dir_l = vector2dir4(x, y)
    if dir_l == 0:
        <up>
    elif dir_l == 1:
        <right>
    elif dir_l == 2:
        <down>
    elif dir_l == 3:
        <left>

# 8-direction variant
def GAMEPAD_JOYSTICK_L_1(x, y):
    dir_l = vector2dir8(x, y)
    if dir_l == 0:
        ...
    elif dir_l == 1:      # ... through 7
```

`vector2dir4(x, y)` → `0..3`; `vector2dir8(x, y)` → `0..7`. Both are **globals injected by the
runtime** — no generator emits an import for them. **[Verified]**

The units and range of `x`/`y` are **[Unknown]**. The direction indices are **[Inferred]** to
follow the same clockwise-from-top convention as the HAT, since the 4-way generator maps its
branches onto the 8-way block's slots 0/2/4/6 — exactly the cardinal positions.

Both stick variants emit a function with the **same name** (`GAMEPAD_JOYSTICK_L_1`), so the 4-way
and 8-way blocks are mutually exclusive — using both for one stick means one silently wins.
**[Inferred]**

## Example

```python
import actions

def GAMEPAD_A_1():
    q.play(actions.bark(q), dly=0.1)

def GAMEPAD_Y_1():
    car.buzzer.freq(880, 0.2)

def GAMEPAD_Y_0():
    car.buzzer.close()

def GAMEPAD_HAT_0():
    q.play(actions.walk(q, ofs=actions.ofs_stand), 3, dly=0.1)

def GAMEPAD_HAT_4():
    q.play(actions.walk(q, x=-1, ofs=actions.ofs_stand), 3, dly=0.1)

def GAMEPAD_HAT_2():
    actions.c_pivot(q, -1 * 3)      # right

def GAMEPAD_HAT_6():
    actions.c_pivot(q, 3)           # left

def GAMEPAD_JOYSTICK_L_1(x, y):
    d = vector2dir4(x, y)
    if d == 0:
        q.play(actions.walk(q, ofs=actions.ofs_stand), 1, dly=0.1)
    elif d == 2:
        q.play(actions.walk(q, x=-1, ofs=actions.ofs_stand), 1, dly=0.1)
```

The press/release pair is what gives you "do X while held" — see `GAMEPAD_Y_1`/`GAMEPAD_Y_0`
above. Define only the `_1` and the buzzer never stops.

## Accessibility / "Toggle Execution" blocks

The toolbox has a 辅助功能 ("Accessibility Features") group with **Toggle Execution** (切换执行),
**Increment** (递增), and **Decrement** (递减) blocks, parameterised by Index / Initial Value /
Maximum / Minimum / Task / Change Each Time. **[Verified]** that they exist and are labelled this
way; what they emit is **[Unknown]** — not chased down.
