"""Figure 7 — fig:benchmark_comparison.

Four-panel horizontal layout comparing DeepBias against four prior bias
benchmarks (BBQ, VLBiasBench, GenderBias-VL, PAIRS) on:
  1. Instance count
  2. Demographic category count
  3. Average bias accuracy on strong LVLMs (lower = harder)
  4. Multimodal input

DeepBias bar is highlighted; others use a uniform grey. Numbers track the
in-text claims in main_real.tex (avg bias accuracy 52% on DeepBias; 69-81%
range on prior benchmarks; 62,457 single-image instances).
"""
import os
import sys

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from _common import save_fig, setup_matplotlib

# Display ordering matches the placeholder layout (Ours rightmost).
BENCHMARKS = ["BBQ", "VLBiasBench", "GenderBias-VL", "PAIRS", "DeepBias\n(Ours)"]
HIGHLIGHT_IDX = 4
COLOR_BASE = "#9aa0a6"
COLOR_OURS = "#e07b26"

# Per-axis values (real numbers; refs in main_real.tex / CLAUDE.md).
INSTANCES = [58_492, 24_000, 10_072, 264, 62_457]
CATEGORIES = [9, 8, 1, 3, 3]
# Average bias accuracy (%) on strong LVLMs — lower is harder.
# Prior benchmarks come in at 69-81 % per main_real.tex; ours = 52 % per §5.4.
BIAS_ACC = [81, 73, 78, 69, 52]
# Multimodal (vision input): 1 = Yes, 0 = No.
MULTIMODAL = [0, 1, 1, 1, 1]


def _bar_colors():
    return [COLOR_OURS if i == HIGHLIGHT_IDX else COLOR_BASE
            for i in range(len(BENCHMARKS))]


def _annotate(ax, vals, fmt="{:,}", fontsize=9.0, dy=0.02):
    ymin, ymax = ax.get_ylim()
    pad = (ymax - ymin) * dy
    for i, v in enumerate(vals):
        if v is None:
            ax.text(i, pad * 0.5, "N/R", ha="center", va="bottom",
                    color="#888", fontsize=fontsize, style="italic")
            continue
        ax.text(i, v + pad, fmt.format(v),
                ha="center", va="bottom", fontsize=fontsize)


def main():
    plt = setup_matplotlib()
    fig, axes = plt.subplots(1, 4, figsize=(13.6, 3.4),
                             gridspec_kw=dict(wspace=0.32))
    x = np.arange(len(BENCHMARKS))
    cols = _bar_colors()

    # --- 1. Instances ---
    ax = axes[0]
    ax.bar(x, INSTANCES, color=cols, edgecolor="none")
    ax.set_title("# Instances", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(BENCHMARKS, rotation=30, fontsize=8.5, ha="right")
    ax.set_ylim(0, max(INSTANCES) * 1.18)
    _annotate(ax, INSTANCES, fmt="{:,}", fontsize=8.5)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.4, alpha=0.5)

    # --- 2. Categories ---
    ax = axes[1]
    ax.bar(x, CATEGORIES, color=cols, edgecolor="none")
    ax.set_title("# Categories", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(BENCHMARKS, rotation=30, fontsize=8.5, ha="right")
    ax.set_ylim(0, max(CATEGORIES) * 1.18 + 0.5)
    _annotate(ax, CATEGORIES, fmt="{}", fontsize=9.0)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.4, alpha=0.5)

    # --- 3. Avg Bias Accuracy ---
    ax = axes[2]
    ax.bar(x, BIAS_ACC, color=cols, edgecolor="none")
    ax.set_title("Avg. Bias Accuracy\non Strong LVLMs (%)", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(BENCHMARKS, rotation=30, fontsize=8.5, ha="right")
    ax.set_ylim(0, 100)
    _annotate(ax, BIAS_ACC, fmt="{}", fontsize=9.0)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.4, alpha=0.5)

    # --- 4. Multimodal ---
    ax = axes[3]
    ax.bar(x, MULTIMODAL, color=cols, edgecolor="none")
    ax.set_title("Multimodal", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(BENCHMARKS, rotation=30, fontsize=8.5, ha="right")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["No", "Yes"], fontsize=9)
    ax.set_ylim(0, 1.25)
    for i, v in enumerate(MULTIMODAL):
        label = "Yes" if v == 1 else "No"
        ax.text(i, v + 0.04, label, ha="center", va="bottom", fontsize=9)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.4, alpha=0.5)

    fig.suptitle("DeepBias vs. Prior Bias Benchmarks — Axis-by-Axis Comparison",
                 fontsize=12.5, y=1.04)

    save_fig(fig, "benchmark_comparison")
    plt.close(fig)
    print("[bench-cmp] saved -> benchmark_comparison.pdf")


if __name__ == "__main__":
    main()
