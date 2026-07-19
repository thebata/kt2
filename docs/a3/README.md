# Xiaogui A3 (小龟A3) — Manual, translated to English

> # ⚠️ This is NOT the KT2
>
> **The A3 is a different product from the B4-KT2 that this project targets.** The A3 is a
> **Mecanum-wheel car**; the KT2 is a **four-servo quadruped dog**. Different chassis, different
> board, different API, different gamepad handler names.
>
> **Nothing on these pages applies to the KT2.** Concretely:
>
> | | A3 (these docs) | KT2 ([../kt2/](../kt2/README.md)) |
> |---|---|---|
> | Motion | `move(x, y, z, T)` | `q.play(actions.walk(q, …), n, dly=0.1)` |
> | Gamepad press | `Y_1` | `GAMEPAD_Y_1` |
> | D-pad | `CROSS_0` … `CROSS_15` | `GAMEPAD_HAT_0` … `GAMEPAD_HAT_15` |
> | Pinout | [pins.md](pins.md) — **A3 board only** | not published |
>
> **Never use the A3 pinout for KT2 wiring.** Using A3 handler names on a KT2 fails silently —
> the handlers simply never fire.
>
> These pages are kept because they are the vendor's **only** published documentation, and they
> usefully explain the shared ecosystem: Mixly, MicroPython on ESP32, and the `.bpy`/`.py`
> save model. For KT2 work, go to **[../kt2/README.md](../kt2/README.md)**.

English translation of the official 小龟A3 ("Xiaogui A3" / "Little Turtle A3") robot manual,
published at <https://guidan.com/a3/manual/>. Captured 2026-07-17.

The A3 is a Mecanum-wheel robot chassis built on an **ESP32-S3**, shipping with three
programming surfaces: Mixly (block/graphical), MicroPython, and XiaoguiOS.

## Contents

| Page | Source | What's actually in it |
|---|---|---|
| [Overview](overview.md) | `/manual/` | Navigation only |
| [First use](first-use.md) | `/manual/start/` | Video link only |
| [Control & buttons](control.md) | `/manual/control/` | **Default gamepad button map** |
| [Graphical programming (Mixly)](graphical-programming.md) | `/manual/mixly/` | Links to Mixly's own docs |
| [Python programming](python.md) | `/manual/python/` | **The `move()` motion API — the main reference** |
| [MicroPython](micropython.md) | `/manual/micropython/` | Links to upstream MicroPython docs |
| [Gamepad programming](gamepad-programming.md) | `/manual/gamepad/` | **Button→function naming contract** |
| [Pin reference](pins.md) | `/manual/pins/` | **Full board pinout** |
| [Networking](networking.md) | `/manual/connect/` | Online control page |

## Read this first

The upstream manual is **thin**. Most pages are a paragraph plus a Bilibili video link.
Only three pages carry information you can actually build against:

- **[python.md](python.md)** — the `move(x, y, z, T)` chassis API. This is the one interface
  the vendor says you need to memorize.
- **[pins.md](pins.md)** — the board pinout, transcribed from the vendor's diagram image.
- **[gamepad-programming.md](gamepad-programming.md)** — how button handlers are named and
  dispatched (`Y_1` / `Y_0` / `CROSS_0`…).

Everything substantive that exists only as a video is **not** captured here — the videos were
not transcribed. Where the manual's own content is missing or illegible, the pages below say so
explicitly rather than guessing.

## Conventions used in these translations

- Original Chinese terms are kept in parentheses on first use, so you can search the upstream
  docs and the Mixly UI.
- Blocks marked **[Not in source]** flag information the upstream manual omits or renders
  illegibly. These are gaps in the vendor documentation, not in this translation — do not
  treat them as verified facts.
- Blocks marked **[Inferred]** are conclusions drawn from the source rather than stated by it.
  They are reasonable but unverified against hardware.
- Code examples are reproduced verbatim; only the comments are translated.

## Known gaps in the upstream documentation

These are real holes in the vendor's own material, worth knowing before you rely on the docs:

1. **Motor pins M3, M5, M7 are incomplete.** The pinout diagram prints e.g. `IO14 /` with the
   second pin of the pair simply absent. Verified by zooming the source image — it is not a
   capture artifact. See [pins.md](pins.md).
2. **The UART header's third pin is not printed** (`IO0 / IO44 /`).
3. **`car.hcsr04()` appears in an example but is never documented.** No import, no module
   reference, no list of what else `car` exposes. The `move()`/`stop()` page implies `move` is
   the whole interface, which the example contradicts.
4. **No documented API surface beyond `move()`/`stop()`** — nothing for the buzzer, RGB LED, IMU,
   or servos, despite all four being on the board.
5. **Sensor/servo port pin ordering is ambiguous** — see the caveats in [pins.md](pins.md).

## Source

Upstream manual (Chinese, MkDocs/ReadTheDocs): <https://guidan.com/a3/manual/>
Vendor site: <https://guidan.com/>
Online control page: <http://guidan.com/a3box/>
