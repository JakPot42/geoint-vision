"""Rich terminal dashboard — ASCII-safe (box.ASCII2) for Windows cp1252
console compatibility, same convention as every other CLI in this
portfolio."""
from __future__ import annotations

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import config

console = Console(width=115)

_BANNER = "[bold cyan]GEOINT Vision Pipeline[/bold cyan]  [dim]v1.0[/dim]"


def print_banner() -> None:
    console.print()
    console.print(_BANNER)
    console.print(Panel(config.SCOPE_DISCLAIMER, box=box.ASCII2, border_style="yellow", title="[bold yellow]Scope[/bold yellow]"))


def print_scene_table(matches, title: str) -> None:
    console.rule(f"[bold]{title}[/bold]")
    t = Table(box=box.ASCII2)
    t.add_column("Date")
    t.add_column("Cloud %", justify="right")
    t.add_column("Scene ID", overflow="fold")
    for m in matches:
        t.add_row(m.datetime[:10], f"{m.cloud_cover:.1f}", m.scene_id)
    console.print(t)


def print_change_summary(result) -> None:
    console.rule(f"[bold]{result.location_name}[/bold] -- {result.before_date} vs {result.after_date}")
    console.print(f"Change flagged: {result.change.change_pct:.1f}% of frame, "
                   f"{len(result.change.regions)} region(s) >= {result.change.min_region_pixels}px "
                   f"(threshold: mean RGB diff > {result.change.threshold})")
    if result.change.regions:
        t = Table(box=box.ASCII2)
        t.add_column("Rank", justify="right")
        t.add_column("Pixels", justify="right")
        t.add_column("Centroid (row, col)")
        for i, r in enumerate(result.change.regions[:8], start=1):
            t.add_row(str(i), str(r.pixel_count), f"({r.centroid_row:.0f}, {r.centroid_col:.0f})")
        console.print(t)


def print_analysis(text: str) -> None:
    console.rule("[bold]Change Analysis[/bold]")
    console.print(text)
    console.print()
