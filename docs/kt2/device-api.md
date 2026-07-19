# KT2 Device HTTP API

> **[Verified]** — extracted from the vendor's `car_core.js` / `ajax` layer, shipped in every
> `/b4/*` and `/apps/*` bundle. Not vendor-documented. See [README.md](README.md) for provenance.
>
> **Update 2026-07-17:** tested end-to-end against a physical unit for the first time. The RPC
> shape, `/py`, `/file`, `/data/dir/list`, and the buzzer all behave exactly as documented below.
> One endpoint was missing entirely — `GET /log` — and has been added. Callouts marked
> **[Verified — hardware]** were confirmed live; everything else is still inference from vendor
> code, as before.

The robot runs an HTTP server on the local network. Every vendor web app drives the device through
this API, so it is the complete control surface.

## Addressing

The device is reached by **local IP**. There is no discovery protocol in the web layer — the IP is
resolved in this order **[Verified]**:

1. the `?ip=` query parameter on the app URL,
2. `window.location.host`, if the page is itself served from the device,
3. `localStorage["XIAOGUI_LOCAL_IP"]` — the last-used IP, saved on `beforeunload`.

**The apps force HTTP.** `_checkProtocol()` rewrites `https://` → `http://` on load, because the
robot serves plain HTTP only:

```js
_checkProtocol: function () {
    /https/.test(window.location.protocol) &&
        (window.location.href = window.location.href.replace(/https/, "http"));
}
```

So all device traffic is unencrypted and unauthenticated. Anything on the same network can drive
the robot. Keep that in mind before putting one on a shared or untrusted LAN.

## Transport

Two shapes. **[Verified]**

### RPC — `GET /api`

```
GET http://<ip>/api?p=<endpoint>&v=<json-encoded-params>
```

`p` is the endpoint path; `v` is its parameters, `JSON.stringify`'d, then URL-encoded. Responses
are JSON. Timeout is **5000 ms**.

**Errors are signalled in the body, not the status code** — a response of `{"status": "NG"}` means
failure even on HTTP 200:

```js
get_bot: function (ip, path, ok, ng, cfg) {
    ajax.get("http://" + ip + path, function (status, resp) {
        "NG" != resp.status ? ok && ok(status, resp) : ng && ng(status, resp);
    }, ng, cfg);
}
```

Check `status !== "NG"`, not `response.ok`.

### Raw endpoints

`/py` and `/file` are **not** under `/api` — they take their own request shapes (below).

## Endpoints

Every endpoint confirmed from a call site in vendor code. **[Verified]**

### Execute Python — the important one

```
POST http://<ip>/py
Content-Type: application/x-www-form-urlencoded

code=<python source>
```

**Runs arbitrary Python on the robot.** This is the primary hook for any external tooling — you do
not need Blockly or the vendor IDE to drive the device.

```js
py: function (ip, code, ok, ng, cfg) {
    post_bot(ip, "/py", { code: code }, ok, ng, cfg);
}
```

**[Verified — hardware]** The response to `POST /py` is just `{"status": "OK", "msg": ""}` —
**it does not carry your `print()` output.** `print()` output is buffered on the device and must
be fetched separately:

```
GET http://<ip>/log?_t=<timestamp>
```

This is what the vendor's own IDE polls to fill its Log panel — `_getLog` in the `ide` bundle
runs it on an interval (`getLogLooper`) and keeps looping as long as the response is non-empty.
Confirmed live:

```
$ curl -X POST 'http://<ip>/py' --data-urlencode 'code=print("hello from the robot")'
{"status":"OK", "msg":""}

$ curl 'http://<ip>/log?_t=0'
hello from the robot
```

So driving the device from a script means **POST the code, then poll `/log` until your expected
output shows up (or a short timeout elapses)** — there's no synchronous request/response for
output the way `/api` has.

**[Verified — hardware]** `/py` is **fire-and-forget, not blocking.** Confirmed by running a
5-step physical walk followed by a `print()`:

```python
import actions
q.play(actions.walk(q, ofs=actions.ofs_stand), 5, dly=0.1)
print("walk forward: done")
```

The HTTP response came back near-instantly — far faster than 5 physical steps take. The code
itself still runs **synchronously/blocking on the device** (the `print()` only reached `/log`
once the robot had actually finished walking), but the HTTP layer doesn't wait around for that.
A poll ~2s after posting came back empty; a poll ~5s after caught the output. **A 200 from `/py`
means "accepted," not "finished executing."** Don't fire a second command assuming the first has
completed — poll `/log` with real slack, especially for anything with physical duration.

Run a file already on the device:

```
POST http://<ip>/py/file      # path passed as a parameter
```

Interrupt the running VM:

