import base64

import numpy as np

import config
from change_detection import detect_changes
from sentinel2_client import load_bundled_demo_image
from vision_analysis import _encode_png, analyze


def _real_change_result():
    before = load_bundled_demo_image(config.DEMO_CASE["before_image"])
    after = load_bundled_demo_image(config.DEMO_CASE["after_image"])
    return before, after, detect_changes(before, after)


def test_encode_png_produces_valid_base64():
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    encoded = _encode_png(img)
    raw = base64.b64decode(encoded)
    assert raw[:8] == b"\x89PNG\r\n\x1a\n"   # PNG magic bytes


def test_demo_mode_returns_factual_template_with_real_stats():
    before, after, result = _real_change_result()
    text = analyze(before, after, result, "2018-05-26", "2019-10-23")
    assert config.SCOPE_DISCLAIMER in text
    assert "34.4%" in text
    assert "ANTHROPIC_API_KEY" in text   # honest disclosure that live vision wasn't run


def test_analyze_falls_back_to_template_when_claude_call_fails(monkeypatch):
    monkeypatch.setattr(config, "DEMO_MODE", False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    before, after, result = _real_change_result()
    text = analyze(before, after, result, "2018-05-26", "2019-10-23")
    assert "PIXEL-DIFFERENCE ANALYSIS" in text   # fell back to template, didn't crash


def test_template_never_invents_a_region_that_does_not_exist():
    before, after, result = _real_change_result()
    text = analyze(before, after, result, "2018-05-26", "2019-10-23")
    assert f"{len(result.regions)} contiguous changed region(s)" in text
