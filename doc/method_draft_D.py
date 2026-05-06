"""Method figure draft — Option D: concrete method depiction.

Proposer row shows the four concrete mechanisms (Expand / SDXL rendering /
Query + Label / DPO update) with an explicit positive/negative split, and a
loop-back arrow indicating iteration. DeepAgent row shows a stylised agent
character that issues progressively deeper questions across T=3 turns, with
the Q-card tint darkening to suggest deepening.

Run:
    python3 doc/method_draft_D.py
"""
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle

OUT = os.path.join(os.path.dirname(__file__), 'figure_mockups',
                   'method_draft_D.png')

fig = plt.figure(figsize=(19, 11.0))
ax = fig.add_axes((0, 0, 1, 1))
ax.set_xlim(0, 19)
ax.set_ylim(0, 11.0)
ax.axis('off')


# ---------------------------------------------------------------------------
# Drawing primitives
# ---------------------------------------------------------------------------
def doc_stack(cx, cy, n=4, w=0.48, h=0.6, facecolor='#FFFFFF',
              edgecolor='#7A9FD8', lw=0.8, step=0.07, top_lines=True):
    for i in range(n - 1, -1, -1):
        off = i * step
        ax.add_patch(FancyBboxPatch(
            (cx - w / 2 + off, cy - h / 2 - off),
            w, h, boxstyle='round,pad=0.01',
            facecolor=facecolor, edgecolor=edgecolor, lw=lw, zorder=10 - i))
    if top_lines:
        top_x = cx - w / 2
        top_y = cy + h / 2
        for k in range(2):
            ax.plot([top_x + 0.07, top_x + w - 0.07],
                    [top_y - 0.13 - k * 0.09, top_y - 0.13 - k * 0.09],
                    color=edgecolor, lw=0.7, zorder=20)


def img_triplet_stack(cx, cy, n=3, s=0.13, gap=0.03, step=0.06):
    total = 3 * s + 2 * gap
    for i in range(n - 1, -1, -1):
        off = i * step
        x0 = cx - total / 2 + off
        y0 = cy - s / 2 - off
        for k in range(3):
            ax.add_patch(Rectangle((x0 + k * (s + gap), y0), s, s,
                                   facecolor='#f0e8ff',
                                   edgecolor='#7a4fa6', lw=0.5,
                                   zorder=10 - i))


def proposer_icon(cx, cy, label_pi=r'$\pi_\theta$'):
    ax.add_patch(FancyBboxPatch((cx - 0.55, cy - 0.38), 1.1, 0.76,
                                boxstyle='round,pad=0.02',
                                facecolor='#DDE9F5', edgecolor='#1f3d63',
                                lw=1.2))
    ax.text(cx, cy + 0.13, 'Proposer',
            ha='center', va='center', fontsize=8.5,
            color='#1f3d63', fontweight='bold')
    ax.text(cx, cy - 0.14, label_pi,
            ha='center', va='center', fontsize=12, color='#1f3d63')


def sdxl_icon(cx, cy):
    ax.add_patch(FancyBboxPatch((cx - 0.55, cy - 0.35), 1.1, 0.7,
                                boxstyle='round,pad=0.02',
                                facecolor='#F3E8FF', edgecolor='#7a4fa6',
                                lw=1.2))
    ax.text(cx, cy + 0.1, 'SDXL',
            ha='center', va='center', fontsize=9.5,
            color='#7a4fa6', fontweight='bold')
    ax.text(cx, cy - 0.13, 'T2I rendering',
            ha='center', va='center', fontsize=7.5,
            color='#7a4fa6', style='italic')


def lvlm_icon(cx, cy, label='target LVLM', w=1.3, h=0.6, fs=9):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                boxstyle='round,pad=0.02',
                                facecolor='#FFF5E0', edgecolor='#C77A2C',
                                lw=1.2))
    ax.text(cx, cy, label, ha='center', va='center',
            fontsize=fs, color='#7a4a10', fontweight='bold')


