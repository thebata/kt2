# KT2 System Architecture

> **[Verified]** — from the vendor's app hub HTML/JS and by probing which URLs exist.
> See [README.md](README.md) for provenance.

## The shape of it

The KT2 has **no native app**. Everything is web pages talking to an HTTP server on the robot over
the local network.

```
┌─────────────────┐         ┌──────────────────────┐
│  guidan.com     │  page   │  Browser             │
│  (vendor host)  ├────────►│  /b4/index/          │
│  HTTPS          │  loads  │  (downgraded to HTTP)│
└─────────────────┘         └──────────┬───────────┘
                                       │  GET /api?p=…
                                       │  POST /py
                                       ▼
                            ┌──────────────────────┐
                            │  KT2 robot           │
                            │  ESP32 + MicroPython │
                            │  http://<local-ip>   │
                            │  /sys/bot/*.py       │
                            │  /my/*.py            │
                            └──────────────────────┘
```

The pages are served by the vendor; the **control traffic never goes to the vendor** — it goes
straight from your browser to the robot on the LAN. Which is why the hub force-downgrades itself
to HTTP: an HTTPS page cannot make plain-HTTP requests to the robot without mixed-content errors.

**Consequence:** the apps only work while `guidan.com` is up and serving them, unless you load them
from the robot itself. See "Two hosting modes" below.

## Two hosting modes

The hub detects where it is running **[Verified]**:

```js
var t = window.location.host;
if (!t.match(h.IP_REG) && !t.match(/^local/)) {
    // NOT on the device → rewrite "common" app links to the vendor CDN
    document.querySelectorAll("[common=true]").forEach(function (el) {
        el.href = ("http://guidan.com/apps/" + el.getAttribute("href")).replace(/\.\.\//, "");
    });
    document.querySelectorAll("[only-online=true]").forEach(el => el.style.display = "block");
    document.querySelector("#os-entry").style.display = "none";
}
```

So:

- **Loaded from the robot's IP** (or a `local*` host) — apps resolve to the **device's own copies**,
  and the `#os-entry` link is shown.
- **Loaded from guidan.com** — apps marked `common=true` are rewritten to `guidan.com/apps/…`,
  `only-online` elements appear, and the xiaoguiOS entry is **hidden**.

