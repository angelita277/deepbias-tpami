"""Figure 4 — fig:proposer_diversity.

8-panel grid (2x4) of diversity / concentration metrics computed over the
real Age-bias Proposer outputs at four stages (Seed, Pre-DPO, Iter 1, Iter 2),
for two target LVLMs (InternVL3-8B, Qwen2.5-VL-7B).

Metrics:
  1. Effective Topic Count   (count of KMeans clusters with >=1 hit)
  2. Topic Entropy           (Shannon entropy of cluster-size distribution, nats)
  3. Distinct-2              (unique-bigram / total-bigram ratio)
  4. Unique-Instruction Ratio
  5. Mean Pairwise Cosine    (sentence-embedding similarity, lower = more spread)
  6. Centroid Distance       (mean distance of points to group centroid)
  7. Self-BLEU               (corpus self-BLEU on a 200-sample subset)
  8. Vocabulary Size         (# unique lowercase tokens)
"""
import os
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from _common import (
    PROPOSER_ORDER, TARGET_COLORS,
    get_sentence_encoder, load_proposer_texts, load_seed_bbq_age,
    save_fig, setup_matplotlib,
)

STAGE_X_ORDER = ["Seed", "Pre-DPO", "Iter 1", "Iter 2"]
STAGE_KEY = {
    "Seed":     "Seed (BBQ)",
    "Pre-DPO":  "Pre-DPO",
    "Iter 1":   "DPO Iter 1",
    "Iter 2":   "DPO Iter 2",
}


def _tokens(text):
    return re.findall(r"[a-z][a-z\-']*", text.lower())


def vocab_size(texts):
    vocab = set()
    for t in texts:
        vocab.update(_tokens(t))
    return len(vocab)


def distinct_n(texts, n=2):
    bigrams_total = 0
    bigrams_unique = set()
    for t in texts:
        toks = _tokens(t)
        for i in range(len(toks) - n + 1):
            bigrams_total += 1
            bigrams_unique.add(tuple(toks[i:i + n]))
    return len(bigrams_unique) / bigrams_total if bigrams_total else 0.0


def unique_ratio(texts):
    return len(set(t.strip().lower() for t in texts)) / max(len(texts), 1)


def self_bleu_corpus(texts, max_pairs=200, ngram=4):
    """Approximate corpus self-BLEU: for each of `max_pairs` sampled texts,
    compute BLEU against the rest of the corpus and average."""
    from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
    sf = SmoothingFunction().method1
    rng = np.random.default_rng(0)
    if len(texts) <= 1:
        return 0.0
    sample_idx = rng.choice(len(texts), size=min(max_pairs, len(texts)), replace=False)
    bleus = []
    tok_all = [_tokens(t) for t in texts]
    for i in sample_idx:
        refs = [tok_all[j] for j in range(len(texts)) if j != i]
        # Use a small reference set to keep this tractable.
        ref_idx = rng.choice(len(refs), size=min(40, len(refs)), replace=False)
        refs_sub = [refs[k] for k in ref_idx]
        cand = tok_all[i]
        if not cand or not refs_sub:
            continue
        b = sentence_bleu(refs_sub, cand,
                          weights=tuple([1.0/ngram] * ngram),
                          smoothing_function=sf)
        bleus.append(b)
    return float(np.mean(bleus)) if bleus else 0.0


def cosine_metrics(emb, max_pairs=2000, rng_seed=0):
    """Compute mean pairwise cosine similarity (subsampled) and centroid distance.

    `emb` must already be L2-normalised."""
    rng = np.random.default_rng(rng_seed)
    n = len(emb)
    if n < 2:
        return 0.0, 0.0
    pairs = rng.integers(0, n, size=(max_pairs, 2))
    pairs = pairs[pairs[:, 0] != pairs[:, 1]]
    sims = (emb[pairs[:, 0]] * emb[pairs[:, 1]]).sum(axis=1)
    mean_sim = float(np.mean(sims))
    centroid = emb.mean(axis=0)
    centroid /= max(np.linalg.norm(centroid), 1e-9)
    dists = np.linalg.norm(emb - centroid, axis=1)
    return mean_sim, float(np.mean(dists))


