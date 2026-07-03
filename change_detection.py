"""change_detection.py — deterministic pixel-difference change detection.

Purely arithmetic, no ML: mean absolute RGB difference per pixel,
thresholded, then connected-component analysis (scipy.ndimage.label) to
group changed pixels into regions and drop small ones as noise. This is
what tells the pipeline WHERE change occurred; Claude vision (see
vision_analysis.py) is what describes WHAT the change looks like.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import ndimage

import config


@dataclass
class ChangeRegion:
    pixel_count: int
    centroid_row: float
    centroid_col: float
    bbox: tuple[int, int, int, int]   # (row_min, row_max, col_min, col_max)


@dataclass
class ChangeDetectionResult:
    diff: np.ndarray            # (H, W) float, mean abs RGB difference per pixel
    mask: np.ndarray            # (H, W) bool, cleaned change mask (small regions removed)
    regions: list[ChangeRegion]  # sorted by pixel_count descending
    change_pct: float           # % of analyzed pixels flagged as changed
    threshold: int
    min_region_pixels: int
    shape: tuple[int, int]


def _align(before: np.ndarray, after: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Different scenes' windowed reads can differ by a pixel or two due to
    floating-point bbox-to-pixel rounding -- crop both to the common
    top-left-aligned region rather than assuming exact shape equality."""
    h = min(before.shape[0], after.shape[0])
    w = min(before.shape[1], after.shape[1])
    return before[:h, :w], after[:h, :w]


def detect_changes(
    before: np.ndarray, after: np.ndarray,
    threshold: int = config.PIXEL_DIFF_THRESHOLD,
    min_region_pixels: int = config.MIN_REGION_PIXELS,
) -> ChangeDetectionResult:
    before, after = _align(before, after)

    diff = np.abs(before.astype(np.float64) - after.astype(np.float64)).mean(axis=2)
    raw_mask = diff > threshold

    labeled, n_labels = ndimage.label(raw_mask)
    regions = []
    cleaned_mask = np.zeros_like(raw_mask)
    for label_id in range(1, n_labels + 1):
        region_mask = labeled == label_id
        pixel_count = int(region_mask.sum())
        if pixel_count < min_region_pixels:
            continue
        cleaned_mask |= region_mask
        rows, cols = np.nonzero(region_mask)
        regions.append(ChangeRegion(
            pixel_count=pixel_count,
            centroid_row=float(rows.mean()),
            centroid_col=float(cols.mean()),
            bbox=(int(rows.min()), int(rows.max()), int(cols.min()), int(cols.max())),
        ))
    regions.sort(key=lambda r: r.pixel_count, reverse=True)

    change_pct = 100.0 * cleaned_mask.sum() / cleaned_mask.size

    return ChangeDetectionResult(
        diff=diff, mask=cleaned_mask, regions=regions, change_pct=change_pct,
        threshold=threshold, min_region_pixels=min_region_pixels,
        shape=cleaned_mask.shape,
    )
