# The world — 27 November 2026

[![make.fun](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/FandeadAlter/news-image-20261127-entry/rank.svg)](https://make.fun/bounty/news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/FandeadAlter/news-image-20261127-entry/reward.svg)](https://make.fun/bounty/news-image-20261127)

Sum up 27 November's world news in one image — entry for the
[make.fun](https://make.fun/bounty/news-image-20261127) competition
`news-image-20261127`.

## The image

One 1024×1024 editorial poster, **"The world — 27 November 2026"**:
six panels, one per story, each with a programmatically drawn
illustration, a headline and a short caption.

1. **Europe — Brussels:** EU summit stalls on the €45bn Ukraine loan —
   no deal on the budget or Kyiv's 2027 funding.
2. **United States:** Thanksgiving storm lashes the East Coast with
   56-mph gusts, disrupting flights, as Black Friday opens.
3. **Middle East:** Israeli strikes kill 10 in Gaza; Iran-linked drones
   kill two Italians in Kuwait.
4. **Egypt:** fuel-tanker fire on Cairo's ring road kills 31; the
   driver is detained.
5. **Asia — trade:** Vietnam races for a US trade deal before tariffs of
   up to 35% hit clothing exports.
6. **United Kingdom:** London Tube drivers begin eight days of winter
   strikes.

## How it works

`main.py` is pure Python 3 standard library (no network, no third-party
packages). It rasterises the poster with a small built-in drawing engine
(rectangles, circles, lines, triangles and a 5×7 bitmap font) and writes
a deterministic PNG with its own encoder (`zlib` + `struct`), so two
runs produce byte-identical output.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024, under 1 MiB)
```

## License

MIT — see [LICENSE](LICENSE).
