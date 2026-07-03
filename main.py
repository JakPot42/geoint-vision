"""GEOINT Vision Pipeline CLI.

Claude-vision-powered change detection and briefing on real, public
Sentinel-2 imagery -- NOT a validated computer vision research system,
NOT an intelligence determination. See config.SCOPE_DISCLAIMER, printed
on every command.
"""
from __future__ import annotations

import os
import sys

import click

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import dashboard
import pipeline
from dashboard import console
from sentinel2_client import search_scenes


@click.group()
def cli() -> None:
    """GEOINT Vision Pipeline: real Sentinel-2 imagery, deterministic
    pixel-difference change detection, Claude vision analysis.

    \b
    NOT a validated computer vision research system. No local ML/
    segmentation model. Every finding requires human GEOINT analyst
    review before any use.
    """


@cli.command()
def demo() -> None:
    """Flagship demo: Chinese PLA Support Base, Djibouti -- bundled,
    already-verified real imagery, no network or API key needed."""
    dashboard.print_banner()
    result = pipeline.run_demo()
    dashboard.print_change_summary(result)
    dashboard.print_analysis(result.analysis_text)
    figure_path, pdf_path = pipeline.build_outputs(result)
    console.print(f"Saved figure: {figure_path}")
    console.print(f"Saved PDF brief: {pdf_path}")
    if config.DEMO_MODE:
        console.print("[dim]DEMO_MODE=True -- change analysis used a deterministic pixel-diff template, not a live Claude vision call.[/dim]")


@cli.command()
@click.option("--lat", type=float, required=True)
@click.option("--lon", type=float, required=True)
@click.option("--before-start", required=True, help="Start of the 'before' date range (YYYY-MM-DD).")
@click.option("--before-end", required=True, help="End of the 'before' date range (YYYY-MM-DD).")
@click.option("--after-start", required=True, help="Start of the 'after' date range (YYYY-MM-DD).")
@click.option("--after-end", required=True, help="End of the 'after' date range (YYYY-MM-DD).")
@click.option("--name", default="Custom location", help="Label for the report.")
@click.option("--margin", type=float, default=config.DEFAULT_MARGIN_DEG, help="Crop half-width in degrees.")
def analyze(lat: float, lon: float, before_start: str, before_end: str, after_start: str, after_end: str, name: str, margin: float) -> None:
    """Live analysis for any coordinates: real Sentinel-2 search + crop +
    change detection + vision brief. Picks the clearest (lowest-cloud)
    scene in each date range.

    \b
    Example: geoint analyze --lat 11.59265 --lon 43.06049 \\
      --before-start 2018-01-01 --before-end 2018-06-30 \\
      --after-start 2019-09-01 --after-end 2019-12-31 \\
      --name "Djibouti PLA base"
    """
    dashboard.print_banner()
    try:
        result = pipeline.run_live_analysis(
            lat, lon, (before_start, before_end), (after_start, after_end),
            location_name=name, margin=margin,
        )
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1)

    dashboard.print_change_summary(result)
    dashboard.print_analysis(result.analysis_text)
    figure_path, pdf_path = pipeline.build_outputs(result)
    console.print(f"Saved figure: {figure_path}")
    console.print(f"Saved PDF brief: {pdf_path}")
    if config.DEMO_MODE:
        console.print("[dim]DEMO_MODE=True -- change analysis used a deterministic pixel-diff template, not a live Claude vision call.[/dim]")


@cli.command()
@click.option("--lat", type=float, required=True)
@click.option("--lon", type=float, required=True)
@click.option("--start", required=True, help="YYYY-MM-DD")
@click.option("--end", required=True, help="YYYY-MM-DD")
def search(lat: float, lon: float, start: str, end: str) -> None:
    """List real available Sentinel-2 scenes for a location/date range,
    sorted by cloud cover -- use this to pick good before/after dates."""
    dashboard.print_banner()
    matches = search_scenes(lat, lon, start, end)
    if not matches:
        console.print("[yellow]No scenes found for that location/date range.[/yellow]")
        return
    dashboard.print_scene_table(matches, f"Sentinel-2 scenes near ({lat}, {lon}), {start} to {end}")


if __name__ == "__main__":
    cli()