```
GET http://<ip>/api?p=/py/vm/break
```

### System

| Endpoint | Params | Purpose |
|---|---|---|
| `/sys/reboot` | — | Reboot the board. Required after saving boot files. |

### Hardware

| Endpoint | Params | Purpose |
|---|---|---|
| `/hw/buzzer/music` | `{music: "1="}` | Play a tune string. `"1="` is the "Hi" chirp. |
| `/hw/adc/battery` | — | Battery level. Used by `/apps/battery/`. |

The music string format is a numbered-notation ("简谱") dialect — `"1="` is the shortest valid
tune. Full grammar is **[Unknown]**; the `car.buzzer.music()` Python call takes the same string.

**[Verified — hardware]** actual responses from a physical unit:

```
GET /api?p=/hw/adc/battery
→ {"battery":3970,"usb":0,"status":"OK"}

GET /api?p=/hw/buzzer/music&v={"music":"1="}
→ {"status":"OK"}
```

`battery` is plausibly millivolts (3970 ≈ a single-cell Li-ion mid-charge); `usb` is `0`/`1` for
whether USB power is connected. Both readings are **[Inferred]** from context — the field names
came with no unit documentation.

### Files

| Endpoint | Params | Purpose |
|---|---|---|
| `/data/file/exists` | `{path}` | Test a file |
| `/data/file/stat` | `{path}` | File metadata |
| `/data/file/del` | `{path}` | Delete a file |
| `/data/file/rename` | `{path, ...}` | Rename |
| `/data/dir/list` | `{path}` | List a directory |
| `/data/dir/exists` | `{path}` | Test a directory |
| `/data/dir/del` | `{path}` | Delete a directory |

Read/write file **content** uses a separate endpoint, not `/api`:

```
GET  http://<ip>/file?path=<path>     # read
POST http://<ip>/file?path=<path>     # write (body = content)
```

### Config

| Endpoint | Purpose |
|---|---|
| `/cfg/get_json` | Read a JSON config blob |
| `/cfg/set_json` | Write a JSON config blob |

## On-device filesystem

Paths harvested from vendor call sites. **[Verified]** as paths the apps read and write; the
**full tree is [Unknown]** without a device.

