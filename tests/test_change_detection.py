import numpy as np
import pytest

import config
from change_detection import detect_changes
from sentinel2_client import load_bundled_demo_image


def test_identical_images_have_zero_change():
    img = np.random.default_rng(0).integers(0, 255, size=(50, 50, 3), dtype=np.uint8)
    r = detect_changes(img, img.copy())
    assert r.change_pct == 0.0
    assert r.regions == []


def test_injected_square_difference_is_detected_at_correct_location():
    rng = np.random.default_rng(1)
    before = rng.integers(0, 50, size=(100, 100, 3), dtype=np.uint8)
    after = before.copy()
    after[20:40, 60:80, :] = 255   # a 20x20 bright square, far from background noise

    r = detect_changes(before, after, threshold=40, min_region_pixels=25)
    assert len(r.regions) == 1
    region = r.regions[0]
    assert region.pixel_count == 400   # 20x20
    assert 20 <= region.centroid_row <= 40
    assert 60 <= region.centroid_col <= 80
    assert region.bbox == (20, 39, 60, 79)


def test_small_region_below_min_pixels_is_dropped_as_noise():
    before = np.zeros((50, 50, 3), dtype=np.uint8)
    after = before.copy()
    after[0:2, 0:2, :] = 255   # 4 pixels, below default min_region_pixels=25
    r = detect_changes(before, after, threshold=40, min_region_pixels=25)
    assert r.regions == []
    assert r.change_pct == 0.0


def test_mismatched_shapes_are_aligned_to_common_size():
    before = np.zeros((50, 60, 3), dtype=np.uint8)
    after = np.zeros((48, 60, 3), dtype=np.uint8)
    after[:, :, :] = 255
    r = detect_changes(before, after, threshold=10, min_region_pixels=1)
    assert r.shape == (48, 60)   # cropped to the smaller common shape


def test_real_djibouti_images_produce_stable_deterministic_stats():
    # Regression guard: this is a pure deterministic computation on fixed
    # bundled real images -- exact values should never drift.
    before = load_bundled_demo_image(config.DEMO_CASE["before_image"])
    after = load_bundled_demo_image(config.DEMO_CASE["after_image"])
    r = detect_changes(before, after)
    assert r.change_pct == pytest.approx(34.37, abs=0.1)
    assert len(r.regions) > 0
    assert r.regions[0].pixel_count == 51029
