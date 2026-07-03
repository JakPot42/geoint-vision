"""vision_analysis.py — Claude vision analysis of the before/after images.

This is the actual point of the project: Claude's real multimodal vision
capability looking at the two images directly, not a local segmentation
model. change_detection.py's pixel-diff output is handed in as context
(WHERE change was flagged) -- Claude's job is to describe WHAT the
imagery shows there, in GEOINT-brief style, never as an intelligence
determination.

DEMO_MODE (default) uses a deterministic, fully-factual template built
only from the pixel-difference statistics -- it does NOT invent a visual
description, since unlike every other DEMO_MODE fallback in this
portfolio there is no rule-based way to describe image content. This is
an honest limitation, not a placeholder disguised as a real description:
live vision analysis needs ANTHROPIC_API_KEY and was not exercised
against a real network call during this build (no key was available in
the build environment) -- same disclosure pattern as P38 BillShield AI's
Claude vision limitation.
"""
from __future__ import annotations

import base64
import io

import numpy as np
from PIL import Image

import config
from change_detection import ChangeDetectionResult


def _encode_png(image: np.ndarray) -> str:
    buf = io.BytesIO()
    Image.fromarray(image).save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _deterministic_template(result: ChangeDetectionResult, before_date: str, after_date: str) -> str:
    lines = [
        "PIXEL-DIFFERENCE ANALYSIS (deterministic template -- DEMO_MODE, no live vision call)",
        config.SCOPE_DISCLAIMER,
        "",
        f"Comparing {before_date} to {after_date}: {result.change_pct:.1f}% of the analyzed "
        f"frame exceeded the {result.threshold}-point mean-RGB-difference threshold.",
        f"{len(result.regions)} contiguous changed region(s) of at least {result.min_region_pixels} "
        "pixels were found. Largest regions (pixel count, approximate location as row/col of frame center):",
    ]
    for r in result.regions[:5]:
        lines.append(f"  - {r.pixel_count} px, centered at row {r.centroid_row:.0f}/col {r.centroid_col:.0f} "
                      f"of a {result.shape[0]}x{result.shape[1]} frame")
    lines += [
        "",
        "IMPORTANT: large, diffuse changed regions commonly reflect open-water sun-glint, wave "
        "state, or tide differences between the two acquisition dates rather than construction -- "
        "raw pixel-differencing cannot tell the two apart. This is exactly why the pipeline is "
        "designed to hand the actual images to Claude's vision capability for a real descriptive "
        "read, rather than trusting the difference mask alone. That step requires "
        "ANTHROPIC_API_KEY and DEMO_MODE=False; it was not run here.",
    ]
    return "\n".join(lines)


_SYSTEM_PROMPT = (
    "You are looking at two real Sentinel-2 satellite images of the same location on different "
    "dates (10m/pixel resolution) plus a deterministic pixel-difference analysis identifying "
    "where the images differ most. Write a short, plain-English GEOINT-style change description. "
    "Rules, mandatory: "
    "(1) Describe only what is visually apparent in the imagery -- new structures, cleared land, "
    "vessels present/absent, changes in built-up area. Do not guess at function, purpose, or "
    "capability beyond what a lay observer could see. "
    "(2) Never make an intelligence determination, threat assessment, or attribution claim. "
    "(3) Explicitly note the 10m/pixel resolution limit -- individual people and vehicles are not "
    "resolvable, only large structures and construction activity. "
    "(4) State plainly that this requires human GEOINT analyst review before any use. "
    "(5) If a flagged 'changed' region looks like it's open water, note that this commonly "
    "reflects sun-glint or wave-state differences, not real change. "
    "Output plain text, no markdown headers, under 300 words."
)


def _claude_vision_analysis(before: np.ndarray, after: np.ndarray, result: ChangeDetectionResult, before_date: str, after_date: str) -> str:
    import anthropic

    client = anthropic.Anthropic()
    context_text = (
        f"Image 1 is from {before_date}. Image 2 is from {after_date}. Same location, same "
        f"framing. Deterministic pixel-difference analysis found {result.change_pct:.1f}% of the "
        f"frame changed beyond threshold, in {len(result.regions)} region(s); the largest is "
        f"{result.regions[0].pixel_count if result.regions else 0} pixels, centered at row "
        f"{result.regions[0].centroid_row:.0f}/col {result.regions[0].centroid_col:.0f} of the "
        f"{result.shape[0]}x{result.shape[1]}-pixel frame." if result.regions else
        f"Image 1 is from {before_date}. Image 2 is from {after_date}. No significant "
        "pixel-difference regions were flagged."
    )
    message = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=700,
        system=_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": _encode_png(before)}},
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": _encode_png(after)}},
                {"type": "text", "text": context_text},
            ],
        }],
    )
    return message.content[0].text.strip()


def analyze(before: np.ndarray, after: np.ndarray, result: ChangeDetectionResult, before_date: str, after_date: str) -> str:
    if config.DEMO_MODE:
        return _deterministic_template(result, before_date, after_date)
    try:
        return _claude_vision_analysis(before, after, result, before_date, after_date)
    except Exception:
        return _deterministic_template(result, before_date, after_date)
