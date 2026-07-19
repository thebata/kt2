# Xiaogui B4-KT2 (小龟机器狗游戏版) — Developer Reference

The **B4-KT2** is a pocket-sized **four-servo quadruped robot dog** from 小龟机器人 (Xiaogui
Robot / 杭州集步科技有限公司, Hangzhou Jibu Technology). Marketed as "a robot that fits in your
pocket, with 99 built-in games." Crowdfunded 2024.

Product page: <https://guidan.com/b4/> · Vendor catalog: <https://guidan.com/index/>

## ⚠️ Read this before trusting anything here

**The vendor publishes no manual for the KT2.** `/a3/manual/` is the only manual on the entire
site, and it is for a *different product* (see [../a3/](../a3/README.md)).

Everything in these pages was **reverse-engineered on 2026-07-17** from the vendor's own web
applications — their Blockly code generators, message catalogs, and JavaScript bundles. This is
strong evidence: the code generators *are* the source of truth for what the blocks emit, and the
English names are the vendor's own. But it is **inference from shipped code, not a documented
contract**, and it can change with any firmware or site update.

Provenance is marked throughout:

- **[Verified]** — read directly out of vendor code (a generator template, a message catalog).
  High confidence.
- **[Inferred]** — a conclusion drawn from that code. Reasonable, unverified against hardware.
- **[Unknown]** — a gap. Requires a device or vendor input to resolve.

**Update 2026-07-17:** a physical unit was reached on the local network and tested live —
buzzer, file reads, directory listing, and `POST /py` code execution all confirmed. Findings
verified against hardware are marked **[Verified — hardware]** rather than plain **[Verified]**.
Everything else below is still unverified vendor-code inference, as originally written.

## Contents

| Page | What's in it |
|---|---|
| [architecture.md](architecture.md) | How the apps, the vendor host, and the robot fit together |
| [device-api.md](device-api.md) | The robot's HTTP API and on-device filesystem |
| [python-api.md](python-api.md) | **The Python API — `actions`, `q`, `imu`, `led`, `car.buzzer`** |
| [gamepad.md](gamepad.md) | `GAMEPAD_*` button handler contract |
| [agent.md](agent.md) | The agent/`process` framework for autonomous behaviour |

## The 30-second version

The KT2 runs **MicroPython**. You program it in one of three ways:

1. **Blockly** (`/b4/blk/`) — blocks that generate MicroPython.
2. **Python** (`/apps/ide/`) — write MicroPython directly.
3. **HTTP** — `POST http://<device-ip>/py` with `code=<python>` executes arbitrary Python on the
   robot. This is the most useful entry point for external tooling. See
   [device-api.md](device-api.md).

The core motion API is a global **`q`** object (the quadruped) plus an **`actions`** module:

```python
import actions
q.play(actions.stand(q), dly=0.1)                          # stand up
q.play(actions.walk(q, ofs=actions.ofs_stand), 5, dly=0.1) # walk 5 steps
q.play(actions.bark(q), dly=0.1)                           # bark
actions.c_pivot(q, 3)                                      # turn left 3
q.play(q.f(0, 0, 0, 0, 0.5), dly=0.1)                      # raw 4-servo frame
```

Full details in [python-api.md](python-api.md).

## Editions — and two incompatible API generations

The `/b4/blk/` editor ships two toolbox configurations **[Verified]** — from
`/b4/blk/modules/config.json`:

| Edition | id | Categories |
|---|---|---|
| Basic (基础版) | `b4-basic` | actions, buzzer, led, agent, control, gamepad, custom_agent |
| Advanced (进阶版) | `b4-advanced` | the above **+ imu, math** |

Both generate the same underlying Python; Advanced simply exposes more blocks. The IMU category is
Advanced-only.

