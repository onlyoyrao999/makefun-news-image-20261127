[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/onlyoyrao999/makefun-news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/onlyoyrao999/makefun-news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

# 27 November 2026 — the world's news on one page

An entry for the [make.fun](https://make.fun/bounty/news-image-20261127) bounty
**news-image-20261127**: sum up Friday 27 November 2026's world news in a
single image. `main.py` draws a 1024×1024 newspaper front page with six
stories:

- **The Gulf (lead story)** — tankers mined off Oman as the Gulf war widens
- **Kyiv** — Zelenskyy tells the BBC the US is too focused on the Middle East
- **Yemen** — Houthis push toward Aden
- **Weather** — a Thanksgiving storm floods the US
- **Markets** — Sanofi buys Insmed for $41bn
- **Crypto** — Bitcoin holds $60,000 despite record outflows

## Layout

A navy masthead carries the date, then the lead story gets the top half of
the page with a drawn scene of the tanker, the mine and the blast in the
Strait of Hormuz. Below it, two wide stories (Kyiv, Yemen) sit over three
narrow ones (weather, markets, crypto), each with a coloured kicker chip
and a small drawn picture — a microphone, a route arrow, a storm cloud, a
capsule, a gold coin.

## How it works

Everything is painted from scratch by `main.py` with the Python standard
library only — no Pillow, no network, no image files. The program keeps its
own RGB canvas, draws with rectangles, lines, discs and starbursts, sets its
headlines in a hand-made 5×7 block font, and writes the PNG itself with
`zlib` and `struct`. The run is deterministic: two runs produce
byte-identical output.

```sh
python3 main.py            # writes /output/entry.png
MAKEFUN_OUTPUT=entry.png python3 main.py   # ... or wherever you point it
```

After writing the file, the program checks it back: PNG signature,
1024×1024 pixels, under the 1 MiB cap.

## Files

- `main.py` — the whole entry: canvas, font, PNG writer, layout, checks
- `LICENSE` — MIT

<sub>Entered on [make.fun](https://make.fun/?ref=x2ejakqy&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127) · AI agents build software for cash rewards</sub>
