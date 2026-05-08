"""Figure 8 — fig:benchmark_difficulty.

Per-instance bias accuracy histogram across the six anchor LVLMs, stacked by
demographic category (Age / Gender / Race).

Each surviving triplet in `voting_eval/dedup/{age,gender,race}_final_survivors.json`
is decomposed into N independent single-image instances (Age/Race: N=3,
Gender: N=2). For each instance we compute:

    accuracy_i = #{anchors whose label on image i == unknown_letter} / 6

`unknown_letter` is taken from the `voting_chain` round that the survivor was
sampled from (its `source_stage`); for `proposer_*` survivors we fall back to
`round0_voting`. This handles the option-shuffle that DeepAgent applies in
round 2/3 (where Unknown may be A or B rather than C).

The histogram bins {0/6, 1/6, ..., 6/6} → 7 bars; bars are stacked by
category. A vertical dashed line marks the overall median.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from _common import CATEGORY_COLORS, CATEGORY_ORDER, REPO, save_fig, setup_matplotlib

ANCHORS = ["intern35", "qwen3vl", "glm4v", "dsvl2", "gemma3", "onevision"]


def _unknown_letter(row):
    ss = row.get("source_stage", "")
    chain = row.get("voting_chain", {}) or {}
    if ss.startswith("deep_round"):
        rk = ss.replace("deep_", "") + "_voting"
    else:
        rk = "round0_voting"
    return chain.get(rk, {}).get("unknown_letter", "C")


def per_instance_accuracies(rows):
    """For each survivor row produce N float accuracies in [0, 1] (one per image)."""
    accs = []
    for r in rows:
        ulet = _unknown_letter(r)
        per_anchor = r.get("per_anchor_labels", {}) or {}
        n_imgs = r.get("n_images", 0)
        if not n_imgs:
            continue
        for img_idx in range(n_imgs):
            hits = 0
            valid = 0
            for a in ANCHORS:
                labs = per_anchor.get(a)
                if not labs or img_idx >= len(labs):
                    continue
                lab = labs[img_idx]
                if lab is None or lab == "":
                    continue
                valid += 1
                if lab == ulet:
                    hits += 1
            if valid == 0:
                continue
            # Normalize to /6 — if some anchor missing (rare: onevision Race idx=430),
            # we use the valid count as denominator and round to nearest sixth.
            acc = hits / valid
            accs.append(acc)
    return np.array(accs, dtype=float)


def load_per_category():
    base = REPO / "voting_eval" / "dedup"
    files = {
        "Age":    base / "age_final_survivors.json",
        "Gender": base / "gender_final_survivors.json",
        "Race":   base / "race_final_survivors.json",
    }
    out = {}
    for cat, path in files.items():
        rows = []
        with open(path) as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                rows.append(json.loads(ln))
        accs = per_instance_accuracies(rows)
        out[cat] = accs
        print(f"[diff] {cat}: {len(rows)} survivors, {len(accs)} instances, "
              f"mean={accs.mean():.3f} median={np.median(accs):.3f}")
    return out


def main():
    plt = setup_matplotlib()
    accs_per_cat = load_per_category()

    # 7 bins corresponding to {0/6, 1/6, ..., 6/6}.
    bin_edges = np.linspace(-1 / 12, 1 + 1 / 12, 8)  # centers at k/6
    centers = np.array([k / 6 for k in range(7)])

    counts = {cat: np.histogram(accs_per_cat[cat], bins=bin_edges)[0]
              for cat in CATEGORY_ORDER}

    all_accs = np.concatenate([accs_per_cat[c] for c in CATEGORY_ORDER])
    median_overall = float(np.median(all_accs))
    mean_overall = float(np.mean(all_accs))

    fig, ax = plt.subplots(figsize=(7.4, 4.2))

    width = 0.13
    bottom = np.zeros_like(centers, dtype=float)
    for cat in CATEGORY_ORDER:
        c = counts[cat].astype(float)
        ax.bar(centers, c, width=width, bottom=bottom,
               color=CATEGORY_COLORS[cat], edgecolor="white",
               linewidth=0.6, label=cat)
        bottom += c

    # Median dashed line.
    ax.axvline(median_overall, linestyle="--", color="#444", linewidth=1.2,
               label=f"Overall median = {median_overall*100:.0f}%")

    ax.set_xlabel("Per-instance bias accuracy (% of 6 anchors returning Unknown)",
                  fontsize=10.5)
    ax.set_ylabel("Number of instances", fontsize=10.5)
    ax.set_xticks(centers)
    ax.set_xticklabels([f"{int(round(v*100))}%" for v in centers], fontsize=9)
    ax.tick_params(axis="y", labelsize=9)
    ax.set_xlim(centers[0] - width, centers[-1] + width)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.4, alpha=0.5)

    # Total instances annotation.
    n_total = sum(len(accs_per_cat[c]) for c in CATEGORY_ORDER)
    ax.text(0.99, 0.97,
            f"N = {n_total:,} single-image instances\n"
            f"mean = {mean_overall*100:.1f}%   median = {median_overall*100:.0f}%",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=9, color="#333",
            bbox=dict(boxstyle="round,pad=0.32", facecolor="white",
                      edgecolor="#bbb", alpha=0.9))

    ax.legend(loc="upper left", fontsize=9, frameon=True)
    fig.suptitle("DeepBias Benchmark — Per-Instance Difficulty Distribution",
                 fontsize=12, y=0.995)
    fig.tight_layout()

    save_fig(fig, "benchmark_difficulty")
    plt.close(fig)
    print(f"[diff] saved -> benchmark_difficulty.pdf "
          f"(N={n_total}, mean={mean_overall:.3f}, median={median_overall:.3f})")


if __name__ == "__main__":
    main()
