"""Method figure draft — Option C: pure schematic module-flow.

No scatter plots (which read like §5 results). Only iconic modules and arrows,
close in spirit to the fig1 / fig2 teaser style: document-stack icons for
batches, image-triplet icons for per-candidate visuals, LVLM avatars, and
labelled arrows. "Distribution-level" is conveyed by stack size + a drift
indicator badge, NOT by scatter.

Run:
    python3 doc/method_draft_C.py
"""
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

OUT = os.path.join(os.path.dirname(__file__), 'figure_mockups',
                   'method_draft_C.png')

fig = plt.figure(figsize=(18, 9.6))
ax = fig.add_axes((0, 0, 1, 1))
ax.set_xlim(0, 18)
ax.set_ylim(0, 9.6)
ax.axis('off')


# ---------------------------------------------------------------------------
# Drawing primitives
# ---------------------------------------------------------------------------
def doc_stack(cx, cy, n=5, w=0.52, h=0.68, color='#FFFFFF', edge='#7A9FD8',
              lw=0.9, step=0.07):
    """Draw n overlapping document cards centred at (cx, cy)."""
    for i in range(n - 1, -1, -1):
        off = i * step
        ax.add_patch(FancyBboxPatch(
            (cx - w / 2 + off, cy - h / 2 - off),
            w, h, boxstyle='round,pad=0.01',
            facecolor=color, edgecolor=edge, lw=lw, zorder=3 + (n - i)))
    # Top card decoration: 3 thin lines (text hint) + small triplet icon
    top_x = cx - w / 2
    top_y = cy + h / 2
    for k in range(2):
        ax.plot([top_x + 0.08, top_x + w - 0.08],
                [top_y - 0.14 - k * 0.1, top_y - 0.14 - k * 0.1],
                color='#7A9FD8', lw=0.7, zorder=10)
    # triplet dots at bottom of top card
    for k in range(3):
        ax.add_patch(Rectangle(
            (top_x + 0.07 + k * 0.12, top_y - h + 0.1),
            0.09, 0.09, facecolor='#dce6f2', edgecolor='#7A9FD8',
            lw=0.5, zorder=10))


def image_triplet(cx, cy, s=0.5, gap=0.08, color='#ececec', edge='#999'):
    total = 3 * s + 2 * gap
    x0 = cx - total / 2
    for k in range(3):
        x = x0 + k * (s + gap)
        ax.add_patch(FancyBboxPatch((x, cy - s / 2), s, s,
                                    boxstyle='round,pad=0.01',
                                    facecolor=color, edgecolor=edge, lw=0.7))
        ax.text(x + s / 2, cy, f'$I_{k+1}$', ha='center', va='center',
                fontsize=8.5, color='#555')


def lvlm_icon(cx, cy, w=0.85, h=0.38, color='#FFF5E0', edge='#C77A2C',
              label='target LVLM', fs=8):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                boxstyle='round,pad=0.02',
                                facecolor=color, edgecolor=edge, lw=0.8))
    ax.text(cx, cy, label, ha='center', va='center', fontsize=fs,
            fontweight='bold', color='#7a4a10')


def drift_badge(cx, cy, w=1.15, h=0.35, text='more implicit',
                color='#E8F0F9', edge='#1f3d63'):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                boxstyle='round,pad=0.02',
                                facecolor=color, edgecolor=edge, lw=0.8))
    # inline arrow icon
    ax.annotate('', xy=(cx + w / 2 - 0.12, cy),
                xytext=(cx - w / 2 + 0.12, cy),
                arrowprops=dict(arrowstyle='->', color='#1f3d63', lw=1.1))
    ax.text(cx, cy - 0.26, text, ha='center', va='top', fontsize=7.6,
            color='#1f3d63', style='italic')


# ---------------------------------------------------------------------------
# Top band: Proposer
# ---------------------------------------------------------------------------
band_y = 8.85
ax.add_patch(FancyBboxPatch((0.3, band_y), 17.4, 0.5,
                            boxstyle='round,pad=0.02',
                            facecolor='#DDE9F5', edgecolor='#4a79b8', lw=1.0))
