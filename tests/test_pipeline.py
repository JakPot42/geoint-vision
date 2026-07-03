import os

import pipeline
import config


def test_run_demo_returns_expected_structure():
    result = pipeline.run_demo()
    assert result.location_name == config.DEMO_CASE["name"]
    assert result.before_date == config.DEMO_CASE["before_date"]
    assert result.after_date == config.DEMO_CASE["after_date"]
    assert result.change.change_pct > 0


def test_run_live_analysis_matches_bundled_demo_exactly():
    live = pipeline.run_live_analysis(
        config.DEMO_CASE["lat"], config.DEMO_CASE["lon"],
        ("2018-01-01", "2018-06-30"), ("2019-09-01", "2019-12-31"),
        location_name="Live test",
    )
    assert live.before_scene.scene_id == config.DEMO_CASE["before_scene_id"]
    assert live.after_scene.scene_id == config.DEMO_CASE["after_scene_id"]


def test_build_outputs_creates_real_files(tmp_path):
    result = pipeline.run_demo()
    figure_path, pdf_path = pipeline.build_outputs(result, output_dir=str(tmp_path))
    assert os.path.exists(figure_path)
    assert os.path.exists(pdf_path)
    with open(pdf_path, "rb") as f:
        assert f.read(4) == b"%PDF"
