# Documentation

Vendor documentation for 小龟机器人 (Xiaogui Robot) hardware, translated and reverse-engineered
into English. Captured 2026-07-17.

## [kt2/](kt2/README.md) — **B4-KT2 robot dog** ← this project's target

The four-servo quadruped "robot dog, game edition." Reverse-engineered from the vendor's web
applications, because **no manual exists** for this product.

Start at [kt2/README.md](kt2/README.md). The two pages that matter most:

- [kt2/python-api.md](kt2/python-api.md) — the `actions` / `q` / `imu` / `led` / `car.buzzer` API
- [kt2/device-api.md](kt2/device-api.md) — the robot's HTTP API, including `POST /py` to run
  arbitrary Python on it

## [a3/](a3/README.md) — A3 creation box ⚠️ **different product**

An English translation of the vendor's published A3 manual. **The A3 is a Mecanum-wheel car, not
the KT2 dog.** Its API, pinout, and gamepad handler names are all different and **do not apply to
the KT2**.

Kept because it's the vendor's only real documentation and is useful for understanding the shared
ecosystem (Mixly, MicroPython, the app architecture). **Do not use its pinout or API for KT2 work.**

## Product family

For orientation — from the vendor catalog at <https://guidan.com/index/> **[Verified]**:

| Product | Name | What it is | Page |
|---|---|---|---|
| **B4-KT2** | 小龟机器狗游戏版 | **Pocket robot dog, 99 games. Crowdfunded 2024.** | `/b4/` |
| B4-DIY2 | 小龟机器狗启蒙版 (4th gen) | Robot dog, education. 2024; AI hardware upgrade 2026. | `/erha2/` |
| B3-Making | 小龟机器狗手工版 | Hand-built robot dog. 2024. | `/prism/` |
| B3 | 小龟机器狗启蒙版 (3rd gen) | Robot dog. 2023. | `/erha2/` |
| B2 | 小龟机器狗 (2nd gen) | Desktop electronic pet. 2022. | `/erha/` |
| B1 | 小龟机器狗 (1st gen) | 2021. | — |
| A3JZ | 小龟智能车 | Smart car. 2024. | `/jiazi/` |
| **A3** | 小龟创作盒 | **Mecanum car — what `a3/` documents.** 2023. | `/a3/` |
| A2 | 小龟创作板 | Maker-education board. | `/a2/` |

Vendor: 杭州集步科技有限公司 (Hangzhou Jibu Technology).

## Provenance

The `kt2/` docs are **reverse-engineered from shipped vendor code**, not translated from a manual.
They mark every claim:

- **[Verified]** — read directly out of vendor code. High confidence.
- **[Inferred]** — a conclusion drawn from it. Reasonable, unverified.
- **[Unknown]** — a genuine gap needing hardware or vendor input.

**None of it has been tested against a physical robot.** The `a3/` docs use the same markers to
separate the vendor's published text from gaps in it.