def deepagent_icon(cx, cy, w=1.4, h=1.75):
    # Body (rounded-square head-and-shoulders)
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2 + 0.08), w, h - 0.2,
                                boxstyle='round,pad=0.04',
                                facecolor='#DDEEDD', edgecolor='#1f5c2a',
                                lw=1.6))
    # Eyes
    ax.add_patch(Circle((cx - 0.22, cy + 0.28), 0.07,
                        facecolor='#1f5c2a', zorder=5))
    ax.add_patch(Circle((cx + 0.22, cy + 0.28), 0.07,
                        facecolor='#1f5c2a', zorder=5))
    # Smile
    ax.plot([cx - 0.18, cx, cx + 0.18],
            [cy + 0.02, cy - 0.12, cy + 0.02],
            color='#1f5c2a', lw=1.5, zorder=5)
    # Antenna
    ax.plot([cx, cx], [cy + h / 2 - 0.15, cy + h / 2 + 0.08],
            color='#1f5c2a', lw=1.6)
    ax.add_patch(Circle((cx, cy + h / 2 + 0.14), 0.07,
                        facecolor='#b33a2c', zorder=5))
    # Label at bottom
    ax.text(cx, cy - h / 2 + 0.3, 'DeepAgent',
            ha='center', va='center', fontsize=10,
            color='#1f5c2a', fontweight='bold')
    ax.text(cx, cy - h / 2 + 0.05, 'strategy\nselector',
            ha='center', va='center', fontsize=7.5,
            color='#1f5c2a', style='italic')


def step_badge(cx, cy, n):
    ax.add_patch(Circle((cx, cy), 0.22,
                        facecolor='#1f3d63', edgecolor='#1f3d63',
                        zorder=20))
    ax.text(cx, cy, f'{n}', ha='center', va='center',
            fontsize=11, color='white', fontweight='bold', zorder=21)


# ===========================================================================
# TITLE
# ===========================================================================
fig.text(0.5, 0.985,
         'DeepBias Method — Proposer (distribution-level adversarial evolution) '
         '+ DeepAgent (instance-level multi-turn probing)',
         ha='center', va='top', fontsize=14, fontweight='bold')

# ===========================================================================
# PROPOSER SECTION
# ===========================================================================
prop_band_y = 9.75
ax.add_patch(FancyBboxPatch((0.3, prop_band_y), 18.4, 0.5,
                            boxstyle='round,pad=0.02',
                            facecolor='#DDE9F5', edgecolor='#4a79b8', lw=1.1))
ax.text(9.5, prop_band_y + 0.25,
        r'Proposer — Adversarial Evolution via DPO   '
        r'(distribution-level; $\pi_{\mathrm{ref}}$ = base LVLM; no SFT)',
        ha='center', va='center', fontsize=12.5, fontweight='bold',
        color='#1f3d63')

# Proposer content region: y in [5.4 .. 9.65]
prop_y0 = 5.4
prop_y1 = 9.65

# --- Seed input (leftmost) -------------------------------------------------
seed_cx = 1.1
seed_cy = 7.4
ax.add_patch(FancyBboxPatch((0.4, 6.3), 1.4, 2.3,
                            boxstyle='round,pad=0.02',
                            facecolor='#F7FAFE', edgecolor='#4a79b8', lw=0.9,
                            linestyle='--'))
ax.text(seed_cx, 8.35, 'Seed pool', ha='center', va='center',
        fontsize=9.5, color='#1f3d63', fontweight='bold')
ax.text(seed_cx, 8.08, 'BBQ / VLBiasBench', ha='center', va='center',
        fontsize=7.8, color='#355', style='italic')
doc_stack(seed_cx, 7.2, n=3)
ax.text(seed_cx, 6.55, r'$\sim$300 / category',
        ha='center', va='center', fontsize=8.5, color='#1f3d63')

# --- Four numbered step boxes ----------------------------------------------
step_y0 = 5.6
step_h = 3.7
step_xs = [2.3, 6.3, 9.8, 14.2]
step_ws = [3.7, 3.2, 4.1, 4.5]

# Step 1: Expand
x0, w = step_xs[0], step_ws[0]
ax.add_patch(FancyBboxPatch((x0, step_y0), w, step_h,
                            boxstyle='round,pad=0.03',
                            facecolor='#F7FAFE', edgecolor='#4a79b8', lw=1.2))
step_badge(x0 + 0.28, step_y0 + step_h - 0.28, 1)
ax.text(x0 + w / 2, step_y0 + step_h - 0.32, 'Expand',
        ha='center', va='top', fontsize=11, fontweight='bold',
        color='#1f3d63')
ax.text(x0 + w / 2, step_y0 + step_h - 0.62,
        'in-context few-shot generation',
        ha='center', va='top', fontsize=8, color='#355', style='italic')
proposer_icon(x0 + 0.85, step_y0 + 2.05)
# frozen exemplar pool
ax.add_patch(FancyBboxPatch((x0 + 1.7, step_y0 + 1.75), 1.15, 0.6,
                            boxstyle='round,pad=0.02',
                            facecolor='#FFF7E0', edgecolor='#a87c20', lw=0.9))