> ### ⚠️ But there is also a second, older editor with a *different API*
>
> `https://guidan.com/kt2/` is an unlinked standalone editor using **`kt2`/`__actions`** instead of
> **`q`/`actions`** — and its `x` parameter means the **opposite** thing. Same call, opposite
> direction.
>
> These docs describe the **`q`/`actions`** generation, which is newer and is what the product hub
> links to. **[Verified — hardware]** the one physical unit tested runs this generation — see
> [python-api.md § two API generations](python-api.md#two-api-generations) for the confirming
> transcript. Still unknown whether every KT2 unit does.

## Known gaps

1. **Two incompatible API generations exist.** One physical unit has been confirmed as Gen B
   (`q`/`actions`) — see the warning above — but whether that holds for all units is still
   **[Unknown]**.
2. **The action set on real hardware is a tiny fraction of what the generators document.** The
   compiled `/sys/bot/actions.mpy` has only ~9 working actions out of ~30 described. **[Verified — hardware, 2026-07-17]**
   - ✅ **Only these work**: left/right kick, left/right punch, left/right flip, walk, c_pivot, one_key_reset
   - ❌ **Don't exist**: stand, sit, dance, play_dead, chop, and likely all other "named sequences"
   
   This is not missing individual actions — it's a **major firmware capability gap**. The Blockly
   generators describe a much richer action library than the device actually has. This could be:
   (a) an older firmware on this device, (b) different firmware builds for different variants, or
   (c) generators aspirational from a planned but not-yet-shipped firmware. Whatever the cause,
   **only the nine confirmed actions are reliable** — everything else will `AttributeError`.
   
   See [python-api.md § Naming and what actually exists](python-api.md#naming-and-what-actually-exists).
3. **The `actions` and `imu` modules are precompiled bytecode on the device** (`/sys/bot/*.mpy`,
   confirmed **[Verified — hardware]**), on a firmware partition that the file-listing API doesn't
   even enumerate. There is no source to read. So the *signatures* in these docs are confirmed from
   Blockly call sites, but the *implementations*, exact parameter ranges, and return types stay
   **[Unknown]** — not because hardware access was missing, but because the API genuinely can't
   reach them. What real hardware access *did* resolve: actual servo GPIO pins, sign convention,
   and value range — pulled from a calibration config file instead. See
   [python-api.md § Servo calibration](python-api.md#servo-calibration--real-values-from-hardware).
4. **No official pinout or electrical specs are published** anywhere for the KT2. Servo GPIO pins
   are now known (see above); everything else about the board — power, other peripherals — is not.
5. **The 99 games are opaque** — `/b4/games/` is a launcher; the game logic is on the device.
6. **Not mined:** the `games`, `actions`, `calibration`, `agent-table`, `explorer`, `ide`,
   `devices`, `gamepad`, `boot-files`, `battery`, `settings` and `gamepad-editor` app bundles were
   downloaded and searched for API endpoints, but not read line-by-line. They may hold more.
7. **Also confirmed: `/py` is fire-and-forget, not blocking.** `POST /py` returned
   `{"status":"OK","msg":""}` almost instantly — far faster than a 5-step physical walk takes. The
   submitted code (walk, *then* `print()`) clearly kept running on the device after the HTTP
   response was already back. **[Inferred]** mechanism: `/py` acknowledges receipt/parse of the
   code and queues it for execution; it does not wait for the code to finish, even though the code
   itself runs synchronously/blocking on the device (the `print()` only reaches `/log` once the
   preceding `q.play(...)` call has physically finished). Confirmed by direct observation: a ~2s
   poll of `/log` came back empty; a ~5s poll caught the output. **Practical consequence: an HTTP
   200 from `/py` means "accepted," not "done"** — poll `/log` with real slack, especially for
   anything that moves the robot, and don't fire a second command assuming the first has finished.

### Vendor bugs found

All **[Verified]** in shipped code:

| Bug | Where |
|---|---|
| `imu_reset_rpy` defined twice; dropdown ignored | [python-api.md](python-api.md#a-real-bug-in-the-imu-blocks) |
| `math_abs` emits `abs5` — missing parens | [python-api.md](python-api.md#math-advanced-edition-only) |
| `random.randint(0, n)` inclusive → silent no-op branch | [python-api.md](python-api.md#control-flow) |
| "Look down/up + walk backward" blocks pass crossed offsets | [python-api.md](python-api.md#compound-gaits) |
| 前进 ("forward") mistranslated as "Back and Forth" | [python-api.md](python-api.md#label-caveats) |
| "Wait for being flipped" emits `wait_backdown()`, a duplicate | [agent.md](agent.md#wait-calls-blocking) |