| Path | Written by | Purpose |
|---|---|---|
| `/my/boot.py` | Python IDE | **Boot script.** Runs on startup. |
| `/my/boot.bpy` | Blockly editor | Blockly source (XML) for the boot script |
| `/my/ide/__temp.py` | Python IDE | Scratch buffer for Run |
| `/my/gamepad/gamepad_config.py` | Gamepad editor | Gamepad handler definitions |
| `/my/gamepad/gamepad_config.bpy` | Gamepad editor | Blockly source for the above |
| `/my/_startup.py` | Agent table | Agent startup script |
| `/my/agent_*` | Agent table | Per-agent files |
| `/my/mixly/` | Blockly editor | User's custom block categories |
| `/my/bot/user_config.json` | calibration app | **Servo pin map + calibration.** See [python-api.md](python-api.md#servo-calibration--real-values-from-hardware). **[Verified — hardware]** |
| `/sys/libs/*.py` | dependency resolver | Shared Python libraries |
| `/sys/bot/*.mpy` | preinstalled, firmware partition | **Bot-specific libraries — `actions`, `imu`, etc. Precompiled bytecode, not source.** **[Verified — hardware]** |

### The `.py` / `.bpy` pair

Every graphical artifact is stored twice: `.bpy` is the Blockly XML, `.py` is the generated
MicroPython. The robot executes the `.py`. **[Inferred]** — this is also why, on the A3, the
vendor documents graphical edits as overriding Python edits: saving from Blockly regenerates the
`.py` from the `.bpy` and clobbers hand-written changes. Expect the same hazard here.

Blockly files carry a version marker so the editor can reload the right toolbox **[Verified]**:

```python
#BLOCKLY_VERSION_ID:b4-advanced
```

## Library dependency resolution

Worth understanding, because it's how `actions` gets onto a robot. When the Blockly editor runs
your code it **[Verified]**:

1. Parses `import` statements out of the generated Python.
2. Filters out MicroPython/ESP32 builtins (a hardcoded list: `machine`, `network`, `esp32`,
   `neopixel`, `time`, `json`, `math`, `random`, `socket`, `bluetooth`, `framebuf`, … — also
   matching the `u`-prefixed aliases, e.g. `utime` for `time`).
3. For each remaining module, checks `/sys/libs/<name>.py` on the device, then `/sys/bot/<name>.py`.
4. If **neither** exists, downloads `./py-libs/<name>.py` **from the web app** and saves it to
   `/sys/libs/<name>.py` on the device.
5. If that 404s, logs 缺少库资源 ("missing library resource") and continues.

So `/sys/bot/` holds preinstalled bot-specific libraries, while `/sys/libs/` is a web-populated
cache. Confirmed web-hosted libraries at `https://guidan.com/b4/blk/py-libs/`:

- `ws2812.py` **[Verified]** — 200, and turns out to be a generic Mixly-team NeoPixel driver, not
  KT2-specific.
- `servo.py` **[Verified]** — 200, likewise a generic 0–180° servo driver.

`actions.py` and `imu.py` are **not** web-hosted (404), which means they ship on the device under
`/sys/bot/`. **[Verified — hardware]:** confirmed directly — `import actions` on a real unit
resolves to `<module 'actions' from '/sys/bot/actions.mpy'>`. Note the extension: **`.mpy`, not
`.py`** — precompiled MicroPython bytecode on the firmware partition. There is no source file to
read even in principle; `/file?path=/sys/bot/actions.py` was never going to work, because that
path doesn't exist. See the note on `/data/dir/list` below for why it doesn't even show up in a
directory listing.

### `/data/dir/list` doesn't reach the firmware partition

**[Verified — hardware]:** `/data/dir/list` on `/sys/bot` or `/sys/libs` returns
`{"files": [], "count": 0, "status": "OK"}` — empty, despite `actions.mpy` demonstrably loading
from `/sys/bot`. **[Inferred]:** `/data/...` is scoped to a writable user-data partition, and
`/sys/bot` is a separate, read-only firmware partition that this endpoint doesn't enumerate. It
isn't a permissions error or a wrong path — the endpoint reports success with zero results.
`/my` **does** list correctly (e.g. `["bot/user_config.json"]`), which is where the calibration
data in [python-api.md](python-api.md#servo-calibration--real-values-from-hardware) came from.

## Minimal client

**[Verified — hardware]** — the shape below (`api`, `py`+`log`, `read_file`) has been run against
a physical unit; the convenience wrappers (`hi`, `stop`, `reboot`) follow the same confirmed `api`
call and weren't separately re-verified beyond `hi()`.

```python
import json, time, urllib.parse, urllib.request

class KT2:
    def __init__(self, ip):
        self.base = f"http://{ip}"

    def api(self, endpoint, params=None):
        q = {"p": endpoint}
        if params is not None:
            q["v"] = json.dumps(params)
        url = f"{self.base}/api?" + urllib.parse.urlencode(q)
        with urllib.request.urlopen(url, timeout=5) as r:
            resp = json.loads(r.read())
        if isinstance(resp, dict) and resp.get("status") == "NG":
            raise RuntimeError(f"device returned NG for {endpoint}: {resp}")
        return resp

    def py(self, code, wait=0.3):
        """Execute Python on the robot and return whatever it printed.

        /py's own response carries no output — output has to be polled from
        /log separately. `wait` is a fixed pause before polling once; for
        long-running code, poll /log yourself in a loop instead.
        """
        body = urllib.parse.urlencode({"code": code}).encode()
        with urllib.request.urlopen(f"{self.base}/py", data=body, timeout=5) as r:
            r.read()  # {"status": "OK", "msg": ""} — not the print() output
        time.sleep(wait)
        return self.log()

    def log(self):
        url = f"{self.base}/log?_t={int(time.time() * 1000)}"
        with urllib.request.urlopen(url, timeout=5) as r:
            return r.read().decode()

    def read_file(self, path):
        url = f"{self.base}/file?path=" + urllib.parse.quote(path)
        with urllib.request.urlopen(url, timeout=5) as r:
            return r.read().decode()

    def hi(self):      return self.api("/hw/buzzer/music", {"music": "1="})
    def stop(self):    return self.api("/py/vm/break")
    def reboot(self):  return self.api("/sys/reboot")
    def battery(self): return self.api("/hw/adc/battery")


bot = KT2("192.168.1.42")
bot.hi()
print(bot.py('import actions\nq.play(actions.bark(q), dly=0.1)\nprint("done")'))
```

**Reading the on-device libraries doesn't work — and now we know why.** `/sys/bot/actions.mpy` and
`/sys/bot/imu.mpy` are **precompiled MicroPython bytecode**, not source, sitting on a firmware
partition that `/data/dir/list` doesn't even enumerate (see above). There is no `.py` to fetch.
Confirmed on hardware — this used to be phrased as "the single highest-value next step"; it no
longer is, because it's not achievable via this API. What *is* achievable, and was just done: probe
behaviour empirically via `/py` (checking what names exist, what a call returns) and read
`/my/*` config files, which are plain JSON/text on the writable partition. The servo calibration
data in [python-api.md](python-api.md#servo-calibration--real-values-from-hardware) came from
exactly that.