ax.text(x0 + 2.28, step_y0 + 2.15, 'frozen\nexemplar pool',
        ha='center', va='center', fontsize=7.2, color='#5a4010',
        fontweight='bold')
# arrows from Proposer + Exemplar -> batch
arr = FancyArrowPatch((x0 + 1.4, step_y0 + 2.05),
                      (x0 + 2.85, step_y0 + 0.9),
                      arrowstyle='-|>', mutation_scale=14,
                      color='#1f3d63', lw=1.1,
                      connectionstyle='arc3,rad=-0.15')
ax.add_patch(arr)
arr = FancyArrowPatch((x0 + 2.28, step_y0 + 1.75),
                      (x0 + 2.85, step_y0 + 0.9),
                      arrowstyle='-|>', mutation_scale=14,
                      color='#a87c20', lw=1.0, linestyle=':',
                      connectionstyle='arc3,rad=0.15')
ax.add_patch(arr)
# output batch of Q cards
doc_stack(x0 + 1.05, step_y0 + 0.8, n=5)
ax.text(x0 + 1.8, step_y0 + 0.8,
        'batch of $Q$\ncandidates', ha='left', va='center',
        fontsize=8, color='#1f3d63')

# Step 2: T2I rendering
x0, w = step_xs[1], step_ws[1]
ax.add_patch(FancyBboxPatch((x0, step_y0), w, step_h,
                            boxstyle='round,pad=0.03',
                            facecolor='#FAF5FF', edgecolor='#7a4fa6', lw=1.2))
step_badge(x0 + 0.28, step_y0 + step_h - 0.28, 2)
ax.text(x0 + w / 2, step_y0 + step_h - 0.32, 'Render images',
        ha='center', va='top', fontsize=11, fontweight='bold',
        color='#7a4fa6')
ax.text(x0 + w / 2, step_y0 + step_h - 0.62,
        'T2I for counterfactual triplets',
        ha='center', va='top', fontsize=8, color='#5a3080', style='italic')
sdxl_icon(x0 + w / 2, step_y0 + 2.1)
# arrow down to image triplets
ax.annotate('', xy=(x0 + w / 2, step_y0 + 1.25),
            xytext=(x0 + w / 2, step_y0 + 1.8),
            arrowprops=dict(arrowstyle='-|>', color='#7a4fa6', lw=1.3))
img_triplet_stack(x0 + w / 2, step_y0 + 0.85, n=4)
ax.text(x0 + w / 2, step_y0 + 0.3, r'triplets $(I_1, I_2, I_3)$',
        ha='center', va='center', fontsize=8, color='#5a3080')

# Step 3: Query + Label
x0, w = step_xs[2], step_ws[2]
ax.add_patch(FancyBboxPatch((x0, step_y0), w, step_h,
                            boxstyle='round,pad=0.03',
                            facecolor='#FFF9F0', edgecolor='#C77A2C', lw=1.2))
step_badge(x0 + 0.28, step_y0 + step_h - 0.28, 3)
ax.text(x0 + w / 2, step_y0 + step_h - 0.32, 'Query + Label',
        ha='center', va='top', fontsize=11, fontweight='bold',
        color='#7a4a10')
ax.text(x0 + w / 2, step_y0 + step_h - 0.62,
        r'responses split by Unknown rule',
        ha='center', va='top', fontsize=8, color='#7a4a10', style='italic')
lvlm_icon(x0 + w / 2, step_y0 + 2.3)
# Split down to positive/negative piles
# positive pile (green tint)
pos_cx = x0 + 1.0
neg_cx = x0 + w - 1.0
ax.annotate('', xy=(pos_cx, step_y0 + 1.2),
            xytext=(x0 + w / 2 - 0.25, step_y0 + 2.0),
            arrowprops=dict(arrowstyle='-|>', color='#4a9447', lw=1.3))
ax.annotate('', xy=(neg_cx, step_y0 + 1.2),
            xytext=(x0 + w / 2 + 0.25, step_y0 + 2.0),
            arrowprops=dict(arrowstyle='-|>', color='#b33a2c', lw=1.3))
doc_stack(pos_cx, step_y0 + 0.85, n=3, facecolor='#E5F4E0', edgecolor='#4a9447')
doc_stack(neg_cx, step_y0 + 0.85, n=3, facecolor='#F9E0DA', edgecolor='#b33a2c')
ax.text(pos_cx, step_y0 + 0.25, r'positive $y^+$',
        ha='center', va='center', fontsize=8, color='#1f5c2a',
        fontweight='bold')
