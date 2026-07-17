# GEOINT Vision Pipeline

## Scope

**A Claude-vision-powered change-detection and briefing tool, not a
validated computer vision research system.** No local ML/segmentation
model runs anywhere in this pipeline (no LLaVA, no SAM, no object
detector) — that was explicitly rejected as research-lab-scale, the same
"drop the research-lab-scale trap" discipline applied to the MOF Discovery
project's GNN reshape. Deterministic pixel-difference thresholding flags
*where* two images differ; Claude's real multimodal vision capability is
what *describes* what's there. Neither step makes an intelligence
determination, a capability/threat assessment, or an attribution claim.
Sentinel-2's public bands are 10 m/pixel at best — individuals, vehicles,
and most equipment are not resolvable, only large structures and
construction activity are. Every output states this and requires human
GEOINT analyst review before any use (`config.SCOPE_DISCLAIMER`, printed
on every command).

```
python main.py demo                          # flagship demo, bundled real imagery, no network/key needed
python main.py search --lat LAT --lon LON --start DATE --end DATE
python main.py analyze --lat LAT --lon LON --before-start D --before-end D --after-start D --after-end D
```

---

## Data sourcing

**The original spec named the "Copernicus Open Access Hub API."** That service
was decommissioned in October 2023, replaced by the Copernicus Data Space
Ecosystem — which requires a registered account (free, but self-serve
registration needs a human, not something buildable/testable
autonomously). Checked directly before writing any code, not assumed
still-live from the original spec.

**What this uses instead, verified live during this build:** AWS's
Element84 "Earth Search" STAC API (`earth-search.aws.element84.com`) for
catalog search, plus the public `e84-earth-search-sentinel-data` S3
bucket for actual pixel data (`sentinel-2-c1-l2a` collection, Cloud-
Optimized GeoTIFFs) — **zero registration, zero authentication.** This is
a genuinely public mirror of the same real ESA/Copernicus Sentinel-2
archive, actually more frictionless than the original spec's intent, not
a downgrade. `rasterio` does windowed HTTP range-request reads against
the COGs, so only the ~a few hundred KB around the target coordinate is
pulled, not the full ~110 km tile.

**A real constraint found and worked around:** this specific public
mirror's `sentinel-2-c1-l2a` ("Collection 1" reprocessing) coverage for
the demo tile starts January 2018, not back to the mission's 2015 launch
or the base's March 2016 construction start. The flagship demo therefore
compares 2018-05-26 to 2019-10-23 (the pier-construction phase) rather
than the full 2016 "bare land to fortress" transition — still real,
still dramatic, still exactly matches independently published reporting
(see below), just a different phase of the same facility's growth than
a first guess would have picked.

---

## Flagship demo — Chinese PLA Support Base, Djibouti

**11.59265°N, 43.06049°E.** Real, public, well-documented change: a
300+ meter pier was built at the base between 2018 and 2019.

- Forbes, "Satellite Images Show That Chinese Navy Is Expanding Overseas
  Base" (H I Sutton, May 10, 2020)
- USNI News, "AFRICOM: Chinese Naval Base in Africa Set to Support
  Aircraft Carriers" (April 20, 2021)

Both demo images (`data/djibouti_before_2018-05-26.png`,
`data/djibouti_after_2019-10-23.png`) were pulled and verified live
through the real pipeline during this build — not fabricated or
AI-generated. `python main.py demo` reproduces them offline from the
bundled files; `python main.py analyze --lat 11.59265 --lon 43.06049
--before-start 2018-01-01 --before-end 2018-06-30 --after-start
2019-09-01 --after-end 2019-12-31` reproduces the identical result live
(confirmed in testing — same two scene IDs selected either way).

The deterministic pixel-diff flags 34.4% of the frame as changed, with
the largest region (51,029 px) covering open water — a real, disclosed
limitation of raw RGB differencing (sun-glint/wave-state differences
between acquisition dates look like "change" too) — and smaller, more
localized regions corresponding to the actual pier and building
footprint changes. This is exactly why the pipeline hands the real
images to Claude's vision capability rather than trusting the
difference mask alone: pixel-diff casts a wide net, vision analysis is
what would actually distinguish real structural change from natural
variation.

---

## Honest limitation — live vision analysis was not exercised

`vision_analysis.py` sends both images to Claude via the real messages
API (multimodal content blocks) when `DEMO_MODE=False` and
`ANTHROPIC_API_KEY` is set, and is built to the same exception-handling
standard as every Claude call site in this portfolio (falls back to the
deterministic template on any API error). **No API key was available in
this build environment**, so the live vision call path was never
exercised against a real network call this session — the same honest gap
already on record for this portfolio's other vision-capable project
(BillShield AI). `DEMO_MODE` (default) uses a template built only
from the real pixel-difference statistics — it does not invent a visual
description, since unlike every other `DEMO_MODE` fallback in this
portfolio, there's no rule-based way to describe image content.

---

## Change detection — the formula

`change_detection.py`: mean absolute RGB difference per pixel →
threshold (default 40 of 255) → `scipy.ndimage.label` connected-component
grouping → regions smaller than 25 px dropped as noise. Pure arithmetic,
no training, no tuning against a labeled dataset — disclosed as a coarse
localization signal, not a verified structural-change classifier.

---

## Tech stack

Python, `rasterio` (windowed COG reads via HTTP range requests), `scipy`
(connected-component labeling), Matplotlib, Click, Rich (`box.ASCII2`),
ReportLab, Anthropic Claude (vision-capable Haiku, `DEMO_MODE`-gated).
22 tests, all passing.
