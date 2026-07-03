"""config.py — scope disclaimer, demo case, and thresholds. No logic here.

======================================================================
MANDATORY, NON-NEGOTIABLE FRAMING
======================================================================
This is a Claude-vision-powered change-detection and briefing tool, NOT
a validated computer vision research system. It does not run any local
segmentation/detection model (no LLaVA, no SAM, no object counting
algorithm) -- deterministic pixel-difference thresholding flags WHERE
change occurred; Claude's vision capability is what DESCRIBES what the
change looks like. Neither step makes an intelligence determination,
an attribution claim, or a capability/threat assessment. Sentinel-2's
public bands are 10m/pixel at best -- individual people, vehicles, and
most equipment are not resolvable; only large structures, land clearing,
and construction are. Every output states these limits and requires
human GEOINT analyst review before any use.
======================================================================
"""
from __future__ import annotations

import os

DEMO_MODE = os.environ.get("DEMO_MODE", "True") == "True"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"   # vision-capable; same model used for every Claude call in this project

SCOPE_DISCLAIMER = (
    "Claude-vision-powered change detection and briefing tool -- NOT a "
    "validated computer vision research system, NOT an intelligence "
    "determination. No local ML/segmentation model is used. Sentinel-2 "
    "imagery is 10m/pixel at best -- individuals, vehicles, and most "
    "equipment are not resolvable; only large structures and construction "
    "activity are. Every finding requires human GEOINT analyst review "
    "before any use."
)

# ---------------------------------------------------------------------------
# Data source: AWS Element84 "Earth Search" STAC API + the public
# e84-earth-search-sentinel-data S3 bucket -- real ESA Sentinel-2 imagery,
# zero registration, zero authentication. CLAUDE.md named the "Copernicus
# Open Access Hub API," which was decommissioned in October 2023 (replaced
# by the Copernicus Data Space Ecosystem, which requires a registered
# account). This is a real, live, unauthenticated public mirror of the
# same Copernicus/ESA Sentinel-2 archive -- verified working during this
# build. See README "Data sourcing" for the full account.
# ---------------------------------------------------------------------------
STAC_API_URL = "https://earth-search.aws.element84.com/v1"
SENTINEL2_COLLECTION = "sentinel-2-c1-l2a"   # "Collection 1" reprocessing; public bucket, no requester-pays
DEFAULT_MARGIN_DEG = 0.02   # ~4.4 km box around the target coordinate

# ---------------------------------------------------------------------------
# Flagship demo: Chinese PLA Support Base, Djibouti. Real, public,
# well-documented change -- a 300m+ pier was built at the base between
# 2018 and 2019 (Forbes, "Satellite Images Show That Chinese Navy Is
# Expanding Overseas Base," May 2020; USNI News, "AFRICOM: Chinese Naval
# Base in Africa Set to Support Aircraft Carriers," April 2021). Both
# demo images were pulled and verified live from the public Sentinel-2
# mirror during this build -- not fabricated.
# ---------------------------------------------------------------------------
DEMO_CASE = {
    "name": "Chinese PLA Support Base, Djibouti",
    "lat": 11.59265, "lon": 43.06049,
    "location_citation": "Publicly reported coordinates (Wikipedia, "
                           "'People's Liberation Army Support Base in "
                           "Djibouti,' citing open-source GEOINT reporting).",
    "before_date": "2018-05-26",
    "before_image": "data/djibouti_before_2018-05-26.png",
    "before_scene_id": "S2B_T38PKT_20180526T074312_L2A",
    "after_date": "2019-10-23",
    "after_image": "data/djibouti_after_2019-10-23.png",
    "after_scene_id": "S2A_T38PKT_20191023T073537_L2A",
    "event_citation": "Forbes, 'Satellite Images Show That Chinese Navy "
                        "Is Expanding Overseas Base' (H I Sutton, May 10, "
                        "2020); USNI News, 'AFRICOM: Chinese Naval Base "
                        "in Africa Set to Support Aircraft Carriers' "
                        "(April 20, 2021). Both report a large new pier "
                        "(300m+) constructed at the base beginning ~2018, "
                        "essentially complete by late 2019.",
}

# ---------------------------------------------------------------------------
# Deterministic change detection -- disclosed thresholds, not tuned/trained.
# ---------------------------------------------------------------------------
PIXEL_DIFF_THRESHOLD = 40       # mean abs RGB difference (0-255) to flag a pixel as "changed"
MIN_REGION_PIXELS = 25          # connected-component regions smaller than this are treated as noise

OUTPUT_DIR = "output"