ax.text(pos_cx, step_y0 + 0.0, r'$\geq 1$ non-Unknown',
        ha='center', va='center', fontsize=7, color='#1f5c2a',
        style='italic')
ax.text(neg_cx, step_y0 + 0.25, r'negative $y^-$',
        ha='center', va='center', fontsize=8, color='#8a1a0a',
        fontweight='bold')
ax.text(neg_cx, step_y0 + 0.0, 'all Unknown',
        ha='center', va='center', fontsize=7, color='#8a1a0a',
        style='italic')

# Step 4: DPO Update
x0, w = step_xs[3], step_ws[3]
ax.add_patch(FancyBboxPatch((x0, step_y0), w, step_h,
                            boxstyle='round,pad=0.03',
                            facecolor='#F7FAFE', edgecolor='#4a79b8', lw=1.2))
step_badge(x0 + 0.28, step_y0 + step_h - 0.28, 4)
ax.text(x0 + w / 2, step_y0 + step_h - 0.32, 'Update Proposer (DPO)',
        ha='center', va='top', fontsize=11, fontweight='bold',
        color='#1f3d63')
ax.text(x0 + w / 2, step_y0 + step_h - 0.62,
        r'preference optimisation on $(y^+, y^-)$',
        ha='center', va='top', fontsize=8, color='#355', style='italic')
# DPO loss formula card
ax.add_patch(FancyBboxPatch((x0 + 0.4, step_y0 + 1.5), w - 0.8, 1.3,
                            boxstyle='round,pad=0.02',
                            facecolor='white', edgecolor='#4a79b8', lw=1.0))
ax.text(x0 + w / 2, step_y0 + 2.45,
        r'$\mathcal{L}_{\mathrm{DPO}}(\theta)$',
        ha='center', va='center', fontsize=11, color='#1f3d63',
        fontweight='bold')
ax.text(x0 + w / 2, step_y0 + 1.95,
        r'$= -\log \sigma\!\left[\,\beta \log\frac{\pi_\theta(y^+)}{\pi_{\mathrm{ref}}(y^+)}'
        r'\ -\ \beta \log\frac{\pi_\theta(y^-)}{\pi_{\mathrm{ref}}(y^-)}\right]$',
        ha='center', va='center', fontsize=9.5, color='#1f3d63')
# Feed positive/negative inputs (visual)
ax.annotate('', xy=(x0 + 0.4, step_y0 + 2.1),
            xytext=(x0 - 0.1, step_y0 + 1.0),
            arrowprops=dict(arrowstyle='-|>', color='#4a79b8', lw=1.0,
                            connectionstyle='arc3,rad=-0.25'))
# Arrow out of DPO back to Proposer (loop-back)
# We'll draw a big curved arrow at the bottom.

# Inter-step arrows (top of each step box)
for i in range(3):
    x_start = step_xs[i] + step_ws[i]
    x_end = step_xs[i + 1]
    ax.annotate('', xy=(x_end - 0.02, step_y0 + step_h / 2),
                xytext=(x_start + 0.02, step_y0 + step_h / 2),
                arrowprops=dict(arrowstyle='-|>', color='#4a79b8', lw=2.0))

# Arrow from Seed pool into Step 1 (from right side of seed to left side of step 1)
ax.annotate('', xy=(step_xs[0] - 0.02, 7.4),
            xytext=(1.85, 7.4),
            arrowprops=dict(arrowstyle='-|>', color='#666', lw=1.6))

# --- Loop-back arrow: Step 4 -> Step 1 (iteration) --------------------------
loop_y = step_y0 - 0.55
ax.annotate('',
            xy=(step_xs[0] + 0.85, step_y0 - 0.05),
            xytext=(step_xs[3] + step_ws[3] - 0.9, step_y0 - 0.05),
            arrowprops=dict(arrowstyle='-|>', color='#1f3d63', lw=2.0,
                            connectionstyle=f'arc3,rad=-0.08'))
ax.text((step_xs[0] + step_xs[3] + step_ws[3]) / 2, step_y0 - 0.55,
        r'iterate for $K$ DPO rounds   '
        r'(Iter 1 $\to$ Iter 2 $\to$ $\ldots$)',
        ha='center', va='center', fontsize=10, color='#1f3d63',
        fontweight='bold', style='italic')

