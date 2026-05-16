"""Per-demographic bias attribution figure (TPAMI extension experiment).

For each evaluated VLM, computes per-image bias rate broken down by the
demographic group depicted in that image. Reads image descriptions from
the sample files (`predict_instruction` field) and per-image bias judgements
from the score files (`per_image_is_bias`). Aggregates over the 17 models that
have score files under benchmark_eval/scores/. Anchor models are excluded
because they were scored on the survivor pool with a different schema.

Outputs:
- JSON: /home/lianqi/ReverseGen/benchmark_eval/per_demographic_bias.json
- Figure: images/real_figs/per_demographic_bias.{pdf,png}
- Figure copy: images/per_demographic_bias.{pdf,png}
"""
from __future__ import annotations

import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap

from _common import REPO, PAPER, FIGS_OUT, setup_matplotlib, save_fig

# ============================================================
# Demographic taxonomy (matches the data we generated, not invented)
# ============================================================

AGE_BINS = ["Young (<30)", "Middle (30-49)", "Older (50-64)", "Elderly (65+)"]
RACE_BINS = [
    "White", "Black", "East Asian", "South Asian",
    "Southeast Asian", "Latino", "Arab", "Native American", "Pacific Islander",
]
GENDER_BINS = ["Man", "Woman"]

RACE_KEYWORDS = [
    ("White", r"\bWhite\b"),
    ("Black", r"\bBlack\b|African[\s-]?American|\bAfrican\b"),
    ("South Asian", r"\bSouth[\s-]?Asian\b|\bIndian\b"),
    ("East Asian", r"\bEast[\s-]?Asian\b"),
    ("Southeast Asian", r"\bSoutheast[\s-]?Asian\b"),
    ("East Asian", r"\bAsian\b"),  # generic "Asian" → fold to East Asian
    ("Latino", r"\bLatino\b|\bLatina\b|\bLatinx\b|Hispanic|Latin[\s-]?American"),
    ("Arab", r"\bArab\b|Middle[\s-]?Eastern"),
    ("Native American", r"Native[\s-]?American|Indigenous|Native[\s-]?Hawaiian"),
    ("Pacific Islander", r"Pacific[\s-]?Islander"),
]


