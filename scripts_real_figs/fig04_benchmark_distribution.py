"""Figure 6 — fig:benchmark_distribution.

Two panels (saved separately):
  - benchmark_distribution_umap.pdf : 2D UMAP overlay of the distilled
    benchmark question embeddings, coloured by demographic category.
  - benchmark_distribution_radar.pdf : 10-topic BERTopic-style radar of
    topic coverage per category.

Source data: voting_eval/dedup/{age,race,gender}_final_survivors.json (the
final SemDeDup-distilled candidate pool used as the released benchmark).
"""
import os
import sys
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from _common import (
    BENCHMARK_TOPICS, CATEGORY_COLORS, CATEGORY_ORDER,
    get_sentence_encoder, load_final_survivors,
    save_fig, setup_matplotlib, survivor_question_text,
    topic_distribution,
)


def collect_data(per_cat=500, rng_seed=0):
    rng = np.random.default_rng(rng_seed)
    survivors = load_final_survivors()
    out = {}
    for cat in CATEGORY_ORDER:
        rows = survivors[cat]
        texts = [survivor_question_text(r) for r in rows]
        texts = [t for t in texts if t and len(t) > 30]
        if len(texts) > per_cat:
            idx = rng.choice(len(texts), per_cat, replace=False)
            texts = [texts[i] for i in idx]
        out[cat] = texts
    return out


def panel_umap(layers, out_name="benchmark_distribution_umap"):
    plt = setup_matplotlib()
    enc = get_sentence_encoder()

    flat_text, flat_label = [], []
    for cat in CATEGORY_ORDER:
        for t in layers[cat]:
            flat_text.append(t)
            flat_label.append(cat)
    flat_label = np.array(flat_label)
    print(f"[bench-umap] encoding {len(flat_text)} texts")
    emb = enc.encode(flat_text, batch_size=64, show_progress_bar=False,
                     normalize_embeddings=True)

    import umap
    reducer = umap.UMAP(
        n_components=2, n_neighbors=40, min_dist=0.40, spread=1.2,
        metric="cosine", random_state=11,
    )
    xy = reducer.fit_transform(emb)
    keep = (np.abs(xy[:, 0] - np.median(xy[:, 0])) < 6 * np.std(xy[:, 0])) & \
           (np.abs(xy[:, 1] - np.median(xy[:, 1])) < 6 * np.std(xy[:, 1]))
    xy = xy[keep]; flat_label = flat_label[keep]
    xy = xy - xy.mean(0)
    span = np.percentile(np.abs(xy), 99)
    xy = xy / max(span, 1e-6) * 4.5

    fig, ax = plt.subplots(figsize=(5.4, 4.2))
    for cat in CATEGORY_ORDER:
        m = flat_label == cat
        n = int(m.sum())
        ax.scatter(xy[m, 0], xy[m, 1],
                   s=11, alpha=0.55, linewidths=0,
                   color=CATEGORY_COLORS[cat],
                   label=f"{cat} (n={n})")
    ax.set_xlabel("UMAP-1")
    ax.set_ylabel("UMAP-2")
    ax.set_title("(a) Final Benchmark Semantic Space (UMAP)", fontsize=11)
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.4)
    leg = ax.legend(loc="upper left", fontsize=9, frameon=True,
                    handletextpad=0.5, borderpad=0.4)
    leg.get_frame().set_alpha(0.85)

    save_fig(fig, out_name)
    plt.close(fig)
    print(f"[bench-umap] saved -> {out_name}.pdf")


def panel_radar(layers, out_name="benchmark_distribution_radar"):
    plt = setup_matplotlib()

    series = {}
    for cat in CATEGORY_ORDER:
        series[cat] = topic_distribution(layers[cat], BENCHMARK_TOPICS)

    n_topics = len(BENCHMARK_TOPICS)
    angles = np.linspace(0, 2 * np.pi, n_topics, endpoint=False).tolist()
    angles_loop = angles + angles[:1]

    fig = plt.figure(figsize=(6.6, 5.6))
    ax = fig.add_axes([0.13, 0.05, 0.64, 0.78], projection="polar")
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    for cat in CATEGORY_ORDER:
        vals = series[cat].tolist()
        vals_loop = vals + vals[:1]
        c = CATEGORY_COLORS[cat]
        ax.plot(angles_loop, vals_loop, color=c, linewidth=1.7, label=cat)
        ax.fill(angles_loop, vals_loop, color=c, alpha=0.18)

    ax.set_xticks(angles)
    ax.set_xticklabels([t for t, _ in BENCHMARK_TOPICS], fontsize=9.5)
    rmax = max(0.30, max(max(s) for s in series.values()) * 1.10)
    ax.set_ylim(0, rmax)
    ticks = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
    ticks = [v for v in ticks if v <= rmax]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{int(v*100)}%" for v in ticks], fontsize=8, color="#555")
    ax.tick_params(axis="x", pad=10)
    ax.set_rlabel_position(35)

    fig.suptitle("(b) Topic Coverage by Demographic Category (BERTopic-style)",
                 fontsize=11, y=0.97)
    leg = ax.legend(loc="upper right", bbox_to_anchor=(1.50, 1.08),
                    fontsize=9.5, frameon=True)
    leg.get_frame().set_alpha(0.88)

    save_fig(fig, out_name)
    plt.close(fig)
    print(f"[bench-radar] saved -> {out_name}.pdf")


def main():
    layers = collect_data(per_cat=500, rng_seed=0)
    sizes = {k: len(v) for k, v in layers.items()}
    print("layer sizes:", sizes)
    panel_umap(layers)
    panel_radar(layers)


if __name__ == "__main__":
    main()