# ===========================================================================
# TRANSITION between Proposer and DeepAgent
# ===========================================================================
# Converged batch -> sample candidate
sample_cx = 17.9
sample_cy = step_y0 + 1.5
ax.annotate('', xy=(sample_cx, 4.55),
            xytext=(sample_cx, step_y0 - 0.55),
            arrowprops=dict(arrowstyle='-|>', color='#b33a2c', lw=2.0))
ax.text(sample_cx + 0.2, step_y0 - 1.2,
        'sample\ncandidate',
        ha='left', va='center', fontsize=8.8, color='#b33a2c',
        fontweight='bold')

# ===========================================================================
# DEEPAGENT SECTION
# ===========================================================================
da_band_y = 4.1
ax.add_patch(FancyBboxPatch((0.3, da_band_y), 18.4, 0.5,
                            boxstyle='round,pad=0.02',
                            facecolor='#DDEEDD', edgecolor='#4a9447', lw=1.1))
ax.text(9.5, da_band_y + 0.25,
        r'DeepAgent — Multi-Turn Probing   '
        r'(instance-level; fixed image triplet; $T{=}3$ turns; '
        r'Deepening / Rewriting)',
        ha='center', va='center', fontsize=12.5, fontweight='bold',
        color='#1f5c2a')

# Candidate instance card
cand_x, cand_y = 0.4, 0.7
cand_w, cand_h = 2.6, 3.1
ax.add_patch(FancyBboxPatch((cand_x, cand_y), cand_w, cand_h,
                            boxstyle='round,pad=0.02',
                            facecolor='white', edgecolor='#4a9447', lw=1.2))
ax.text(cand_x + cand_w / 2, cand_y + cand_h - 0.25,
        'Candidate instance',
        ha='center', va='top', fontsize=10.5, fontweight='bold',
        color='#1f5c2a')
# Image triplet
for k in range(3):
    ix = cand_x + 0.3 + k * 0.72
    ax.add_patch(FancyBboxPatch((ix, cand_y + 1.85), 0.62, 0.62,
                                boxstyle='round,pad=0.01',
                                facecolor='#ececec', edgecolor='#888', lw=0.6))
    ax.text(ix + 0.31, cand_y + 2.16, f'$I_{k+1}$',
            ha='center', va='center', fontsize=9, color='#555')
# Q_0
ax.add_patch(FancyBboxPatch((cand_x + 0.2, cand_y + 1.05), cand_w - 0.4, 0.55,
                            boxstyle='round,pad=0.02',
                            facecolor='#F7FAFE', edgecolor='#7A9FD8', lw=0.9,
                            linestyle='--'))
ax.text(cand_x + cand_w / 2, cand_y + 1.32,
        r'$Q_0$: ambiguous,' '\n' r'negatively-implied',
        ha='center', va='center', fontsize=8.2, color='#355', style='italic')
ax.text(cand_x + cand_w / 2, cand_y + 0.55,
        r'$\mathcal{O}=\{\mathrm{Yes},\,\mathrm{No},\,\mathrm{Unknown}\}$',
        ha='center', va='center', fontsize=8, color='#222')

# DeepAgent avatar
agent_cx, agent_cy = 4.45, 2.25
deepagent_icon(agent_cx, agent_cy)

# Arrow from candidate instance to DeepAgent
ax.annotate('', xy=(agent_cx - 0.75, agent_cy),
            xytext=(cand_x + cand_w + 0.02, agent_cy),
            arrowprops=dict(arrowstyle='-|>', color='#4a9447', lw=2.0))
ax.text((cand_x + cand_w + agent_cx - 0.75) / 2, agent_cy + 0.2,
        'instance',
        ha='center', va='bottom', fontsize=8, color='#4a9447',
        style='italic')

