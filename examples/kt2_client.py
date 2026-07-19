"""Minimal HTTP client for the KT2 robot dog.

Talks to the on-device HTTP server described in ../docs/kt2/device-api.md.
No external dependencies - only the Python standard library.
"""
import json
import time
import urllib.parse
import urllib.request


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
        """Run MicroPython code on the robot and return whatever it printed.

        The /py response itself carries no output - print() output has to be
        polled from /log separately. `wait` is a fixed pause before polling
        once; for longer-running code (walking, flips, ...) call log()
        yourself in a loop until the expected text shows up.
        """
        body = urllib.parse.urlencode({"code": code}).encode()
        with urllib.request.urlopen(f"{self.base}/py", data=body, timeout=5) as r:
            r.read()  # {"status": "OK", "msg": ""} - not the print() output
        time.sleep(wait)
        return self.log()

    def log(self):
        url = f"{self.base}/log?_t={int(time.time() * 1000)}"
        with urllib.request.urlopen(url, timeout=5) as r:
            return r.read().decode()

    def hi(self):
        return self.api("/hw/buzzer/music", {"music": "1="})

    def stop(self):
        return self.api("/py/vm/break")

    def battery(self):
        return self.api("/hw/adc/battery")
