# Graphical Programming (图形编程)

> Translated from <https://guidan.com/a3/manual/mixly/>

The A3's built-in graphical programming is **based on a Mixly (米思齐) extension**. This page
collects Mixly's official tutorials and demonstrates basic use of A3 graphical programming.

## Heads-up

**This page is a stub.** In the original it is one sentence plus four links — there is no A3-specific
block reference, no block list, and no worked example in text form. The A3-specific material exists
only as a video.

If you're looking for something to build against, the useful pages are
[python.md](python.md) (the `move()` API), [pins.md](pins.md) (the pinout), and
[gamepad-programming.md](gamepad-programming.md) (the handler naming contract).

## Mixly official tutorials (米思齐官方教程)

| Resource | Link |
|---|---|
| Illustrated/text tutorial (图文教程) | <https://mixly.readthedocs.io/zh-cn/latest/> |
| Bilibili video tutorials | <https://space.bilibili.com/641272017> |
| NetEase Cloud Classroom video course (网易云课堂视频教程) | <https://study.163.com/provider/480000002171531/course.htm> |

All are in Chinese. These are upstream Mixly docs — they cover Mixly generally, not the A3
extension.

## A3 graphical programming guide (小龟A3图形编程使用说明)

📹 <https://www.bilibili.com/video/BV146421w7Y4/> (Bilibili, Chinese)

**[Not in source]** — the entire A3-specific guide is this video. Not transcribed.

## Useful in practice

From [gamepad-programming.md](gamepad-programming.md), two things about the graphical editor are
worth knowing when working with Python instead:

- **File → View** shows the **generated Python** for your blocks. This is the most reliable way to
  discover the actual API the blocks call — useful given how thin the Python docs are.
- If a button is defined in **both** graphical and Python programming, **the graphical definition
  wins.** A stray block can silently shadow a Python handler.

Saving requires a **board restart** to take effect.