# Three turn cards (progressively darker background → "deepening")
turn_bg = ['#FFF3E6', '#FFD9BF', '#F5B099']
turn_edge = ['#D48A33', '#B86A20', '#8C3A14']
turn_xs = [6.3, 10.2, 14.1]
turn_y, turn_h, turn_w = 0.7, 3.1, 3.6
turn_titles = [
    ('Turn 1', 'Rewriting',
     '• contextualisation\n• projection\n• behav.-tendency\n• cognitive attrib.'),
    ('Turn 2', 'Deepening',
     '• attribute refinement\n• scenario deepening\n• comparison deepening'),
    ('Turn 3', 'Deepening',
     '• attribute refinement\n• scenario deepening\n• comparison deepening'),
]
prev_out_x = agent_cx + 0.75  # right edge of agent
for idx, (tx, (name, strat, subs)) in enumerate(zip(turn_xs, turn_titles)):
    ax.add_patch(FancyBboxPatch((tx, turn_y), turn_w, turn_h,
                                boxstyle='round,pad=0.03',
                                facecolor=turn_bg[idx],
                                edgecolor=turn_edge[idx], lw=1.2))
    ax.text(tx + turn_w / 2, turn_y + turn_h - 0.25,
            f'{name}  —  {strat}',
            ha='center', va='top', fontsize=10.5, fontweight='bold',
            color=turn_edge[idx])
    # sub-strategy list
    ax.text(tx + 0.22, turn_y + turn_h - 0.7, subs,
            ha='left', va='top', fontsize=8, color='#4a2a10')
    # Q_t card (darker tint with each turn)
    q_bg = ['#FFFFFF', '#FFF5EA', '#FFE5D3'][idx]
    ax.add_patch(FancyBboxPatch((tx + 0.2, turn_y + 0.95), turn_w - 0.4, 0.65,
                                boxstyle='round,pad=0.02',
                                facecolor=q_bg, edgecolor='#7A9FD8',
                                lw=1.0, linestyle='--'))
    ax.text(tx + turn_w / 2, turn_y + 1.28,
            f'$Q_{idx+1}$  (fixed $I_1,I_2,I_3$)',
            ha='center', va='center', fontsize=8.5,
            color='#355', style='italic')
    # intensity ticks: 1/2/3 small bars to visualise "depth"
    for tk in range(3):
        fc = turn_edge[idx] if tk <= idx else '#ddd'
        ax.add_patch(Rectangle((tx + 0.25 + tk * 0.2, turn_y + 1.02),
                               0.15, 0.08, facecolor=fc,
                               edgecolor='none'))
    # target LVLM + response
    lvlm_icon(tx + 0.85, turn_y + 0.45, label='target LVLM', w=1.1,
              h=0.42, fs=7.8)
    ax.text(tx + 1.52, turn_y + 0.45,
            r'$\to\ r_t \in \{\mathrm{Yes},\mathrm{No},\mathrm{Unknown}\}$',
            ha='left', va='center', fontsize=8.2, color='#111')
    # Arrow from previous block to this block
    start_x = prev_out_x + 0.02
    ax.annotate('', xy=(tx - 0.02, turn_y + turn_h / 2),
                xytext=(start_x, turn_y + turn_h / 2),
                arrowprops=dict(arrowstyle='-|>', color='#4a9447', lw=1.8))
    prev_out_x = tx + turn_w
    # History feedback arrow (from turn back down to agent)
    if idx < 2:
        ax.annotate('',
                    xy=(agent_cx + 0.1, agent_cy - 0.9),
                    xytext=(tx + turn_w / 2, turn_y + 0.05),
                    arrowprops=dict(arrowstyle='-|>', color='#4a9447',
                                    lw=0.9, linestyle=':',
                                    connectionstyle=f'arc3,rad={-0.25 - idx*0.1}'))

# History-conditioned annotation near the agent
ax.text(agent_cx, agent_cy - 1.35,
        'each turn\'s history feeds\nback into strategy choice',
        ha='center', va='top', fontsize=7.8, color='#1f5c2a',
        style='italic')

# Depth gradient bar at bottom
grad_y = 0.4
ax.text(turn_xs[0], grad_y,
        'probing depth increases',
        ha='left', va='center', fontsize=9, color='#8a4a10',
        fontweight='bold', style='italic')
ax.annotate('',
            xy=(turn_xs[2] + turn_w - 0.3, grad_y),
            xytext=(turn_xs[0] + 2.0, grad_y),
            arrowprops=dict(arrowstyle='-|>', color='#8a4a10', lw=1.6))

# Final output → §4.3
ax.annotate('',
            xy=(18.7, turn_y + turn_h / 2),
            xytext=(turn_xs[2] + turn_w + 0.02, turn_y + turn_h / 2),
            arrowprops=dict(arrowstyle='-|>', color='black', lw=2.0))
ax.text(18.72, turn_y + turn_h / 2,
        r'$\Rightarrow$ $(I,Q,\mathcal{O})$' '\n'
        'test instances\n§4.3',
        ha='right', va='center', fontsize=8.8, fontweight='bold',
        color='#222')

plt.savefig(OUT, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()
print('Saved:', OUT)
