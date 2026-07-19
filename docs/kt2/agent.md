# KT2 Agent Framework (智能体)

> **[Verified]** — from `/b4/blk/modules/b4-{basic,advanced}/{agent,custom_agent}/generators.js`.
> See [README.md](README.md) for provenance.

"Agent" (智能体) is the vendor's term for autonomous behaviour — the robot reacting to how it's
handled rather than to a gamepad. There are **two distinct mechanisms** with confusingly similar
names.

| Category | Vendor English | Mechanism |
|---|---|---|
| `agent` | **Interaction** | An `imu`-driven poll loop |
| `custom_agent` | **Agent** | An event/check/callback registration |

## 1. Interaction — the poll loop

The `agent` category builds a `while True` loop that samples the IMU and dispatches on
its state. **[Verified]**

```python
import imu

ds_ax = imu.DataStream()
ds_ay = imu.DataStream()
ds_az = imu.DataStream()
while True:
    ds_ax.add(imu.get_ax())
    ds_ay.add(imu.get_ay())
    ds_az.add(imu.get_az())
    if imu.is_patted():
        <your blocks>
        _agent_reset(ds_ax, ds_ay, ds_az)
        continue
    if imu.is_shaken():
        ...
        _agent_reset(ds_ax, ds_ay, ds_az)
        continue
    sleep(0.02)
```

Three things to copy if you hand-write this **[Verified]**:

- **`imu.DataStream()`** accumulates a rolling series per axis. Each condition block re-samples all
  three every iteration.
- **After a branch fires, the generator emits `_agent_reset(...)` then `continue`** — the streams
  are cleared so a single gesture doesn't retrigger. `_agent_reset` is emitted as a helper that
  sets `.dataset = []` on each stream.
- **`sleep(0.02)`** closes the loop — the same cooperative yield used everywhere else.

### State predicates (non-blocking)

Return a bool. **[Verified]** — English is the vendor's.

| Call | Meaning |
|---|---|
| `imu.is_horizontal()` | Horizontal |
| `imu.is_backup()` | Back facing up |
| `imu.is_backdown()` | Back facing down |
| `imu.is_patted()` | Back patted |
| `imu.is_shaken()` | Shaken |
| `imu.is_flicked()` | Head tapped/flicked |
| `imu.is_static()` | Still |
| `imu.is_front_up()` | Front lifted |
| `imu.is_back_up()` | Rear lifted |
| `imu.is_left_up()` | Left side lifted |
| `imu.is_right_up()` | Right side lifted |
| `imu.is_p_on()` | **[Unknown]** — "p" is unexplained; pitch-based, probably |

> **Careful — `is_backup()` and `is_back_up()` are different things.** `is_backup()` is "the
> robot's *back* is facing *up*" (背朝上). `is_back_up()` is "the *rear* has been lifted"
> (后面被抬起). One underscore apart, unrelated meanings. **[Verified]** — both exist, both are
> labelled as above by the vendor.

### Wait calls (blocking)

Same conditions, but they block until satisfied. **[Verified]**

`imu.wait_backup()` · `imu.wait_backdown()` · `imu.wait_pat()` · `imu.wait_shake()` ·
`imu.wait_flick()` · `imu.wait_static()` · `imu.wait_move()` · `imu.wait_front_up()` ·
`imu.wait_back_up()` · `imu.wait_left_up()` · `imu.wait_right_up()` · `imu.wait_p_on()` ·
`imu.wait_p_off()` · `imu.wait_r_on()` · `imu.wait_r_off()`

`wait_r_on` / `wait_r_off` have no exposed block — **[Inferred]** roll-axis counterparts of the
`p_on`/`p_off` (pitch) pair.

**Vendor quirk [Verified]:** the "wait for being flipped" block (等待被翻面, `agent_wait_turn_over`)
emits **`imu.wait_backdown()`** — identical to the "wait for back facing down" block. Either
deliberate aliasing or a copy-paste slip. **[Unknown]** which.

