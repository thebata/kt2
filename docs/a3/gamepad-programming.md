# Gamepad Programming (手柄编程)

> Translated from <https://guidan.com/a3/manual/gamepad/>

How to customise what a gamepad button does. The manual uses button **Y** as its worked example,
and shows the graphical route, the Python route, and how to restore defaults.

To start: in the gamepad view, tap the button you want to change and pick a programming mode.

## The naming contract — the key idea

A button maps to **functions named after the button and its state**. The runtime dispatches to a
function by name; you never register a callback explicitly.

```
<BUTTON>_1    # called when the button is PRESSED
<BUTTON>_0    # called when the button is RELEASED
```

So for button Y: define `Y_1` for press, `Y_0` for release. Define only `Y_1` and the action fires
on press and never stops — the press/release pair is what gives you "buzz while held":

> "This is the same as motor rotation: press to rotate, release to stop."

## Editing with graphical programming (用图形编程编辑)

1. **Go to graphical programming** when prompted.
2. **Write the function.** In the function category, pick the first block. Rename the function to
   `Y_1` — meaning "the function for button Y pressed" — then drag in the blocks to execute.
3. **Save the file.** File → Save. **Restart the board for changes to take effect.**
4. **Test.** Open the virtual gamepad and press Y; the new behaviour should be live.

To make a sound play while held and stop on release, add a second function `Y_0` (button Y
released) and drag in the corresponding blocks.

## Editing with Python (用Python编程编辑)

1. **Go to Python programming** when prompted.
2. **Write the functions.** Define `Y_1` for the press action and `Y_0` for the release action.
3. **Save, then restart the board** — same as the graphical route.

You can also view the generated Python for your blocks: in graphical programming, **File → View**.
Useful for learning the API the blocks are calling.

### Precedence — worth knowing

> **如果用图形编程和Python编程编辑了相同的按键，最终会以图形编程的更改为准。**
>
> If the **same button** is edited in both graphical and Python programming, the **graphical
> programming change wins.**

So Python edits to a button can be silently overwritten by a block definition for the same button.
If a Python handler mysteriously doesn't fire, check whether a block version of it exists.

## Restoring defaults (恢复默认功能)

In the button's edit dialog, choose **Restore default (恢复默认)**.

## Applying this to other buttons

The Y example generalises. Each button has two functions — `_1` for press, `_0` for release.

**The 8 standard buttons** — `A` `B` `X` `Y` `L1` `L2` `R1` `R2` — all work exactly this way:

```python
def A_1(): ...    # A pressed
def A_0(): ...    # A released
def R2_1(): ...   # R2 pressed
def R2_0(): ...   # R2 released
```

### The D-pad (十字键) is different

The D-pad is named **`CROSS`** and encodes *direction* in the numeric suffix rather than
press/release. Starting from the top and going **clockwise**, the eight directions are **0–7**.
**Release is 15.**

```python
def CROSS_0(): ...     # top direction pressed
def CROSS_1(): ...     # next direction clockwise pressed
...
def CROSS_7(): ...     # last direction pressed
def CROSS_15(): ...    # D-pad released  (any direction)
```

The physical layout, per the button diagram:

```
   7   0   1
   6       2
   5   4   3
```

Apart from the different suffixes, the workflow is identical to A/B/X/Y/L1/L2/R1/R2.

> Note the asymmetry: for normal buttons the suffix is a **state** (1 = down, 0 = up), but for
> `CROSS` the suffix is a **direction**, with a single sentinel `15` for release. There is no
> `CROSS_0` "released" — `CROSS_0` means *the top direction was pressed*.

## See also

[control.md](control.md) — the default button map, i.e. what these functions do before you
override them.
