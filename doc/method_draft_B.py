"""Method figure draft — Option B: full benchmark-construction scope
(§4.1 + §4.2 wrapped by the §4.3 ensemble).

Difference from Option A:
  * The DPO inner loop is driven by an ensemble of 6 anchor LVLMs rather than
    a single target (consensus preference labelling).
  * After DeepAgent, candidate triplets pass a K=6 validity check with
    threshold rho(Q) > tau = 1/3 before landing in the DeepBias benchmark.

Run:
    python3 doc/method_draft_B.py
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(__file__), 'figure_mockups',
                   'method_draft_B.png')
rng = np.random.default_rng(13)

fig = plt.figure(figsize=(18, 10.8))
ax = fig.add_axes((0, 0, 1, 1))
ax.set_xlim(0, 18)
ax.set_ylim(0, 10.8)
ax.axis('off')


def anchor_column(x0, y0, n=6, tag_prefix='M'):
    """Draw a vertical column of n small LVLM icons, return y-centers."""
    ys = []
    for k in range(n):
        cy = y0 - k * 0.32
        ax.add_patch(FancyBboxPatch((x0, cy - 0.11), 0.55, 0.22,
                                    boxstyle='round,pad=0.01',
                                    facecolor='#fff5e0', edgecolor='#c77a2c',
                                    lw=0.7))
        ax.text(x0 + 0.275, cy, f'{tag_prefix}$_{k+1}$',
                ha='center', va='center', fontsize=8, color='#7a4a10')
        ys.append(cy)
    return ys


# ---------------------------------------------------------------------------
# Top band: Proposer
# ---------------------------------------------------------------------------
band_y = 9.9
ax.add_patch(FancyBboxPatch((0.3, band_y), 17.4, 0.55,
                            boxstyle='round,pad=0.02',
                            facecolor='#DDE9F5', edgecolor='#4a79b8', lw=1.0))
ax.text(9.0, band_y + 0.28,
        'Proposer — Adversarial Evolution via DPO, '
        'ENSEMBLE-DRIVEN CONSENSUS LABELLING  (distribution-level)',
        ha='center', va='center', fontsize=12, fontweight='bold',
        color='#1f3d63')

# Four panels: Seed, Expanded, DPO Iter 1, DPO Iter 2
panel_specs = [
    dict(title='Seed pool\n(BBQ / VLBiasBench)', n=25,
         center=(0.0, 0.0), spread=0.55, color='#888'),
    dict(title='Expanded candidate batch\n(frozen exemplar pool)', n=220,
         center=(0.15, 0.05), spread=1.1, color='#6E8FC3'),
    dict(title='DPO Iter 1 distribution\n(ensemble consensus)', n=220,
         center=(0.55, 0.25), spread=1.0, color='#3E6CA6'),
    dict(title='DPO Iter 2 distribution\n(converged)', n=220,
         center=(0.95, 0.55), spread=0.95, color='#1F3D63'),
]

panel_w, panel_h = 3.4, 2.75
panel_y = 6.55
panel_xs = [0.6, 4.6, 8.6, 12.6]

for (x0, spec) in zip(panel_xs, panel_specs):
    ax.add_patch(FancyBboxPatch((x0, panel_y), panel_w, panel_h,
                                boxstyle='round,pad=0.02',
                                facecolor='#F7FAFE', edgecolor='#4a79b8',
                                lw=1.1))
    ax.text(x0 + panel_w / 2, panel_y + panel_h - 0.32,
            spec['title'], ha='center', va='top',
            fontsize=10, fontweight='bold', color='#1f3d63')
    sx0, sx1 = x0 + 0.4, x0 + panel_w - 0.4
    sy0, sy1 = panel_y + 0.3, panel_y + 1.85
    pts = rng.normal(size=(spec['n'], 2)) * spec['spread']
    pts[:, 0] += spec['center'][0] * 2.0
    pts[:, 1] += spec['center'][1] * 1.3
    xs = (pts[:, 0] - pts[:, 0].min()) / (pts[:, 0].max() - pts[:, 0].min() + 1e-9)
    ys = (pts[:, 1] - pts[:, 1].min()) / (pts[:, 1].max() - pts[:, 1].min() + 1e-9)
    xs = sx0 + xs * (sx1 - sx0)
    ys = sy0 + ys * (sy1 - sy0)
    drift = spec['center'][0] * 0.6 * (sx1 - sx0)
    xs = np.clip(xs + drift - 0.3, sx0, sx1)
    ax.scatter(xs, ys, s=14, c=spec['color'], alpha=0.55,
               edgecolors='none', zorder=3)
    ax.annotate('', xy=(sx1, sy0 - 0.05), xytext=(sx0, sy0 - 0.05),
                arrowprops=dict(arrowstyle='->', color='#999', lw=0.8))
    ax.text(sx1, sy0 - 0.22, 'implicitness',
            ha='right', va='top', fontsize=7.5, color='#777', style='italic')

# Arrows between panels
arrow_y = panel_y + panel_h / 2 + 0.3
arrow_labels = [
    ('Expansion', '#4a79b8'),
    ('DPO step\n(6-anchor consensus)', '#4a79b8'),
    ('DPO step', '#4a79b8'),
]
for i, (lbl, col) in enumerate(arrow_labels):
    x_start = panel_xs[i] + panel_w + 0.05
    x_end = panel_xs[i + 1] - 0.05
    arr = FancyArrowPatch((x_start, arrow_y), (x_end, arrow_y),
                          arrowstyle='-|>', mutation_scale=22,
                          color=col, lw=2.0)
    ax.add_patch(arr)
    ax.text((x_start + x_end) / 2, arrow_y + 0.3, lbl,
            ha='center', va='bottom', fontsize=8.5,
            color=col, style='italic')

# Anchor-ensemble side panels feeding into DPO steps (iter 1 and iter 2)
for iter_idx in [1, 2]:
    col_x = (panel_xs[iter_idx] + panel_xs[iter_idx] + panel_w) / 2 \
            if iter_idx == -99 else panel_xs[iter_idx] + panel_w / 2 - 0.275
    # put anchors BELOW the panel, feeding up into it
    anchor_top_y = panel_y - 0.35
    ax.add_patch(FancyBboxPatch((col_x - 0.4, anchor_top_y - 2.3), 1.3, 2.15,
                                boxstyle='round,pad=0.02',
                                facecolor='#FFF7E8', edgecolor='#c77a2c',
                                lw=0.9))
    ax.text(col_x + 0.25, anchor_top_y - 0.25,
            '6 anchor LVLMs', ha='center', va='top',
            fontsize=9, fontweight='bold', color='#7a4a10')
    anchor_column(col_x - 0.3, anchor_top_y - 0.55)
    arr = FancyArrowPatch((col_x + 0.25, anchor_top_y - 0.1),
                          (col_x + 0.25, panel_y + 0.25),
                          arrowstyle='-|>', mutation_scale=18,
                          color='#c77a2c', lw=1.2, linestyle='--')
    ax.add_patch(arr)
    ax.text(col_x + 0.4, (anchor_top_y + panel_y) / 2,
            'consensus\npreference\nlabel',
            ha='left', va='center', fontsize=7.5,
            color='#7a4a10', style='italic')

# ---------------------------------------------------------------------------
# Middle transition band
# ---------------------------------------------------------------------------
# Star sampled from converged pool
star_x = panel_xs[3] + panel_w - 0.9
star_y = panel_y + 1.35
ax.scatter([star_x], [star_y], marker='*', s=260,
           c='#b33a2c', edgecolors='black', linewidths=0.6, zorder=5)
ax.text(star_x + 0.18, star_y, 'candidate\nsampled',
        ha='left', va='center', fontsize=8.2, color='#b33a2c',
        fontweight='bold')
ax.annotate('', xy=(star_x, 4.15), xytext=(star_x, star_y - 0.25),
            arrowprops=dict(arrowstyle='-|>', color='#b33a2c', lw=2.0))

# ---------------------------------------------------------------------------
# Row 2: DeepAgent
# ---------------------------------------------------------------------------
band2_y = 3.65
ax.add_patch(FancyBboxPatch((0.3, band2_y), 17.4, 0.5,
                            boxstyle='round,pad=0.02',
                            facecolor='#DDEEDD', edgecolor='#4a9447', lw=1.0))
ax.text(9.0, band2_y + 0.25,
        'DeepAgent — Multi-Turn Probing  '
        '(instance-level; fixed image triplet; '
        r'$T{=}3$; Deepening / Rewriting)',
        ha='center', va='center', fontsize=12, fontweight='bold',
        color='#1f5c2a')

# Candidate card
card_x, card_y = 0.5, 1.15
card_w, card_h = 3.1, 2.35
ax.add_patch(FancyBboxPatch((card_x, card_y), card_w, card_h,
                            boxstyle='round,pad=0.02',
                            facecolor='white', edgecolor='#4a9447', lw=1.2))
ax.text(card_x + card_w / 2, card_y + card_h - 0.25,
        'Candidate instance',
        ha='center', va='top', fontsize=10, fontweight='bold',
        color='#1f5c2a')
for k in range(3):
    ix = card_x + 0.2 + k * 0.92
    ax.add_patch(FancyBboxPatch((ix, card_y + 1.25), 0.8, 0.65,
                                boxstyle='round,pad=0.01',
                                facecolor='#ececec', edgecolor='#999',
                                lw=0.6))
    ax.text(ix + 0.4, card_y + 1.58, f'$I_{k+1}$',
            ha='center', va='center', fontsize=9, color='#333')
ax.text(card_x + card_w / 2, card_y + 1.1,
        r'$Q_0$ (ambiguous, neg. implied)',
        ha='center', va='center', fontsize=8.5, color='#222', style='italic')
ax.text(card_x + card_w / 2, card_y + 0.65,
        r'$\mathcal{O}=\{\mathrm{Yes},\ \mathrm{No},\ \mathrm{Unknown}\}$',
        ha='center', va='center', fontsize=8.5, color='#222')

# Three turn blocks
turn_y = 1.15
turn_h = 2.35
turn_w = 3.1
turn_xs = [4.0, 7.4, 10.8]
turn_titles = [
    ('Turn 1', 'Rewriting',
     'contextualisation /\nprojection /\nbehav.-tendency /\ncognitive attrib.'),
    ('Turn 2', 'Deepening',
     'attribute refinement /\nscenario deepening /\ncomparison deepening'),
    ('Turn 3', 'Deepening',
     'attribute refinement /\nscenario deepening /\ncomparison deepening'),
]
for (tx, (name, strat, subs)) in zip(turn_xs, turn_titles):
    ax.add_patch(FancyBboxPatch((tx, turn_y), turn_w, turn_h,
                                boxstyle='round,pad=0.02',
                                facecolor='#F4FAF4', edgecolor='#4a9447',
                                lw=1.1))
    ax.text(tx + turn_w / 2, turn_y + turn_h - 0.22,
            f'{name} — {strat}', ha='center', va='top',
            fontsize=9.5, fontweight='bold', color='#1f5c2a')
    ax.text(tx + 0.15, turn_y + turn_h - 0.7, subs,
            ha='left', va='top', fontsize=7.8, color='#355')
    ax.add_patch(FancyBboxPatch((tx + 0.15, turn_y + 0.55), turn_w - 0.3, 0.55,
                                boxstyle='round,pad=0.02',
                                facecolor='white', edgecolor='#7A9FD8',
                                lw=1.0, linestyle='--'))
    ax.text(tx + turn_w / 2, turn_y + 0.82,
            r'$Q_t$ (fixed $I_1,I_2,I_3$)',
            ha='center', va='center', fontsize=8.2, color='#355',
            style='italic')
    ax.add_patch(FancyBboxPatch((tx + 0.15, turn_y + 0.1), turn_w - 0.3, 0.35,
                                boxstyle='round,pad=0.01',
                                facecolor='#f5e0b7', edgecolor='#555',
                                lw=0.5))
    ax.text(tx + turn_w / 2, turn_y + 0.275,
            r'$r_t \in \{\mathrm{Yes},\,\mathrm{No},\,\mathrm{Unknown}\}$',
            ha='center', va='center', fontsize=8.0, color='#111')

for i, x_end in enumerate([turn_xs[0], turn_xs[1], turn_xs[2]]):
    x_start = (card_x + card_w) if i == 0 else (turn_xs[i - 1] + turn_w)
    arr = FancyArrowPatch((x_start + 0.02, turn_y + turn_h / 2),
                          (x_end - 0.02, turn_y + turn_h / 2),
                          arrowstyle='-|>', mutation_scale=18,
                          color='#4a9447', lw=1.7)
    ax.add_patch(arr)

# ---------------------------------------------------------------------------
# Right block: Ensemble validity check + DeepBias benchmark
# ---------------------------------------------------------------------------
valid_x, valid_y = 14.2, 1.15
valid_w, valid_h = 3.5, 2.35
ax.add_patch(FancyBboxPatch((valid_x, valid_y), valid_w, valid_h,
                            boxstyle='round,pad=0.02',
                            facecolor='#FFF7E8', edgecolor='#c77a2c', lw=1.2))
ax.text(valid_x + valid_w / 2, valid_y + valid_h - 0.22,
        'Validity Check\n(K=6 anchor voting)',
        ha='center', va='top', fontsize=10, fontweight='bold',
        color='#7a4a10')

# row of 6 anchors inside the box
anc_y = valid_y + 1.3
for k in range(6):
    ix = valid_x + 0.25 + k * 0.5
    ax.add_patch(FancyBboxPatch((ix, anc_y), 0.42, 0.35,
                                boxstyle='round,pad=0.01',
                                facecolor='#fff5e0', edgecolor='#c77a2c',
                                lw=0.7))
    ax.text(ix + 0.21, anc_y + 0.175, f'$M_{k+1}$',
            ha='center', va='center', fontsize=8, color='#7a4a10')

ax.text(valid_x + valid_w / 2, anc_y - 0.2,
        r'each model answers all 3 images $\Rightarrow$ $K{\times}3=18$ responses',
        ha='center', va='center', fontsize=7.8, color='#7a4a10',
        style='italic')
ax.text(valid_x + valid_w / 2, anc_y - 0.55,
        r'$\rho(Q)=\#\{r=\mathrm{Unknown}\}/18$',
        ha='center', va='center', fontsize=8.5, color='#333')
ax.text(valid_x + valid_w / 2, anc_y - 0.9,
        r'retain iff $\rho(Q) > \tau = 1/3$',
        ha='center', va='center', fontsize=9, fontweight='bold',
        color='#b33a2c')

# Arrow from DeepAgent last turn to validity check
arr = FancyArrowPatch((turn_xs[2] + turn_w + 0.02, turn_y + turn_h / 2),
                      (valid_x - 0.02, turn_y + turn_h / 2),
                      arrowstyle='-|>', mutation_scale=20,
                      color='#4a9447', lw=1.7)
ax.add_patch(arr)
ax.text((turn_xs[2] + turn_w + valid_x) / 2, turn_y + turn_h / 2 + 0.2,
        'candidate\ntriplet',
        ha='center', va='bottom', fontsize=7.8, color='#4a9447',
        style='italic')

# Benchmark deliverable box below
bench_y = 0.2
ax.add_patch(FancyBboxPatch((0.5, bench_y), 17.2, 0.75,
                            boxstyle='round,pad=0.02',
                            facecolor='#F0E6F5', edgecolor='#6a3d9a', lw=1.0))
ax.text(0.75, bench_y + 0.52,
        r'DeepBias benchmark:',
        ha='left', va='center', fontsize=10.5, fontweight='bold',
        color='#4a2a7a')
ax.text(0.75, bench_y + 0.22,
        r'retained triplets decomposed into test instances $(I, Q, \mathcal{O})$; '
        r'Correct$(r)=\mathbb{1}[r{=}\mathrm{Unknown}]$  '
        r'$\Rightarrow$  bias accuracy / elicitation rate',
        ha='left', va='center', fontsize=9, color='#333', style='italic')

# Arrow from validity box down into benchmark
arr = FancyArrowPatch((valid_x + valid_w / 2, valid_y - 0.02),
                      (valid_x + valid_w / 2, bench_y + 0.75 + 0.02),
                      arrowstyle='-|>', mutation_scale=20,
                      color='#6a3d9a', lw=2.0)
ax.add_patch(arr)
ax.text(valid_x + valid_w / 2 + 0.15, (valid_y + bench_y + 0.75) / 2,
        'accept',
        ha='left', va='center', fontsize=8.5, color='#6a3d9a',
        fontweight='bold')

# Title
fig.text(0.5, 0.99,
         'DeepBias Method — Benchmark-Construction View '
         '(6-anchor ensemble drives both consensus labelling and validity voting)',
         ha='center', va='top', fontsize=13.5, fontweight='bold')

plt.savefig(OUT, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()
print('Saved:', OUT)