ax.text(9.0, band_y + 0.25,
        r'Proposer — Adversarial Evolution via DPO   '
        r'(distribution-level, iterative; '
        r'$\pi_{\mathrm{ref}}$ = base LVLM, no SFT)',
        ha='center', va='center', fontsize=12.5, fontweight='bold',
        color='#1f3d63')

# Four Proposer module boxes
panel_specs = [
    dict(title='Seed', subtitle='BBQ / VLBiasBench',
         n=3, size_note=r'$\sim$300 / category', drift=None),
    dict(title='Expanded batch', subtitle='frozen exemplar pool + SDXL',
         n=7, size_note=r'$\sim$2000 / category', drift=None),
    dict(title='DPO Iter 1', subtitle='Expand / Query / Label / Update',
         n=7, size_note=r'$\sim$2000 / category', drift='more implicit'),
    dict(title='DPO Iter 2 (converged)', subtitle='',
         n=7, size_note=r'$\sim$2000 / category',
         drift='harder to refuse'),
]

panel_xs = [0.55, 4.85, 9.15, 13.45]
panel_w, panel_h = 4.0, 2.75
panel_y = 5.6

for (x0, spec) in zip(panel_xs, panel_specs):
    ax.add_patch(FancyBboxPatch((x0, panel_y), panel_w, panel_h,
                                boxstyle='round,pad=0.02',
                                facecolor='#F7FAFE', edgecolor='#4a79b8',
                                lw=1.1))
    # Title
    ax.text(x0 + panel_w / 2, panel_y + panel_h - 0.3, spec['title'],
            ha='center', va='top', fontsize=11, fontweight='bold',
            color='#1f3d63')
    if spec['subtitle']:
        ax.text(x0 + panel_w / 2, panel_y + panel_h - 0.6,
                spec['subtitle'], ha='center', va='top',
                fontsize=8.3, color='#355', style='italic')
    # Document stack icon (size encodes batch size)
    doc_stack(x0 + panel_w / 2 - 0.4, panel_y + 1.25,
              n=spec['n'])
    # Size annotation
    ax.text(x0 + panel_w / 2 + 0.5, panel_y + 1.25,
            f"N = {spec['size_note']}", ha='left', va='center',
            fontsize=9, color='#1f3d63')
    # Drift badge for DPO iters
    if spec['drift']:
        drift_badge(x0 + panel_w / 2, panel_y + 0.35,
                    text=spec['drift'])

# Arrows between panels
arrow_y = panel_y + panel_h / 2
arrow_labels = [
    'Expansion\n(in-context few-shot)',
    'DPO step',
    'DPO step',
]
for i, lbl in enumerate(arrow_labels):
    x_start = panel_xs[i] + panel_w
    x_end = panel_xs[i + 1]
    arr = FancyArrowPatch((x_start, arrow_y), (x_end, arrow_y),
                          arrowstyle='-|>', mutation_scale=24,
                          color='#4a79b8', lw=2.2)
    ax.add_patch(arr)
    ax.text((x_start + x_end) / 2, arrow_y + 0.35, lbl,
            ha='center', va='bottom', fontsize=8.5,
            color='#1f3d63', style='italic')

# ---------------------------------------------------------------------------
# DPO inner-loop sub-diagram (tucked under the DPO Iter panels)
# ---------------------------------------------------------------------------
loop_y = 4.65
loop_h = 0.7
ax.add_patch(FancyBboxPatch((9.15, loop_y), 8.3, loop_h,
                            boxstyle='round,pad=0.02',
                            facecolor='#F0F6FC', edgecolor='#7a9fd8',
                            lw=0.9, linestyle='--'))
# 4 small stages: Expand -> Query -> Label -> Update
stages = ['Expand\nbatch', 'Query\ntarget LVLM', 'Label\n(Unknown rule)',
          'Update\nProposer (DPO)']