**[Inferred]:** the robot serves its own copy of every app, so the whole toolchain works offline
with no internet — the vendor host is a convenience, not a dependency. This is a strong inference
(it's the only reading that makes the branch meaningful) but untested without hardware.

## The app surface

Sixteen entries on the hub. Verified by probing every URL **[Verified]**.

### KT2-specific (`common=false` → `guidan.com/b4/<name>/`)

| App | Chinese | Purpose |
|---|---|---|
| `games` | 游戏 | The 99 built-in games |
| `blk` | 图形编程 | **Blockly editor** — the source of the API docs here |
| `actions` | 动作集 | Action set browser |
| `agent-table` | 智能体创作 | Agent authoring — see [agent.md](agent.md) |
| `calibration` | 安装校准 | Servo installation calibration |

### Shared across products (`common=true` → `guidan.com/apps/<name>/`)

| App | Chinese | Purpose |
|---|---|---|
| `devices` | 选择设备 | Device/IP selection |
| `gamepad` | 虚拟手柄 | On-screen gamepad |
| `ide` | Python | **MicroPython IDE** |
| `explorer` | 文件管理 | On-device file manager |
| `boot-files` | 开机启动 | Boot script manager |
| `battery` | 电量 | Battery level |
| `gamepad-editor` | 手柄编程 | Gamepad handler editor — see [gamepad.md](gamepad.md) |
| `settings` | 设置 | Settings |

The two sets are **exactly complementary**: every `common=true` app 404s under `/b4/` and 200s
under `/apps/`, and vice versa. That's what confirms the mechanism rather than merely suggesting it.

### Inline actions

Two hub buttons call the device directly rather than opening an app **[Verified]**:

```html
<a href="javascript:Car.hi();">Hi</a>       <!-- GET /api?p=/hw/buzzer/music&v={"music":"1="} -->
<a href="javascript:Car.reboot();">重启</a>  <!-- GET /api?p=/sys/reboot -->
```

### A second, unlinked editor at `/kt2/`

**[Verified]** — `https://guidan.com/kt2/` is a **standalone Blockly editor**, not linked from any
hub, with its own bundle (`app250103`) and its own module config:

```json
{ "id": "kt2", "categories": ["./modules/kt2-en/actions/",
                              "./modules/kt2-en/buzzer/",
                              "./modules/kt2-en/led/"] }
```

It is a **different API generation** from `/b4/blk/` — `kt2`/`__actions` instead of `q`/`actions`,
with contradictory `x` semantics. This matters a great deal if you target the wrong one; see
[python-api.md](python-api.md#two-api-generations).

Notable properties:

- **`kt2-en` is the only English-named module set on the site.** Every other set is language-neutral
  with `msg/en.js` overlays.
- It has **three categories** (actions, buzzer, led) against b4-advanced's nine — no gamepad,
  no agent, no imu, no control.
- Its bundle predates `/b4/blk/` by four months.
- Nothing links to it. It is only discoverable by guessing the URL.

**[Inferred]:** a legacy or English-market build, superseded by `/b4/blk/`. But this is genuinely
uncertain — it is named for the product, and "superseded" doesn't explain why it's still deployed.
**[Unknown]** which one a given robot's firmware actually expects.

### Cloud block modules — referenced but absent

The toolbox loader rewrites category paths starting `/cloud` to
`https://guidan.com/apps/blk-modules/…` **[Verified]**. That whole tree **404s** — `/apps/blk-modules/`
and every path under it that I probed. The KT2's config uses only local `./modules/…` paths, so the
mechanism is unused here. **[Inferred]:** a shared cross-product block library that is either
retired or served only from devices.

### Dead link

`#os-entry` → **`/os.html`** ("使用xiaoguiOS创作你的机器人" — "create your robot with xiaoguiOS")
**404s** on the vendor host **[Verified]**. It is hidden unless the hub is loaded from the device,
so **[Inferred]** it's meant to be served by the robot. **xiaoguiOS is otherwise undocumented** —
it appears as a logo on the A3's pinout diagram and in this dead link, and nowhere else.

## The Blockly toolbox pipeline

Worth understanding, because it's where the API documentation actually came from.

The editor builds its toolbox at runtime from a JSON config **[Verified]**:

1. Fetch **`/b4/blk/modules/config.json`** — an array of editions, each `{id, label, categories[]}`.
2. For each category path, load three files:
   - `<path>/index.xml` — toolbox XML
   - `<path>/blocks.js` — block definitions (shape, labels)
   - `<path>/generators.js` — **the Python code templates**
   - plus `<path>/msg/<lang>.js` — labels, falling back to `msg/en.js`
   - plus `<path>/index.css`
3. Category paths beginning **`/cloud`** are rewritten to
   `https://guidan.com/apps/blk-modules/…` — a shared cross-product block library. The KT2's own
   config uses only local `./modules/…` paths.
4. `toolbox.addCategoryFromBot(...)` loads categories **from the device** instead, and
   `customPath: "/my/mixly/"` is where a user's own categories live.

Which edition loads is resolved from, in order: a `?version_id=` param; the
`#BLOCKLY_VERSION_ID:<id>` marker inside the opened `.bpy` file; or
`localStorage["BLOCKLY_VERSION_ID"]`. **[Verified]**

### Why this matters

`generators.js` is a **complete, unminified, authoritative** description of what every block emits.
It's better than prose documentation would be — it can't drift from the implementation, because it
*is* the implementation. That's the basis for [python-api.md](python-api.md),
[gamepad.md](gamepad.md), and [agent.md](agent.md).

Its limit: it shows **call sites**, not definitions. The `actions` / `imu` / `process` modules
themselves live at `/sys/bot/*.py` on the device, so ranges, units, and return types stay
**[Unknown]**. Dumping those files off a real device is the single highest-value next step — see
[device-api.md](device-api.md#minimal-client).

## Versions seen

Bundle filenames carry dates. Captured 2026-07-17 **[Verified]**:

| App | Bundle |
|---|---|
| `b4/index` | `app250515.min.js` |
| `b4/blk` | `app250506.min.js` |
| `b4/games` | `app241128.min.js` |
| `b4/actions` | `app250320.min.js` |
| `b4/agent-table` | `app250411.min.js` |
| `b4/calibration` | `app250411.min.js` |
| `apps/explorer` | `app260123.min.js` |
| `apps/ide` | `app250325.min.js` |
| `apps/gamepad` | `app250319.min.js` |

**[Inferred]** the `YYMMDD` scheme — `app250506` = 2025-05-06. Most of the KT2 apps date to
2025; `explorer` is the only one from 2026. The vendor catalog lists "2026年AI硬件升级" (2026 AI
hardware upgrade) for the sibling B4-DIY2, so this product line is still moving — expect these
docs to drift.
