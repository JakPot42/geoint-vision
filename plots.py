"""plots.py — the three-panel demo figure: before / after / change-mask
overlay."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from change_detection import ChangeDetectionResult


def plot_three_panel(
    before: np.ndarray, after: np.ndarray, result: ChangeDetectionResult,
    before_date: str, after_date: str, location_name: str, save_path: str,
) -> str:
    h, w = result.shape
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5))

    axes[0].imshow(before[:h, :w])
    axes[0].set_title(f"Before -- {before_date}")
    axes[0].axis("off")

    axes[1].imshow(after[:h, :w])
    axes[1].set_title(f"After -- {after_date}")
    axes[1].axis("off")

    axes[2].imshow(after[:h, :w])
    overlay = np.zeros((h, w, 4))
    overlay[result.mask] = [1.0, 0.1, 0.1, 0.5]
    axes[2].imshow(overlay)
    axes[2].set_title(f"Flagged change ({result.change_pct:.1f}% of frame)")
    axes[2].axis("off")

    fig.suptitle(f"GEOINT Vision Pipeline -- {location_name}", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    return save_path
