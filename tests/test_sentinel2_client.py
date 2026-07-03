import pytest

import config
from sentinel2_client import fetch_best_crop, load_bundled_demo_image, search_scenes


def test_load_bundled_demo_images_are_real_and_correct_shape():
    before = load_bundled_demo_image(config.DEMO_CASE["before_image"])
    after = load_bundled_demo_image(config.DEMO_CASE["after_image"])
    assert before.dtype.name == "uint8"
    assert before.shape[2] == 3   # RGB
    assert before.shape[0] > 100 and before.shape[1] > 100
    assert after.shape[0] > 100


def test_search_scenes_live_returns_sorted_by_cloud_cover():
    matches = search_scenes(config.DEMO_CASE["lat"], config.DEMO_CASE["lon"], "2018-01-01", "2018-06-30")
    assert len(matches) > 0
    clouds = [m.cloud_cover for m in matches]
    assert clouds == sorted(clouds)


def test_search_scenes_finds_the_known_demo_scene():
    matches = search_scenes(config.DEMO_CASE["lat"], config.DEMO_CASE["lon"], "2018-05-25", "2018-05-27")
    assert any(m.scene_id == config.DEMO_CASE["before_scene_id"] for m in matches)


def test_fetch_best_crop_matches_known_scene():
    crop, scene = fetch_best_crop(config.DEMO_CASE["lat"], config.DEMO_CASE["lon"], "2018-05-25", "2018-05-27")
    assert scene.scene_id == config.DEMO_CASE["before_scene_id"]
    assert crop.shape[2] == 3


def test_fetch_best_crop_raises_on_no_scenes():
    # Date range entirely before Sentinel-2A's June 2015 launch -- no scenes
    # can exist for any location, regardless of cloud cover or tile coverage.
    with pytest.raises(ValueError, match="No Sentinel-2 scenes"):
        fetch_best_crop(config.DEMO_CASE["lat"], config.DEMO_CASE["lon"], "2000-01-01", "2000-01-02")
