"""Figure 3 — fig:proposer_distribution (Age bias).

Four panels saved as separate PDFs and laid out side-by-side via \\subfloat:
  (a) proposer_distribution_umap_intern3.pdf  — UMAP for InternVL3-8B target
  (b) proposer_distribution_umap_qwen25.pdf   — UMAP for Qwen2.5-VL-7B target
  (c) proposer_distribution_radar_intern3.pdf — 10-topic radar (InternVL3-8B)
  (d) proposer_distribution_radar_qwen25.pdf  — 10-topic radar (Qwen2.5-VL-7B)

All four panels are rendered using the *full* Proposer corpus per stage
(no per-stage subsampling); only the Seed (BBQ) layer is bounded by the size
of VLBBQ Age (234 questions).
"""
import os
import sys

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from _common import (
    PROPOSER_COLORS, PROPOSER_ORDER, PROPOSER_TOPICS,
    get_sentence_encoder, load_proposer_texts, load_seed_bbq_age,
    save_fig, setup_matplotlib, topic_distribution,
)

TARGET_LABEL = {
    "intern3": "InternVL3-8B",
    "qwen25": "Qwen2.5-VL-7B",
}


def collect_data(target):
    """Return dict[stage_label] -> list[str], using all available texts."""
    proposer = load_proposer_texts(target=target)
    seed = load_seed_bbq_age()
    return {
        "Seed (BBQ)":   list(seed),
        "Pre-DPO":      list(proposer["Pre-DPO"]),
        "DPO Iter 1":   list(proposer["DPO Iter 1"]),
        "DPO Iter 2":   list(proposer["DPO Iter 2"]),
    }


def panel_umap(layers, target, panel_letter):
    plt = setup_matplotlib()
    enc = get_sentence_encoder()

    flat_text, flat_label = [], []
    for label in PROPOSER_ORDER:
        for t in layers[label]:
            flat_text.append(t)
            flat_label.append(label)
    flat_label = np.array(flat_label)
    print(f"[umap-{target}] encoding {len(flat_text)} texts (full corpus)")
    emb = enc.encode(flat_text, batch_size=128, show_progress_bar=False,
                     normalize_embeddings=True)

    import umap
    reducer = umap.UMAP(
        n_components=2, n_neighbors=50, min_dist=0.40, spread=1.2,
        metric="cosine", random_state=11,
    )
    xy = reducer.fit_transform(emb)

    keep = (np.abs(xy[:, 0] - np.median(xy[:, 0])) < 6 * np.std(xy[:, 0])) & \
           (np.abs(xy[:, 1] - np.median(xy[:, 1])) < 6 * np.std(xy[:, 1]))
    xy = xy[keep]
    flat_label = flat_label[keep]
    xy = xy - xy.mean(0)
    span = np.percentile(np.abs(xy), 99)
    xy = xy / max(span, 1e-6) * 4.5

    # Compact figsize for 4-panel horizontal layout (~0.245\textwidth each).
    fig, ax = plt.subplots(figsize=(3.4, 2.9))

    plot_order = sorted(
        PROPOSER_ORDER, key=lambda lbl: -int((flat_label == lbl).sum())
    )
    # Slightly thinner scatter so denser corpora don't overwhelm.
    for label in plot_order:
        m = flat_label == label
        ax.scatter(xy[m, 0], xy[m, 1],
                   s=4.5, alpha=0.22, linewidths=0,
                   color=PROPOSER_COLORS[label])

    from scipy.stats import gaussian_kde
    grid_x = np.linspace(xy[:, 0].min(), xy[:, 0].max(), 220)
    grid_y = np.linspace(xy[:, 1].min(), xy[:, 1].max(), 220)
    GX, GY = np.meshgrid(grid_x, grid_y)
    points = np.vstack([GX.ravel(), GY.ravel()])

    handles_for_legend = []
    for label in PROPOSER_ORDER:
        m = flat_label == label
        if m.sum() < 25:
            continue
        kde = gaussian_kde(xy[m].T, bw_method=0.30)
        Z = kde(points).reshape(GX.shape)
        levels = [Z.max() * 0.35, Z.max() * 0.65]
        c = PROPOSER_COLORS[label]
        ax.contour(GX, GY, Z, levels=levels, colors=[c],
                   linewidths=[1.0, 1.4])
        ax.contourf(GX, GY, Z, levels=[Z.max() * 0.65, Z.max()],
                    colors=[c], alpha=0.18)
        cx, cy = xy[m].mean(axis=0)
        ax.scatter([cx], [cy], s=80, marker="X", color=c,
                   edgecolor="white", linewidth=1.0, zorder=5)
        handles_for_legend.append((label, int(m.sum())))

    from matplotlib.lines import Line2D
    proxies = []
    for label, n in handles_for_legend:
        proxies.append(Line2D([0], [0], marker="o",
                              markerfacecolor=PROPOSER_COLORS[label],
                              markeredgecolor="none", markersize=6,
                              linestyle="none", label=f"{label} (n={n:,})"))
    leg = ax.legend(handles=proxies, loc="upper left",
                    fontsize=6.6, frameon=True,
                    handletextpad=0.4, borderpad=0.3, labelspacing=0.25)
    leg.get_frame().set_alpha(0.85)

    ax.set_xlabel("UMAP-1", fontsize=8.5)
    ax.set_ylabel("UMAP-2", fontsize=8.5)
    ax.set_title(f"({panel_letter}) {TARGET_LABEL[target]} — UMAP",
                 fontsize=9.5)
    ax.tick_params(axis="both", labelsize=7)
    ax.grid(True, linestyle="--", linewidth=0.4, alpha=0.4)
    ax.set_aspect("equal", adjustable="datalim")
    fig.tight_layout()

    out_name = f"proposer_distribution_umap_{target}"
    save_fig(fig, out_name)
    plt.close(fig)
    print(f"[umap-{target}] saved -> {out_name}.pdf")