stage_xs = [9.5, 11.45, 13.4, 15.35]
for i, (sx, st) in enumerate(zip(stage_xs, stages)):
    ax.add_patch(FancyBboxPatch((sx, loop_y + 0.08), 1.6, loop_h - 0.16,
                                boxstyle='round,pad=0.01',
                                facecolor='white', edgecolor='#4a79b8',
                                lw=0.8))
    ax.text(sx + 0.8, loop_y + loop_h / 2, st,
            ha='center', va='center', fontsize=7.8, color='#1f3d63')
    if i < 3:
        arr = FancyArrowPatch((sx + 1.6, loop_y + loop_h / 2),
                              (stage_xs[i + 1], loop_y + loop_h / 2),
                              arrowstyle='-|>', mutation_scale=14,
                              color='#4a79b8', lw=1.2)
        ax.add_patch(arr)
# loop-back arrow from Update → Expand
ax.annotate('',
            xy=(9.5, loop_y - 0.06),
            xytext=(16.95, loop_y - 0.06),
            arrowprops=dict(arrowstyle='-|>', color='#4a79b8',
                            lw=1.2, linestyle=':',
                            connectionstyle='arc3,rad=0.15'))
ax.text(13.25, loop_y - 0.35, 'loop (per DPO iter)',
        ha='center', va='top', fontsize=8, color='#1f3d63',
        style='italic')

# ---------------------------------------------------------------------------
# Transition: sample one candidate → DeepAgent
# ---------------------------------------------------------------------------
samp_x = panel_xs[3] + panel_w - 0.7
samp_y = panel_y + 0.35
ax.annotate('sample\ncandidate', xy=(samp_x, samp_y),
            xytext=(samp_x + 0.8, 3.5),
            fontsize=8.5, color='#b33a2c', fontweight='bold',
            ha='left', va='top',
            arrowprops=dict(arrowstyle='-|>', color='#b33a2c', lw=2.0))

# Downward arrow from DPO Iter 2 drift badge to DeepAgent band
ax.annotate('',
            xy=(panel_xs[3] + panel_w - 1.5, 3.55),
            xytext=(panel_xs[3] + panel_w - 1.5, panel_y + 0.1),
            arrowprops=dict(arrowstyle='-|>', color='#b33a2c', lw=2.0))

# ---------------------------------------------------------------------------
# Middle band: DeepAgent
# ---------------------------------------------------------------------------
band2_y = 3.05
ax.add_patch(FancyBboxPatch((0.3, band2_y), 17.4, 0.5,
                            boxstyle='round,pad=0.02',
                            facecolor='#DDEEDD', edgecolor='#4a9447', lw=1.0))
ax.text(9.0, band2_y + 0.25,
        r'DeepAgent — Multi-Turn Probing   '
        r'(instance-level, per-candidate; $T{=}3$; '
        r'Deepening / Rewriting)',
        ha='center', va='center', fontsize=12.5, fontweight='bold',
        color='#1f5c2a')

# Candidate instance card
card_x, card_y, card_w, card_h = 0.5, 0.55, 3.2, 2.25
ax.add_patch(FancyBboxPatch((card_x, card_y), card_w, card_h,
                            boxstyle='round,pad=0.02',
                            facecolor='white', edgecolor='#4a9447', lw=1.2))
ax.text(card_x + card_w / 2, card_y + card_h - 0.25,
        'Candidate instance',
        ha='center', va='top', fontsize=10.5, fontweight='bold',
        color='#1f5c2a')
image_triplet(card_x + card_w / 2, card_y + 1.55)
# Q0 placeholder card
ax.add_patch(FancyBboxPatch((card_x + 0.3, card_y + 0.6), card_w - 0.6, 0.4,
                            boxstyle='round,pad=0.01',
                            facecolor='#F7FAFE', edgecolor='#7A9FD8',
                            lw=0.9, linestyle='--'))
ax.text(card_x + card_w / 2, card_y + 0.8,
        r'$Q_0$  (ambiguous, negatively-implied)',
        ha='center', va='center', fontsize=8.3, color='#355',
        style='italic')
ax.text(card_x + card_w / 2, card_y + 0.3,
        r'$\mathcal{O} = \{\mathrm{Yes},\ \mathrm{No},\ \mathrm{Unknown}\}$',
        ha='center', va='center', fontsize=8.3, color='#222')

