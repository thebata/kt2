# Networking (联网)

> Translated from <https://guidan.com/a3/manual/connect/>

Besides controlling the A3 over a **direct WiFi connection** as described in
[first use](first-use.md), you can also **connect the A3 to a network**. Once connected, you can
use an **online page** to control it.

📹 <https://www.bilibili.com/video/BV1XD421E7L7/> (Bilibili, Chinese)

🔗 **Online control page:** <http://guidan.com/a3box/>

---

## Heads-up

The text above is the page's complete content. The two connection modes are:

1. **Direct WiFi** — connect your phone straight to the A3's own access point. This is the
   first-use default.
2. **Networked** — join the A3 to an existing WiFi network, then drive it from the vendor's hosted
   page at `guidan.com/a3box/`.

**[Not in source]** — the actual procedure for joining a network (how credentials are entered,
whether it's captive-portal or code-based, what happens to the AP afterwards) exists only in the
video. Not transcribed.

## Worth noting before using this

The online control page is **plain HTTP**, not HTTPS, and it is **vendor-hosted**. Control traffic
would depend on a third-party server being up and reachable. For development work — especially
anything unattended or on an untrusted network — direct WiFi or a local connection avoids that
dependency entirely.
