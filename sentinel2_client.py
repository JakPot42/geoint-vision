"""sentinel2_client.py — live, unauthenticated Sentinel-2 imagery access.

Real ESA/Copernicus Sentinel-2 imagery via AWS's Element84 "Earth Search"
STAC API (catalog search) and the public e84-earth-search-sentinel-data S3
bucket (actual Cloud-Optimized GeoTIFF pixel data) -- zero registration,
zero authentication, confirmed live during this build. See README "Data
sourcing" for why this replaces the (decommissioned) Copernicus Open
Access Hub named in the original spec.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import requests

import config

_SEARCH_URL = f"{config.STAC_API_URL}/search"


@dataclass
class SceneMatch:
    scene_id: str
    datetime: str
    cloud_cover: float
    visual_href: str


def search_scenes(
    lat: float, lon: float, start_date: str, end_date: str,
    margin: float = config.DEFAULT_MARGIN_DEG, limit: int = 20,
) -> list[SceneMatch]:
    """Searches the real Sentinel-2 catalog for scenes covering (lat, lon)
    in the given date range, sorted by cloud cover (clearest first)."""
    bbox = [lon - margin, lat - margin, lon + margin, lat + margin]
    body = {
        "collections": [config.SENTINEL2_COLLECTION],
        "bbox": bbox,
        "datetime": f"{start_date}T00:00:00Z/{end_date}T23:59:59Z",
        "limit": limit,
        "sortby": [{"field": "properties.eo:cloud_cover", "direction": "asc"}],
    }
    resp = requests.post(_SEARCH_URL, json=body, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return [
        SceneMatch(
            scene_id=f["id"],
            datetime=f["properties"]["datetime"],
            cloud_cover=f["properties"].get("eo:cloud_cover", float("nan")),
            visual_href=f["assets"]["visual"]["href"],
        )
        for f in data["features"]
    ]


def fetch_crop(visual_href: str, lat: float, lon: float, margin: float = config.DEFAULT_MARGIN_DEG) -> np.ndarray:
    """Windowed read of a real Cloud-Optimized GeoTIFF via HTTP range
    requests (rasterio/GDAL) -- pulls only the pixels near (lat, lon), not
    the full ~110km tile. Returns an (H, W, 3) uint8 RGB array."""
    import rasterio
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds

    bbox = (lon - margin, lat - margin, lon + margin, lat + margin)
    with rasterio.open(visual_href) as src:
        projected_bounds = transform_bounds("EPSG:4326", src.crs, *bbox)
        window = from_bounds(*projected_bounds, transform=src.transform)
        data = src.read(window=window)
    return np.moveaxis(data, 0, -1)


def fetch_best_crop(
    lat: float, lon: float, start_date: str, end_date: str,
    margin: float = config.DEFAULT_MARGIN_DEG,
) -> tuple[np.ndarray, SceneMatch]:
    """Finds the clearest real scene in the date range and returns its
    cropped pixels + metadata. Raises if nothing matches."""
    matches = search_scenes(lat, lon, start_date, end_date, margin=margin)
    if not matches:
        raise ValueError(f"No Sentinel-2 scenes found for ({lat}, {lon}) between {start_date} and {end_date}.")
    best = matches[0]
    crop = fetch_crop(best.visual_href, lat, lon, margin=margin)
    return crop, best


def load_bundled_demo_image(path: str) -> np.ndarray:
    """Loads one of the bundled, already-verified real demo images (no
    network needed) -- used by `geoint demo`."""
    from PIL import Image
    return np.array(Image.open(path).convert("RGB"))
