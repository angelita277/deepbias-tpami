"""Method figure draft — Option A: single-target scope (§4.1 + §4.2).

Design principles:
  * Proposer is DISTRIBUTION-LEVEL. Shown as a 2D scatter cloud that shifts
    across Expansion -> DPO Iter 1 -> DPO Iter 2, not as one evolving question.
  * DeepAgent is INSTANCE-LEVEL. Shown as a multi-turn dialogue on one
    candidate sampled from the converged Proposer pool.
  * Only paper-attested vocabulary: responses are r in {Yes, No, Unknown};
    strategies are Deepening and Rewriting with the 7 sub-strategies.

Run:
    python3 doc/method_draft_A.py
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

OUT = os.path.join(os.path.dirname(__file__), 'figure_mockups',
                   'method_draft_A.png')
rng = np.random.default_rng(7)

fig = plt.figure(figsize=(18, 9.6))
ax = fig.add_axes((0, 0, 1, 1))
ax.set_xlim(0, 18)
ax.set_ylim(0, 9.6)
ax.axis('off')

# ---------------------------------------------------------------------------
# ROW 1 (top): Proposer as distribution
# ---------------------------------------------------------------------------
row1_y_band = 8.6  # header band y
ax.add_patch(FancyBboxPatch((0.3, row1_y_band), 17.4, 0.55,
                            boxstyle='round,pad=0.02',
                            facecolor='#DDE9F5', edgecolor='#4a79b8', lw=1.0))
ax.text(9.0, row1_y_band + 0.28,
        'Proposer — Adversarial Evolution via DPO  '
        '(distribution-level, iterative; '
        r'$\pi_{\mathrm{ref}}$ = base LVLM, no SFT)',
        ha='center', va='center', fontsize=12, fontweight='bold',
        color='#1f3d63')

# Four panels along row 1: Seed, Expanded, DPO Iter 1, DPO Iter 2
panel_specs = [
    dict(title='Seed pool\n(BBQ / VLBiasBench)', n=25,
         center=(0.0, 0.0), spread=0.55, color='#888'),
    dict(title='Expanded candidate batch\n(frozen exemplar pool, SDXL-rendered)',
         n=220, center=(0.15, 0.05), spread=1.1, color='#6E8FC3'),
    dict(title='DPO Iter 1 distribution', n=220,
         center=(0.55, 0.25), spread=1.0, color='#3E6CA6'),
    dict(title='DPO Iter 2 distribution\n(converged)', n=220,
         center=(0.95, 0.55), spread=0.95, color='#1F3D63'),
]

panel_w, panel_h = 3.4, 2.9
panel_y = 4.9
panel_xs = [0.6, 4.6, 8.6, 12.6]

for (x0, spec) in zip(panel_xs, panel_specs):
    # panel frame
    ax.add_patch(FancyBboxPatch((x0, panel_y), panel_w, panel_h,
                                boxstyle='round,pad=0.02',
                                facecolor='#F7FAFE', edgecolor='#4a79b8',
                                lw=1.1))
    # title
    ax.text(x0 + panel_w / 2, panel_y + panel_h - 0.32,
            spec['title'], ha='center', va='top',
            fontsize=10, fontweight='bold', color='#1f3d63')
    # scatter: local coords -> panel coords
    cx_local, cy_local = spec['center']
    # Draw into a subregion [x0+0.4, x0+panel_w-0.4] x [panel_y+0.3, panel_y+1.95]
    sx0, sx1 = x0 + 0.4, x0 + panel_w - 0.4
    sy0, sy1 = panel_y + 0.3, panel_y + 1.95
    pts = rng.normal(size=(spec['n'], 2)) * spec['spread']
    pts[:, 0] += cx_local * 2.0  # amplify horizontal drift
    pts[:, 1] += cy_local * 1.3
    # map to panel rect (clip roughly by scaling)
    xs = (pts[:, 0] - pts[:, 0].min()) / (pts[:, 0].max() - pts[:, 0].min() + 1e-9)
    ys = (pts[:, 1] - pts[:, 1].min()) / (pts[:, 1].max() - pts[:, 1].min() + 1e-9)
    xs = sx0 + xs * (sx1 - sx0)
    ys = sy0 + ys * (sy1 - sy0)
    # shift the cloud horizontally within the panel to show directional drift
    drift = cx_local * 0.6 * (sx1 - sx0)
    xs = np.clip(xs + drift - 0.3, sx0, sx1)
    ax.scatter(xs, ys, s=14, c=spec['color'], alpha=0.55,
               edgecolors='none', zorder=3)
    # axes hint inside panel
    ax.annotate('', xy=(sx1, sy0 - 0.05), xytext=(sx0, sy0 - 0.05),
                arrowprops=dict(arrowstyle='->', color='#999', lw=0.8))
    ax.text(sx1, sy0 - 0.22, 'implicitness',
            ha='right', va='top', fontsize=7.5, color='#777', style='italic')
    ax.annotate('', xy=(sx0 - 0.05, sy1), xytext=(sx0 - 0.05, sy0),
                arrowprops=dict(arrowstyle='->', color='#999', lw=0.8))
    ax.text(sx0 - 0.15, sy1, 'scenario diversity',
            ha='right', va='top', fontsize=7.5, color='#777',
            style='italic', rotation=90)

# Arrows between panels
arrow_y = panel_y + panel_h / 2 + 0.3
arrow_labels = [
    ('Expansion\n(in-context few-shot)', '#4a79b8'),
    ('DPO step\nExpand/Query/Label/Update', '#4a79b8'),
    ('DPO step', '#4a79b8'),
]
for i, (lbl, col) in enumerate(arrow_labels):
    x_start = panel_xs[i] + panel_w + 0.05
    x_end = panel_xs[i + 1] - 0.05
    arr = FancyArrowPatch((x_start, arrow_y), (x_end, arrow_y),
                          arrowstyle='-|>', mutation_scale=22,
                          color=col, lw=2.0)
    ax.add_patch(arr)
    ax.text((x_start + x_end) / 2, arrow_y + 0.35, lbl,
            ha='center', va='bottom', fontsize=8.5,
            color=col, style='italic')

# DPO inner-loop callout (single target LVLM labels the candidate batch)
callout_x, callout_y = 8.6, 4.25
ax.add_patch(FancyBboxPatch((callout_x, callout_y), 7.4, 0.5,
                            boxstyle='round,pad=0.02',
                            facecolor='#F0F6FC', edgecolor='#7a9fd8',
                            lw=0.8, linestyle='--'))
ax.text(callout_x + 0.25, callout_y + 0.25,
        r'inner loop: target LVLM queried on each triplet '
        r'$\to$ preference label (all-Unknown = negative, '
        r'$\geq$1 non-Unknown = positive) $\to$ DPO update',
        ha='left', va='center', fontsize=9, color='#355',
        style='italic')

# ---------------------------------------------------------------------------
# Transition: sample one candidate from converged pool -> DeepAgent
# ---------------------------------------------------------------------------
# A star marker inside the last DPO panel, with a downward arrow into row 2
star_x = panel_xs[3] + panel_w - 0.9
star_y = panel_y + 1.4
ax.scatter([star_x], [star_y], marker='*', s=260,
           c='#b33a2c', edgecolors='black', linewidths=0.6, zorder=5)
ax.text(star_x + 0.18, star_y, 'sampled\ncandidate',
        ha='left', va='center', fontsize=8.5, color='#b33a2c',
        fontweight='bold')

ax.annotate('', xy=(star_x, 3.65), xytext=(star_x, star_y - 0.25),
            arrowprops=dict(arrowstyle='-|>', color='#b33a2c', lw=2.0))

# ---------------------------------------------------------------------------
# ROW 2: DeepAgent instance-level multi-turn probing
# ---------------------------------------------------------------------------
row2_y_band = 3.15
ax.add_patch(FancyBboxPatch((0.3, row2_y_band), 17.4, 0.5,
                            boxstyle='round,pad=0.02',
                            facecolor='#DDEEDD', edgecolor='#4a9447', lw=1.0))
ax.text(9.0, row2_y_band + 0.25,
        'DeepAgent — Multi-Turn Probing  '
        '(instance-level; fixed image triplet; '
        r'$T{=}3$ turns; Deepening / Rewriting)',
        ha='center', va='center', fontsize=12, fontweight='bold',
        color='#1f5c2a')

# Candidate card on the left
card_x, card_y = 0.5, 0.5
card_w, card_h = 3.1, 2.35
ax.add_patch(FancyBboxPatch((card_x, card_y), card_w, card_h,
                            boxstyle='round,pad=0.02',
                            facecolor='white', edgecolor='#4a9447', lw=1.2))
ax.text(card_x + card_w / 2, card_y + card_h - 0.25,
        'Candidate instance',
        ha='center', va='top', fontsize=10, fontweight='bold',
        color='#1f5c2a')
# image triplet boxes
for k in range(3):
    ix = card_x + 0.2 + k * 0.92
    ax.add_patch(FancyBboxPatch((ix, card_y + 1.25), 0.8, 0.65,
                                boxstyle='round,pad=0.01',
                                facecolor='#ececec', edgecolor='#999',
                                lw=0.6))
    ax.text(ix + 0.4, card_y + 1.58,
            f'$I_{k+1}$', ha='center', va='center', fontsize=9, color='#333')
ax.text(card_x + card_w / 2, card_y + 1.1,
        r'$Q_0$ (ambiguous, negatively-implied)',
        ha='center', va='center', fontsize=8.5, color='#222', style='italic')
ax.text(card_x + card_w / 2, card_y + 0.65,
        r'$\mathcal{O}=\{\mathrm{Yes},\ \mathrm{No},\ \mathrm{Unknown}\}$',
        ha='center', va='center', fontsize=8.5, color='#222')

# Three turn blocks to the right
turn_y = 0.5
turn_h = 2.35
turn_w = 3.7
turn_xs = [4.1, 8.2, 12.3]
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
            f'{name}  —  {strat}', ha='center', va='top',
            fontsize=10, fontweight='bold', color='#1f5c2a')
    # sub-strategy list
    ax.text(tx + 0.2, turn_y + turn_h - 0.7, subs,
            ha='left', va='top', fontsize=8, color='#355')
    # generated Q
    ax.add_patch(FancyBboxPatch((tx + 0.2, turn_y + 0.55), turn_w - 0.4, 0.55,
                                boxstyle='round,pad=0.02',
                                facecolor='white', edgecolor='#7A9FD8',
                                lw=1.0, linestyle='--'))
    ax.text(tx + turn_w / 2, turn_y + 0.82,
            r'$Q_t$  (re-used $I_1,I_2,I_3$)',
            ha='center', va='center', fontsize=8.5, color='#355',
            style='italic')
    # response bubble
    ax.add_patch(FancyBboxPatch((tx + 0.2, turn_y + 0.1), turn_w - 0.4, 0.35,
                                boxstyle='round,pad=0.01',
                                facecolor='#f5e0b7', edgecolor='#555',
                                lw=0.5))
    ax.text(tx + turn_w / 2, turn_y + 0.275,
            r'target response $r_t \in \{\mathrm{Yes},\mathrm{No},\mathrm{Unknown}\}$',
            ha='center', va='center', fontsize=8.2, color='#111')

# Arrows between DeepAgent blocks (showing history-conditioned choice)
for i, x_end in enumerate([turn_xs[0], turn_xs[1], turn_xs[2]]):
    x_start = (card_x + card_w) if i == 0 else (turn_xs[i - 1] + turn_w)
    arr = FancyArrowPatch((x_start + 0.02, turn_y + turn_h / 2),
                          (x_end - 0.02, turn_y + turn_h / 2),
                          arrowstyle='-|>', mutation_scale=22,
                          color='#4a9447', lw=1.8)
    ax.add_patch(arr)
    ax.text((x_start + x_end) / 2, turn_y + turn_h / 2 + 0.3,
            'history-\nconditioned\nstrategy choice',
            ha='center', va='bottom', fontsize=7.5, color='#4a9447',
            style='italic')

# Final output arrow to benchmark assembly
ax.annotate('',
            xy=(16.3, turn_y + turn_h / 2),
            xytext=(turn_xs[2] + turn_w, turn_y + turn_h / 2),
            arrowprops=dict(arrowstyle='-|>', color='black', lw=2.0))
ax.text(16.35, turn_y + turn_h / 2,
        '→ decomposed\n   test instances\n   (I,Q,\u2131)  §4.3',
        ha='left', va='center', fontsize=9,
        fontweight='bold', color='#222')

# Bias judgment legend below DeepAgent row
ax.text(0.5, 0.15,
        r'Bias judgment (per decomposed instance): '
        r'Correct$(r)=\mathbb{1}[r=\mathrm{Unknown}]$   '
        r'$\Rightarrow$ bias accuracy / elicitation rate',
        ha='left', va='center', fontsize=9, color='#333', style='italic')

# Title
fig.text(0.5, 0.985,
         'DeepBias Method — Single-Target View '
         '(Proposer shifts distribution, DeepAgent probes one instance)',
         ha='center', va='top', fontsize=13.5, fontweight='bold')

plt.savefig(OUT, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()
print('Saved:', OUT)