# Three turn boxes
turn_y, turn_h = 0.55, 2.25
turn_w = 3.4
turn_xs = [4.1, 7.9, 11.7]
turn_titles = [
    ('Turn 1', 'Rewriting',
     '• contextualisation\n• projection\n• behav.-tendency\n• cognitive attrib.'),
    ('Turn 2', 'Deepening',
     '• attribute refinement\n• scenario deepening\n• comparison deepening'),
    ('Turn 3', 'Deepening',
     '• attribute refinement\n• scenario deepening\n• comparison deepening'),
]
for (tx, (name, strat, subs)) in zip(turn_xs, turn_titles):
    ax.add_patch(FancyBboxPatch((tx, turn_y), turn_w, turn_h,
                                boxstyle='round,pad=0.02',
                                facecolor='#F4FAF4', edgecolor='#4a9447',
                                lw=1.1))
    ax.text(tx + turn_w / 2, turn_y + turn_h - 0.22,
            f'{name}  —  {strat}', ha='center', va='top',
            fontsize=10.5, fontweight='bold', color='#1f5c2a')
    ax.text(tx + 0.2, turn_y + turn_h - 0.65, subs,
            ha='left', va='top', fontsize=7.8, color='#355')
    # Q placeholder (schematic)
    ax.add_patch(FancyBboxPatch((tx + 0.2, turn_y + 0.55), turn_w - 0.4, 0.4,
                                boxstyle='round,pad=0.02',
                                facecolor='white', edgecolor='#7A9FD8',
                                lw=0.9, linestyle='--'))
    ax.text(tx + turn_w / 2, turn_y + 0.75,
            r'$Q_t$  (re-uses fixed $I_1, I_2, I_3$)',
            ha='center', va='center', fontsize=8.2, color='#355',
            style='italic')
    # response indicator
    lvlm_icon(tx + 0.6, turn_y + 0.28, w=0.95, h=0.3,
              label='target LVLM', fs=7.5)
    ax.text(tx + 1.25, turn_y + 0.28,
            r'$\to\ r_t \in \{\mathrm{Yes},\mathrm{No},\mathrm{Unknown}\}$',
            ha='left', va='center', fontsize=8.3, color='#111')

# Arrows between turn boxes (history-conditioned)
for i, x_end in enumerate([turn_xs[0], turn_xs[1], turn_xs[2]]):
    x_start = (card_x + card_w) if i == 0 else (turn_xs[i - 1] + turn_w)
    arr = FancyArrowPatch((x_start + 0.02, turn_y + turn_h / 2),
                          (x_end - 0.02, turn_y + turn_h / 2),
                          arrowstyle='-|>', mutation_scale=22,
                          color='#4a9447', lw=1.8)
    ax.add_patch(arr)
    if i > 0:
        ax.text((x_start + x_end) / 2, turn_y + turn_h / 2 + 0.2,
                'history-\nconditioned\nstrategy', ha='center', va='bottom',
                fontsize=7.3, color='#4a9447', style='italic')

# Final arrow → §4.3
ax.annotate('',
            xy=(16.9, turn_y + turn_h / 2),
            xytext=(turn_xs[2] + turn_w + 0.02, turn_y + turn_h / 2),
            arrowprops=dict(arrowstyle='-|>', color='black', lw=2.0))
ax.text(16.95, turn_y + turn_h / 2,
        r'$\Rightarrow$ decomposed' '\n' r'test instances' '\n' r'$(I,Q,\mathcal{O})$' '\n' r'§4.3',
        ha='left', va='center', fontsize=8.8, fontweight='bold',
        color='#222')

# Bias-judgment strap along bottom
ax.text(0.5, 0.2,
        r'Bias judgment (per decomposed instance): '
        r'Correct$(r)=\mathbb{1}[r{=}\mathrm{Unknown}]$   '
        r'$\Rightarrow$   bias accuracy / elicitation rate',
        ha='left', va='center', fontsize=9, color='#333', style='italic')

# Title
fig.text(0.5, 0.99,
         'DeepBias Method (single-target view) — '
         'schematic module-flow; distribution-level Proposer + instance-level DeepAgent',
         ha='center', va='top', fontsize=13.5, fontweight='bold')

plt.savefig(OUT, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()
print('Saved:', OUT)
