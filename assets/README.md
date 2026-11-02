# Terminal profile assets

This profile uses only Juan's latest portrait: the close-up with clear glasses
and a black hoodie. Earlier portraits are not used by the current README or assets.
The face is actual photo-derived ASCII, not an invented avatar or embedded raster.

- `terminal-desktop.svg`: 1240 × 900, ASCII portrait left / information right.
- `terminal-mobile.svg`: 720 × 1887, portrait above / readable information below.
- `portrait.txt`: the same portrait as literal ASCII, 144 columns × 128 rows.
- `source/portrait.png`: the final photo cropped at native resolution, 1672 × 2426.

## Crop and provenance

The uploaded photo is 1792 × 3184. The crop rectangle is
`(left=120, top=70, right=1792, bottom=2496)`. This keeps the full hairstyle,
clear glasses, face and upper hoodie while removing excess wall and lower torso.
Its aspect ratio matches the 448 × 650 portrait area to within 0.01%, avoiding
stretching, a small face or a large empty margin.

Uploaded-photo SHA-256:
`7bc9f4e65be5a75220723a316f84634cc974795a6a1095cf4618820423f25d18`

Cropped-source SHA-256:
`eeb93d5c583324d0835c934d983684cb9b9bc70698d4abb27f9a9c69b1874657`

The crop preserves the original pixels; the static SVG is rebuilt from the cropped
source. No older photo is required. The foreground matte refines the outer band
of the head and hoodie to suppress the pale wall halo while protecting the eyes,
glasses and face. ASCII edges are feathered, and the background occlusion follows
the refined character silhouette instead of a coarse polygon.

## Rebuild and validation

```sh
python -m pip install -r requirements-dev.txt
python scripts/build_profile.py
python scripts/validate_profile.py
```

Pillow is a build-time dependency only. The published assets have no runtime
service, external font, image hosting, JavaScript or third-party badge dependency.
ASCII glyph coverage is calibrated with a real monospace font. Explicit character
coordinates and Liberation Mono / DejaVu Sans Mono / Consolas / Courier New
fallbacks keep the columns aligned. No font files are redistributed.

For exact glyph reproduction, use Liberation Mono. To recreate the crop from the
latest original upload, use Pillow's `Image.crop((120, 70, 1792, 2496))` and save as
`assets/source/portrait.png` before rebuilding.

The green binary background, terminal colors, profile information and contact
links are retained. Native SVG `animateTransform` drives the falling numbers;
`prefers-reduced-motion` replaces the moving layer with static digits. No effects
are drawn over the eyes or glasses. Both GitHub themes use the same opaque dark
terminal surface. The README switches to the mobile SVG at 768px or below.

## Optional browser QA

With Playwright and a local Chromium installation in a development environment:

```sh
python scripts/preview_profile.py
python scripts/check_rendering.py
python scripts/check_animation.py
```

Set `CHROMIUM_PATH` for the viewport checker if Chromium is not at
`/usr/bin/chromium`. Local screenshots and reports go to the ignored `.preview/`
directory. Checks cover light/dark backgrounds, desktop, 768px tablet, 390px phone
and 320px phone; correct responsive source selection, text clipping, horizontal
overflow, actual downward animation and the static reduced-motion fallback.
