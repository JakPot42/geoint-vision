"""pipeline.py — orchestrates search/fetch -> change detection -> vision
analysis -> figure -> PDF, shared by main.py's CLI commands and tests."""
from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np

import config
from change_detection import ChangeDetectionResult, detect_changes
from pdf_report import build_change_brief_pdf
from plots import plot_three_panel
from sentinel2_client import (
    SceneMatch,
    fetch_best_crop,
    load_bundled_demo_image,
)
from vision_analysis import analyze


@dataclass
class AnalysisResult:
    location_name: str
    before: np.ndarray
    after: np.ndarray
    before_date: str
    after_date: str
    before_scene: SceneMatch | None
    after_scene: SceneMatch | None
    change: ChangeDetectionResult
    analysis_text: str


def run_demo() -> AnalysisResult:
    """The flagship demo -- bundled, already-verified real Djibouti
    imagery, no network needed."""
    case = config.DEMO_CASE
    before = load_bundled_demo_image(case["before_image"])
    after = load_bundled_demo_image(case["after_image"])
    change = detect_changes(before, after)
    analysis_text = analyze(before, after, change, case["before_date"], case["after_date"])
    return AnalysisResult(
        location_name=case["name"], before=before, after=after,
        before_date=case["before_date"], after_date=case["after_date"],
        before_scene=None, after_scene=None, change=change, analysis_text=analysis_text,
    )


def run_live_analysis(
    lat: float, lon: float, before_range: tuple[str, str], after_range: tuple[str, str],
    location_name: str = "Custom location", margin: float = config.DEFAULT_MARGIN_DEG,
) -> AnalysisResult:
    """General-purpose live pipeline: real STAC search + real COG crop for
    any coordinates and date ranges."""
    before, before_scene = fetch_best_crop(lat, lon, *before_range, margin=margin)
    after, after_scene = fetch_best_crop(lat, lon, *after_range, margin=margin)
    change = detect_changes(before, after)
    before_date = before_scene.datetime[:10]
    after_date = after_scene.datetime[:10]
    analysis_text = analyze(before, after, change, before_date, after_date)
    return AnalysisResult(
        location_name=location_name, before=before, after=after,
        before_date=before_date, after_date=after_date,
        before_scene=before_scene, after_scene=after_scene,
        change=change, analysis_text=analysis_text,
    )


def build_outputs(result: AnalysisResult, output_dir: str = config.OUTPUT_DIR) -> tuple[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    figure_path = os.path.join(output_dir, "change_detection.png")
    plot_three_panel(result.before, result.after, result.change, result.before_date, result.after_date, result.location_name, figure_path)
    pdf_path = os.path.join(output_dir, "geoint_change_brief.pdf")
    build_change_brief_pdf(pdf_path, figure_path, result.analysis_text, result.location_name, result.before_date, result.after_date)
    return figure_path, pdf_path