### Process — sequential steps

The Advanced `agent_process` block builds a step machine. **[Verified]**

```python
import process

def step0(game):
    <blocks>

def step1(game):
    <blocks>

game = process.Process(step0, step1)
game.start(loop=1)
```

Each step takes a `game` handle. `process.Process(*steps)` takes the step functions varargs;
`start(loop=1)` runs them. What `game` exposes, how a step advances, and what `loop` accepts are
all **[Unknown]** — `process` lives on the device.

## 2. Custom Agent — event registration

The `custom_agent` category is a different, more declarative model: you define a **check** and a
**callback**, and register them against an event. **[Verified]**

```python
def check(state, g):
    if state["collision"]:
        return True
    else:
        return False

def callback(q, t, state, g):
    <blocks>
```

The registration call is **`agent.register(event, check, callback, priority)`** — but note it is
**commented out** in the shipped generator **[Verified]**:

```js
// Blockly.Python.definitions_["custom_agent_register"] = "agent.register(event, check, callback, priority)";
```

So the blocks emit `check` and `callback` definitions but **never emit the registration**.
**[Inferred]**: either the runtime auto-discovers functions named `check`/`callback`, or the
registration happens elsewhere (the `/b4/agent-table/` app writes `/my/agent_*` and
`/my/_startup.py`, so probably there). The signature `agent.register(event, check, callback,
priority)` is the vendor's own text, so it is real — but **whether you're meant to call it
yourself is [Unknown]**.

### Signatures

| Name | Params |
|---|---|
| `check(state, g)` | → `bool`. Decides whether the agent fires. |
| `callback(q, t, state, g)` | Runs the behaviour. `q` = quadruped, `t` = **[Unknown]** (time?) |

### `state` and `g`

- **`state`** — the current sensor snapshot. Only confirmed key: **`state["collision"]`**
  (碰撞 / Collision). **[Verified]**
- **`g`** — a **shared dict** across agents (共享数据 / "Shared Data"). **[Verified]**

```python
g["key"]                            # read
g["key"] = value                    # write
if "key" not in g:                  # "if there is no shared data, then let it equal"
    g["key"] = value
```

That last pattern is a first-run initialiser — the vendor gives it a dedicated block
(`custom_agent_set_g_once`).

The toolbox also labels **电量 / "Battery Level"** and **方向 / "Direction"** in this category,
implying more `state` keys. Their exact names are **[Unknown]**.

### Agent walk

The one motion block in this category **[Verified]**:

```python
q.play(q.frame(*actions.t_walk(25, 25, 25, 25, t, 0.4), 0,
               ofs=[-75, -75, 75, 75], x=<dir>, y=1, z=1, auto=1))
```

Everything except `x` is hardcoded by the block. Notable:

- **`actions.t_walk(...)`** — a gait generator distinct from `actions.walk()`, returning something
  splatted into `q.frame`. **[Unknown]** what its four `25`s and `0.4` mean; `t` is the callback's
  second parameter, so the gait is **time-parameterised** — consistent with `t` being a clock.
  **[Inferred]**
- **`ofs=[-75, -75, 75, 75]`** — a raw 4-element offset instead of an `actions.ofs_*` constant.
  This was the original evidence for the mirrored left/right sign convention, since confirmed
  directly against hardware — a real unit's `servo_dirs` calibration is `[-1, 1, -1, 1]`, the same
  alternating pattern. See [python-api.md § Servo calibration](python-api.md#servo-calibration--real-values-from-hardware).
- **`q.frame(...)`**, not `q.f(...)`. The two coexist; their relationship is **[Unknown]**.

## Where agents live

The `/b4/agent-table/` app manages these, writing **[Verified]**:

- `/my/_startup.py` — startup script
- `/my/agent_*` — per-agent files

See [device-api.md](device-api.md#on-device-filesystem).