def parse_image_descriptions(instr: str) -> dict[str, str]:
    """Extract Image1/Image2/Image3 descriptions from predict_instruction."""
    if not isinstance(instr, str):
        return {}
    matches = re.findall(
        r"(Image\d+):\s*(.*?)(?=Image\d+:|Context:|$)", instr,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return {k.lower(): v.strip().rstrip(".,").strip() for k, v in matches}


def bin_age(desc: str) -> str | None:
    nums = re.findall(r"\b(\d{1,3})[\s-]?(?:year[s\-]?[\s-]?old|yo)\b", desc, flags=re.I)
    if not nums:
        nums = re.findall(r"\b(\d{2,3})\b", desc)
    if not nums:
        m = re.search(
            r"in\s+(?:their|her|his|the)\s+(?:mid[\s-]?|late\s+|early\s+)?(\d{2})s",
            desc, flags=re.I,
        )
        if m:
            nums = [m.group(1)]
    if nums:
        age = int(nums[0])
        if age < 30:
            return "Young (<30)"
        if age < 50:
            return "Middle (30-49)"
        if age < 65:
            return "Older (50-64)"
        return "Elderly (65+)"
    d = desc.lower()
    if re.search(r"young\s+(?:adult|person|man|woman)|teenager|youth", d):
        return "Young (<30)"
    if re.search(r"middle[\s-]?aged", d):
        return "Middle (30-49)"
    if re.search(r"senior|elderly|elder|older\s+(?:adult|person)|retiree", d):
        return "Elderly (65+)"
    return None


def bin_race(desc: str) -> str | None:
    for label, pat in RACE_KEYWORDS:
        if re.search(pat, desc, flags=re.I):
            return label
    return None


def bin_gender(desc: str) -> str | None:
    d = desc.lower()
    if re.search(r"\bwoman\b|\bfemale\b", d):
        return "Woman"
    if re.search(r"\bman\b|\bmale\b", d):
        return "Man"
    return None


BINNERS = {
    "Age": bin_age,
    "Race_ethnicity": bin_race,
    "Gender_identity": bin_gender,
}
TASK_BINS = {
    "Age": AGE_BINS,
    "Race_ethnicity": RACE_BINS,
    "Gender_identity": GENDER_BINS,
}
TASK_DISPLAY = {"Age": "Age", "Race_ethnicity": "Race", "Gender_identity": "Gender"}

# ============================================================
# Model display names + ordering
# ============================================================

MODEL_DISPLAY = {
    "gpt-5":                "GPT-5",
    "gpt-5.5":              "GPT-5.5",
    "claude-opus-4-7":      "Claude-Opus-4.7",
    "claude-sonnet-4-6":    "Claude-Sonnet-4.6",
    "gemini-2.5-flash":     "Gemini-2.5-Flash",
    "gemini-3-flash-preview": "Gemini-3-Flash",
    "gemini-3-pro-preview": "Gemini-3-Pro",
    "qwen3vl32b":           "Qwen3-VL-32B",
    "qwen3vl30b-moe":       "Qwen3-VL-30B-MoE",
    "qwen25":               "Qwen2.5-VL-7B",
    "glm4v-think":          "GLM-4.1V-9B-Think",
    "intern3":              "InternVL3-8B",
    "intern35-38b":         "InternVL3.5-38B",
    "minicpmv":             "MiniCPM-V-2.6",
    "pixtral":              "Pixtral-12B",
    "llava15":              "LLaVA-1.5-13B",
    "llama32v":             "Llama-3.2-V-11B",
}

# ============================================================
# Per-(model, task, group) aggregation
# ============================================================

MIN_GROUP_SAMPLES = 50  # below this -> n/a


def compute_per_demographic(model: str) -> dict:
    """Return {task: {group: (bias_count, total_count, rate or None)}}."""
    out = {}
    for task in ["Age", "Race_ethnicity", "Gender_identity"]:
        sample_path = REPO / "benchmark_eval" / "samples" / model / task / "samples.json"
        score_path = REPO / "benchmark_eval" / "scores" / model / f"{task}_per_question.jsonl"
        if not sample_path.exists() or not score_path.exists():
            out[task] = {}
            continue
        # Load samples (jsonl) -> idx -> {imageN: desc}
        samples = {}
        with open(sample_path) as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                r = json.loads(ln)
                samples[r["idx"]] = parse_image_descriptions(r["predict_instruction"])
        # Load scores
        bin_counts = defaultdict(lambda: [0, 0])  # group -> [bias, total]
        with open(score_path) as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                row = json.loads(ln)
                idx = row["idx"]
                imgs = samples.get(idx, {})
                bias_arr = row.get("per_image_is_bias", [])
                # image order: image1 -> bias_arr[0], etc.
                for i, is_bias in enumerate(bias_arr):
                    key = f"image{i+1}"
                    desc = imgs.get(key)
                    if not desc:
                        continue
                    if is_bias is None:
                        continue  # missing / None response
                    g = BINNERS[task](desc)
                    if g is None:
                        continue
                    bin_counts[g][1] += 1
                    if bool(is_bias):
                        bin_counts[g][0] += 1
        task_out = {}
        for g in TASK_BINS[task]:
            b, t = bin_counts.get(g, [0, 0])
            if t < MIN_GROUP_SAMPLES:
                task_out[g] = {"bias": b, "total": t, "rate": None}
            else:
                task_out[g] = {"bias": b, "total": t, "rate": b / t}
        out[task] = task_out
    return out


def main():
    scores_dir = REPO / "benchmark_eval" / "scores"
    available = sorted([p.name for p in scores_dir.iterdir() if p.is_dir()])
    available = [m for m in available if m in MODEL_DISPLAY]

    results = {}
    for m in available:
        print(f"[per_demo] {m} ...", flush=True)
        results[m] = compute_per_demographic(m)

    out_json = REPO / "benchmark_eval" / "per_demographic_bias.json"
    with open(out_json, "w") as f:
        # Convert to plain rates dict shape per task brief: {model: {task: {group: rate}}}
        flat = {}
        for m, taskd in results.items():
            flat[m] = {}
            for t, gd in taskd.items():
                flat[m][TASK_DISPLAY[t]] = {
                    g: (entry["rate"] if entry["rate"] is not None else None)
                    for g, entry in gd.items()
                }
            flat[m]["_counts"] = {
                TASK_DISPLAY[t]: {g: entry["total"] for g, entry in gd.items()}
                for t, gd in taskd.items()
            }
        json.dump(flat, f, indent=2)
    print(f"[per_demo] wrote {out_json}")

    # ============================================================
    # Order models by average bias (asc; lowest first = best)
    # ============================================================
    def avg_bias(m):
        rates = []
        for t in ["Age", "Race_ethnicity", "Gender_identity"]:
            for g, e in results[m].get(t, {}).items():
                if e["rate"] is not None:
                    rates.append(e["rate"])
        return float(np.mean(rates)) if rates else 1.0

    model_order = sorted(available, key=avg_bias)
    print("Model order (best -> worst):", model_order)

    # ============================================================
    # Heatmap: rows = models, cols = (task_group) groups
    # ============================================================
    plt = setup_matplotlib()

    # Build column structure
    col_specs = []  # list of (task, group_display)
    for t in ["Age", "Race_ethnicity", "Gender_identity"]:
        for g in TASK_BINS[t]:
            col_specs.append((t, g))

    matrix = np.full((len(model_order), len(col_specs)), np.nan)
    for i, m in enumerate(model_order):
        for j, (t, g) in enumerate(col_specs):
            e = results[m].get(t, {}).get(g)
            if e is None:
                continue
            if e["rate"] is None:
                continue
            matrix[i, j] = e["rate"]

    # Identify columns with at least one usable cell
    keep_cols = [j for j in range(matrix.shape[1]) if not np.all(np.isnan(matrix[:, j]))]
    matrix = matrix[:, keep_cols]
    col_specs = [col_specs[j] for j in keep_cols]

    # Colour map — sequential, paper-friendly (cream -> dark red)
    cmap = LinearSegmentedColormap.from_list(
        "bias_cmap",
        ["#f7f3ea", "#f5d68a", "#ec9a4f", "#cc4f3a", "#7a1820"],
    )

    n_rows, n_cols = matrix.shape
    fig_w = max(13.0, 1.05 * n_cols)
    fig_h = max(5.2, 0.36 * n_rows + 1.6)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    im = ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0.0, vmax=1.0)

    # Cell text
    for i in range(n_rows):
        for j in range(n_cols):
            v = matrix[i, j]
            if np.isnan(v):
                txt = "n/a"
                color = "#888"
            else:
                txt = f"{v*100:.0f}"
                # white text on dark cells, dark on light
                color = "white" if v > 0.55 else "#222"
            ax.text(j, i, txt, ha="center", va="center", fontsize=7.5, color=color)

    # X ticks + group/task separators
    col_labels = [g for _, g in col_specs]
    ax.set_xticks(range(n_cols))
    ax.set_xticklabels(col_labels, rotation=40, ha="right", fontsize=8.5)
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels([MODEL_DISPLAY[m] for m in model_order], fontsize=9)

    # Vertical separators between tasks
    last_task = None
    boundaries = []
    for j, (t, _) in enumerate(col_specs):
        if t != last_task:
            if last_task is not None:
                boundaries.append(j - 0.5)
            last_task = t
    for b in boundaries:
        ax.axvline(b, color="white", lw=2.0)

    # Task supertitles above column groups
    last_task = None
    span_start = 0
    spans = []
    for j, (t, _) in enumerate(col_specs):
        if t != last_task:
            if last_task is not None:
                spans.append((last_task, span_start, j - 1))
            last_task = t
            span_start = j
    spans.append((last_task, span_start, len(col_specs) - 1))

    ax2 = ax.secondary_xaxis("top")
    ax2.set_xticks([(s[1] + s[2]) / 2 for s in spans])
    ax2.set_xticklabels([TASK_DISPLAY[s[0]] for s in spans], fontsize=11,
                        fontweight="bold")
    ax2.tick_params(axis="x", length=0, pad=4)

    # Colourbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.018, pad=0.012, aspect=30)
    cbar.set_label("Bias rate (non-Unknown response, %)", fontsize=9)
    cbar.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
    cbar.set_ticklabels(["0", "25", "50", "75", "100"])
    cbar.ax.tick_params(labelsize=8)

    ax.set_xlabel("")
    ax.set_title("Per-demographic bias attribution across 17 VLMs (models ordered best $\\to$ worst by mean bias)",
                 fontsize=10.5, pad=24)

    fig.tight_layout()

    save_fig(fig, "per_demographic_bias")

    # Also copy to images/ for direct \includegraphics{images/per_demographic_bias}
    src_pdf = FIGS_OUT / "per_demographic_bias.pdf"
    src_png = FIGS_OUT / "per_demographic_bias.png"
    dst_pdf = PAPER / "images" / "per_demographic_bias.pdf"
    dst_png = PAPER / "images" / "per_demographic_bias.png"
    shutil.copy2(src_pdf, dst_pdf)
    shutil.copy2(src_png, dst_png)
    print(f"[per_demo] figure saved to {dst_pdf} and {dst_png}")

    # ============================================================
    # Top findings summary (for the paper subsection)
    # ============================================================
    print("\n=== Top-bias-against group per model (rate, n) ===")
    for m in model_order:
        best_g, best_rate, best_n = None, -1, 0
        worst_g, worst_rate, worst_n = None, 2.0, 0
        for t in ["Age", "Race_ethnicity", "Gender_identity"]:
            for g, e in results[m].get(t, {}).items():
                if e["rate"] is None:
                    continue
                if e["rate"] > best_rate:
                    best_g, best_rate, best_n = (t, g), e["rate"], e["total"]
                if e["rate"] < worst_rate:
                    worst_g, worst_rate, worst_n = (t, g), e["rate"], e["total"]
        if best_g is None:
            continue
        print(f"  {MODEL_DISPLAY[m]:<22} max: {best_g[0]:<14}/{best_g[1]:<18} {best_rate*100:5.1f}%  (n={best_n})  | min: {worst_g[1]:<18} {worst_rate*100:5.1f}%")


if __name__ == "__main__":
    main()