def topic_metrics_kmeans(stage_texts_emb, n_clusters=60, rng_seed=0):
    """Fit KMeans on the union of all texts, then compute per-stage effective
    topic count + Shannon entropy.

    `stage_texts_emb` is dict[stage_label] -> np.ndarray (n_i, d) embeddings."""
    from sklearn.cluster import KMeans
    all_emb = np.vstack([v for v in stage_texts_emb.values()])
    km = KMeans(n_clusters=n_clusters, random_state=rng_seed, n_init=4)
    km.fit(all_emb)

    out = {}
    for stage, emb in stage_texts_emb.items():
        labels = km.predict(emb)
        counts = np.bincount(labels, minlength=n_clusters).astype(float)
        eff_count = int((counts > 0).sum())
        p = counts / counts.sum()
        p = p[p > 0]
        entropy = float(-(p * np.log(p)).sum())  # nats
        out[stage] = (eff_count, entropy)
    return out


def collect_metrics(target, per_stage=400, seed_max=200, rng_seed=0):
    rng = np.random.default_rng(rng_seed)
    proposer = load_proposer_texts(target=target)
    seed = load_seed_bbq_age()

    layers = {}
    for x_label, src_label in STAGE_KEY.items():
        if src_label == "Seed (BBQ)":
            raw = seed
            cap = seed_max
        else:
            raw = proposer[src_label]
            cap = per_stage
        if len(raw) > cap:
            idx = rng.choice(len(raw), cap, replace=False)
            chosen = [raw[i] for i in idx]
        else:
            chosen = list(raw)
        layers[x_label] = chosen

    enc = get_sentence_encoder()
    stage_emb = {
        stage: enc.encode(texts, batch_size=64, show_progress_bar=False,
                          normalize_embeddings=True)
        for stage, texts in layers.items()
    }
    topic_out = topic_metrics_kmeans(stage_emb, n_clusters=60)

    metrics = {m: [] for m in [
        "Effective Topic Count", "Topic Entropy", "Distinct-2",
        "Unique-Instruction Ratio", "Mean Pairwise Cosine Sim.",
        "Centroid Distance", "Self-BLEU", "Vocabulary Size",
    ]}
    for stage in STAGE_X_ORDER:
        texts = layers[stage]
        emb = stage_emb[stage]

        v = vocab_size(texts)
        d2 = distinct_n(texts, 2)
        ur = unique_ratio(texts)
        cos, cdist = cosine_metrics(emb)
        sb = self_bleu_corpus(texts, max_pairs=120, ngram=4)
        eff_t, ent = topic_out[stage]

        metrics["Effective Topic Count"].append(eff_t)
        metrics["Topic Entropy"].append(ent)
        metrics["Distinct-2"].append(d2)
        metrics["Unique-Instruction Ratio"].append(ur)
        metrics["Mean Pairwise Cosine Sim."].append(cos)
        metrics["Centroid Distance"].append(cdist)
        metrics["Self-BLEU"].append(sb)
        metrics["Vocabulary Size"].append(v)

    return metrics


def main():
    plt = setup_matplotlib()
    print("[diversity] computing for InternVL3-8B target ...")
    metrics_intern = collect_metrics(target="intern3", rng_seed=0)
    print("[diversity] computing for Qwen2.5-VL-7B target ...")
    metrics_qwen = collect_metrics(target="qwen25", rng_seed=1)

    panels = list(metrics_intern.keys())
    n_panels = len(panels)
    n_cols = 4
    n_rows = (n_panels + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(13.0, 5.6))
    axes = axes.ravel()
    x = np.arange(len(STAGE_X_ORDER))

    for i, name in enumerate(panels):
        ax = axes[i]
        y_intern = metrics_intern[name]
        y_qwen = metrics_qwen[name]
        ax.plot(x, y_intern, color=TARGET_COLORS["InternVL3-8B"],
                marker="o", markersize=5, linewidth=1.6,
                label="InternVL3-8B")
        ax.plot(x, y_qwen, color=TARGET_COLORS["Qwen2.5-VL-7B"],
                marker="s", markersize=5, linewidth=1.6,
                label="Qwen2.5-VL-7B")
        ax.set_xticks(x)
        ax.set_xticklabels(STAGE_X_ORDER, fontsize=9)
        ax.set_title(name, fontsize=10.5)
        ax.grid(True, linestyle="--", linewidth=0.4, alpha=0.5)
        ax.tick_params(axis="y", labelsize=8)

    # Hide any unused axes.
    for j in range(n_panels, len(axes)):
        axes[j].axis("off")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2,
               bbox_to_anchor=(0.5, 1.03), fontsize=10, frameon=True)
    fig.suptitle("Diversity & Concentration Metrics across Proposer DPO Iterations (Age bias)",
                 y=1.08, fontsize=11.5)
    fig.tight_layout()

    save_fig(fig, "proposer_diversity")
    plt.close(fig)
    print("[diversity] saved -> proposer_diversity.pdf")


if __name__ == "__main__":
    main()