def panel_radar(layers, target, panel_letter, share_rmax=None):
    plt = setup_matplotlib()

    series = {}
    for label in PROPOSER_ORDER:
        series[label] = topic_distribution(layers[label], PROPOSER_TOPICS)

    n_topics = len(PROPOSER_TOPICS)
    angles = np.linspace(0, 2 * np.pi, n_topics, endpoint=False).tolist()
    angles_loop = angles + angles[:1]

    fig = plt.figure(figsize=(3.6, 3.0))
    ax = fig.add_axes([0.10, 0.04, 0.72, 0.78], projection="polar")
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    for label in PROPOSER_ORDER:
        vals = series[label].tolist()
        vals_loop = vals + vals[:1]
        c = PROPOSER_COLORS[label]
        ax.plot(angles_loop, vals_loop, color=c, linewidth=1.3, label=label)
        ax.fill(angles_loop, vals_loop, color=c, alpha=0.13)

    ax.set_xticks(angles)
    ax.set_xticklabels([t for t, _ in PROPOSER_TOPICS], fontsize=6.4)
    if share_rmax is not None:
        rmax = share_rmax
    else:
        rmax = max(0.25, max(max(s) for s in series.values()) * 1.10)
    ax.set_ylim(0, rmax)
    ticks = [v for v in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40] if v <= rmax]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{int(v*100)}%" for v in ticks], fontsize=5.8, color="#555")
    ax.tick_params(axis="x", pad=4)
    ax.set_rlabel_position(35)

    fig.suptitle(f"({panel_letter}) {TARGET_LABEL[target]} — Topic Radar",
                 fontsize=9.5, y=0.99)

    leg = ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.20),
                    ncol=2, fontsize=6.4, frameon=True,
                    handletextpad=0.4, columnspacing=0.8, borderpad=0.3)
    leg.get_frame().set_alpha(0.88)

    out_name = f"proposer_distribution_radar_{target}"
    save_fig(fig, out_name)
    plt.close(fig)
    print(f"[radar-{target}] saved -> {out_name}.pdf")


def main():
    layers_by_target = {tgt: collect_data(tgt) for tgt in ("intern3", "qwen25")}
    for tgt, layers in layers_by_target.items():
        sizes = {k: len(v) for k, v in layers.items()}
        print(f"[{tgt}] layer sizes:", sizes, "total =", sum(sizes.values()))

    # Determine a shared rmax across both radars so they're visually comparable.
    shared_rmax = 0.0
    for tgt, layers in layers_by_target.items():
        for label in PROPOSER_ORDER:
            s = topic_distribution(layers[label], PROPOSER_TOPICS)
            shared_rmax = max(shared_rmax, float(s.max()))
    shared_rmax = max(0.25, shared_rmax * 1.12)

    panel_letters_umap = {"intern3": "a", "qwen25": "b"}
    panel_letters_radar = {"intern3": "c", "qwen25": "d"}

    for tgt, layers in layers_by_target.items():
        panel_umap(layers, target=tgt, panel_letter=panel_letters_umap[tgt])
        panel_radar(layers, target=tgt, panel_letter=panel_letters_radar[tgt],
                    share_rmax=shared_rmax)


if __name__ == "__main__":
    main()
