# MicroPython

> Translated from <https://guidan.com/a3/manual/micropython/>

The A3 is based on the **ESP32-S3** chip and has **MicroPython built in**. This page collects
MicroPython's official tutorials, official libraries, and community third-party libraries, and
demonstrates how to import and use third-party libraries on the A3.

## Official tutorials (官方教程)

MicroPython official site — ESP32 quick reference:
<https://docs.micropython.org/en/latest/esp32/quickref.html>

> The A3 is an **ESP32-S3**; the linked quick reference is the general ESP32 page. Most of it
> applies, but S3-specific differences (pin count, USB-native support) are not covered by the
> vendor.

## Library resources (库资源)

| Resource | Link |
|---|---|
| MicroPython official library repo | <https://github.com/micropython/micropython-lib> |
| Community-curated library collection | <https://awesome-micropython.com/> |

## Importing third-party libraries onto the A3

📹 <https://www.bilibili.com/video/BV1Yt42157AD/> (Bilibili, Chinese)

**[Not in source]** — the whole procedure is this video. No written steps, no mention of the
transfer mechanism (`mpremote`, WebREPL, the Mixly IDE, or something vendor-specific). Not
transcribed.

## Notes for development

- **MicroPython is the underlying runtime**, which is consistent with the [Python page](python.md)
  using `move()` / `stop()` / `car.hcsr04()` without imports — those are presumably injected by the
  vendor's runtime layer rather than being standard MicroPython. **[Inferred]**
- Standard MicroPython ESP32 APIs (`machine.Pin`, `machine.PWM`, `machine.I2C`, `time.sleep`)
  should be available, which matters given the vendor documents no API for the buzzer, RGB LED,
  or IMU. Combined with [pins.md](pins.md), driving those directly via `machine` is likely the
  practical route. **[Inferred]** — untested.
- The board ships **three systems**: Mixly, MicroPython, and XiaoguiOS. How they coexist, and what
  XiaoguiOS actually is, is **[Not in source]** — it appears only as a logo on the pinout diagram
  and is documented nowhere in the manual.
