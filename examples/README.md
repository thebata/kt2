# Examples

Runnable Python examples for the KT2, using only the standard library.

- `kt2_client.py` - minimal HTTP client (`api`, `py`, `log`, `hi`, `battery`, `stop`).
  Talks to the device over the API described in
  [../docs/kt2/device-api.md](../docs/kt2/device-api.md).
- `simple_walk.py` - connects to a robot, reads battery level, then makes it
  walk forward, turn, and kick.

## Run it

```
python simple_walk.py 192.168.1.42
```

Replace the IP with your robot's actual address on the local network.

## Gen A vs Gen B

These examples assume the newer **Gen B** API (`q` / `actions`). If your robot
uses the older **Gen A** editor instead (`kt2` / `__actions`), swap the code
string in `simple_walk.py` accordingly - see
[../docs/kt2/python-api.md](../docs/kt2/python-api.md#two-api-generations) for
the exact differences (imports, object names, and note that the `x` direction
parameter means the *opposite* thing between the two generations).

Only actions confirmed working on real hardware are used here
(`walk`, `c_pivot`, `one_key_reset`, `left_kick`) - see
[../docs/kt2/python-api.md](../docs/kt2/python-api.md#naming-and-what-actually-exists)
for the full list of what's confirmed vs. untested vs. confirmed missing.
