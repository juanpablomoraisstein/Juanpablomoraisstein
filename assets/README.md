# Terminal profile assets

The portrait is sampled from **Juan's actual attached photograph**, preserved in
`source/portrait.png`. It is not a generated avatar or a raster image embedded in
an SVG. Every visible portrait mark in the SVG is a literal ASCII character.

- `terminal-desktop.svg`: 1240 × 900, portrait left / information right.
- `terminal-mobile.svg`: 720 × 1887, portrait above / readable information below.
- `portrait.txt`: the 144-column, 128-row portrait as plain ASCII.
- `source/portrait.png`: original, unmodified source photo (864 × 1536).

Source photo SHA-256:
`06b519e1c5050caa06157802d2cf1f0f76cdcd4bed549452c0b83f309f7fe8d6`

## How it is built

```sh
python -m pip install -r requirements-dev.txt
python scripts/build_profile.py
python scripts/validate_profile.py
```

Pillow is a build-time dependency only. The published profile has no runtime
service, external font, image host, JavaScript or third-party badge dependency.
The generator uses a foreground silhouette mask to remove the chair/curtain,
crops the actual head-and-shoulders photo, adjusts grayscale contrast, and samples
it into a 144 × 128 grid. Glyph coverage is measured with a real monospace font
instead of assuming that every character has equally spaced brightness.
Shadows use cool blue/cyan ink; highlights use restrained warm white/orange ink.

The SVG uses real text with explicit character coordinates, plus reliable
monospace fallbacks: Liberation Mono, DejaVu Sans Mono, Consolas and Courier New.
It does not depend on SVG font downloads or operating-system font metrics for
the placement of individual ASCII glyphs. To rebuild on Linux, install Liberation
Mono or DejaVu Sans Mono; on Windows the generator can use Consolas. To reproduce
the committed glyph choices exactly, use Liberation Mono and the same Pillow
version. No font files are redistributed.

The background is opaque and self-contained, so the same design retains its dark
terminal appearance in both GitHub themes. README's `<picture>` switches to the
stacked layout at viewport widths of 768px or less. Contact links and an accessible
plain-text copy of the profile remain ordinary Markdown/HTML below the graphic.
The source photo remains in this repository so the conversion is reproducible.

## Optional browser checks

With a local Chromium installation and Playwright installed in a development
Python environment:

```sh
python scripts/preview_profile.py
python scripts/check_rendering.py
```

Set `CHROMIUM_PATH` if the executable is not `/usr/bin/chromium`.
These commands write local previews to the ignored `.preview/` directory; no
browser-testing dependency is needed to display the profile. The checks cover
light/dark backgrounds, desktop, 768px tablet, 390px phone and 320px phone widths,
assert the correct responsive asset is chosen, and check for text clipping and
horizontal page overflow.
