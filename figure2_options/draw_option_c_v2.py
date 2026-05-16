"""Option C — v2.

Changes from v1:
1. Right side (Probe + Skill Library) wrapped in a single unified Stage B
   outer container. Header bar is 2 segments, not 3 — Stage B spans the
   right 2/3.
2. Stage A redrawn as a compact vertical pipeline that explicitly shows
   the T2I (SDXL) step generating 3 images, plus the DPO closed loop.
3. Cleaner spacing, less saturated colors, consistent radii.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Rectangle
import matplotlib as mpl
from pathlib import Path

mpl.rcParams["font.family"] = "DejaVu Sans"
mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["savefig.dpi"] = 170
mpl.rcParams["savefig.bbox"] = "tight"

OUT = Path("/home/lianqi/papers/deepbias-tpami/figure2_options")
OUT.mkdir(parents=True, exist_ok=True)

# Refined palette — softer, paper-friendly
C_PROPOSER     = "#4A78C8"
C_PROPOSER_BG  = "#E9F0FA"
C_DEEPAGENT    = "#D86A4A"
C_DEEPAGENT_BG = "#FDF0E9"
C_TARGET       = "#566573"
C_DATA         = "#FFF6DC"
C_DPO          = "#E5D7F2"
C_T2I          = "#D7E8DA"
C_IMG          = "#BFD9C3"
C_SKILL_DEEP   = "#4F9B86"
C_SKILL_RW     = "#E0A267"
C_TEXT         = "#222"


def rbox(ax, x, y, w, h, label, fc, ec=C_TEXT, lw=1.0, fs=9, fw="normal",
         tc="black", pad=0.03, rs=0.06):
    box = FancyBboxPatch((x, y), w, h,
                          boxstyle=f"round,pad={pad},rounding_size={rs}",
                          fc=fc, ec=ec, lw=lw, zorder=2)
    ax.add_patch(box)
    if label:
        ax.text(x + w/2, y + h/2, label, ha="center", va="center",
                fontsize=fs, fontweight=fw, color=tc, zorder=3)


def arrow(ax, x1, y1, x2, y2, lw=1.3, color=C_TEXT, style="-|>",
          connection="arc3,rad=0", mutation=14):
    a = FancyArrowPatch((x1, y1), (x2, y2),
                         arrowstyle=style, color=color, lw=lw,
                         connectionstyle=connection,
                         mutation_scale=mutation, zorder=4)
    ax.add_patch(a)


def mini_image(ax, x, y, w, h, label=""):
    """Tiny placeholder thumbnail to indicate a generated image."""
    rect = Rectangle((x, y), w, h, fc=C_IMG, ec="#3C5A40", lw=0.8, zorder=3)
    ax.add_patch(rect)
    # Diagonal accent strokes — suggest portrait silhouette without drawing one
    ax.plot([x + 0.05*w, x + 0.95*w], [y + 0.2*h, y + 0.8*h],
            color="#3C5A40", lw=0.6, zorder=4)
    ax.plot([x + 0.95*w, x + 0.05*w], [y + 0.2*h, y + 0.8*h],
            color="#3C5A40", lw=0.6, zorder=4)
    if label:
        ax.text(x + w/2, y - 0.13, label, ha="center", fontsize=7.5,
                color="#3C5A40")


def draw():
    fig, ax = plt.subplots(figsize=(15, 7.6), dpi=160)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8.2)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # ---------- Title (small, top-left, like a NeurIPS figure caption hint) ----------
    ax.text(8, 8.0, "Option C v2 — two stages (Stage B unified across right two sub-panels)",
            ha="center", fontsize=13, fontweight="bold", color="#444")

    # ============================================================
    # Header bar — 2 segments only
    # ============================================================
    header_y = 7.0
    rbox(ax, 0.4, header_y, 4.4, 0.55,
         "Stage A — train ProposerAgent (offline DPO)",
         C_PROPOSER, tc="white", fw="bold", fs=11, ec=C_PROPOSER, rs=0.08)
    rbox(ax, 5.0, header_y, 10.6, 0.55,
         "Stage B — probe Target VLM with DeepAgent (online, skill-driven)",
         C_DEEPAGENT, tc="white", fw="bold", fs=11, ec=C_DEEPAGENT, rs=0.08)
    # Faint arrow between headers
    arrow(ax, 4.8, header_y + 0.27, 5.0, header_y + 0.27, lw=1.4)

    # ============================================================
    # Stage A — vertical pipeline (left column, x: 0.4 – 4.8)
    # ============================================================
    sa_x, sa_y, sa_w, sa_h = 0.4, 0.4, 4.4, 6.4
    rbox(ax, sa_x, sa_y, sa_w, sa_h, "", C_PROPOSER_BG, ec=C_PROPOSER,
         lw=1.2, pad=0.02, rs=0.05)

    cx = sa_x + sa_w/2
    # 1. ProposerAgent
    rbox(ax, cx - 1.6, 5.85, 3.2, 0.8, "ProposerAgent\n(Qwen3-32B)",
         C_PROPOSER, tc="white", fw="bold", fs=10)
    arrow(ax, cx, 5.85, cx, 5.5)

    # 2. Generated instruction
    rbox(ax, cx - 1.85, 4.85, 3.7, 0.6,
         "Instruction: Q + image prompts ×3",
         C_DATA, fs=8.5)
    arrow(ax, cx, 4.85, cx, 4.5)

    # 3. T2I model
    rbox(ax, cx - 1.6, 3.85, 3.2, 0.6, "T2I model (SDXL)",
         C_T2I, fs=10, fw="bold")
    arrow(ax, cx, 3.85, cx, 3.6)

    # 4. Three image thumbnails
    img_y = 2.95
    img_h = 0.6
    img_w = 0.85
    gap = 0.25
    total_w = 3 * img_w + 2 * gap
    img_x0 = cx - total_w/2
    labels = ["I₁", "I₂", "I₃"]
    for i in range(3):
        mini_image(ax, img_x0 + i*(img_w + gap), img_y, img_w, img_h,
                   label=labels[i])
    # Caption under images
    ax.text(cx, img_y - 0.36, "counterfactual triplet",
            ha="center", fontsize=7.5, color="#555", style="italic")
    arrow(ax, cx, img_y - 0.55, cx, 2.15)

    # 5. Target VLM
    rbox(ax, cx - 1.6, 1.55, 3.2, 0.6, "Target VLM (answers Q given each Iᵢ)",
         C_TARGET, tc="white", fs=9, fw="bold")
    arrow(ax, cx, 1.55, cx, 1.25)

    # 6. Bias preference signal
    rbox(ax, cx - 1.85, 0.65, 3.7, 0.55,
         "bias detected → preference pair",
         C_DPO, fs=8.5, fw="bold")

    # DPO closed loop — curving arrow on the left side, from preference back
    # to ProposerAgent
    arrow(ax, sa_x + 0.15, 0.95, sa_x + 0.15, 6.2,
          lw=1.6, color="#7e6dad", connection="arc3,rad=-0.25",
          mutation=18)
    ax.text(sa_x + 0.32, 3.5, "DPO\nupdate",
            ha="left", fontsize=8.5, color="#7e6dad", fontweight="bold",
            rotation=90, va="center")

    # ============================================================
    # Stage B — unified outer container spanning right 2/3
    # ============================================================
    sb_x, sb_y, sb_w, sb_h = 5.0, 0.4, 10.6, 6.4
    # Outer Stage B container — single rounded rectangle, light bg
    rbox(ax, sb_x, sb_y, sb_w, sb_h, "", C_DEEPAGENT_BG, ec=C_DEEPAGENT,
         lw=1.5, pad=0.02, rs=0.05)

    # Sub-region 1: multi-turn trace (left half of Stage B)
    trace_x, trace_y, trace_w, trace_h = 5.3, 0.6, 5.8, 6.1
    # No outer border — just a sub-header
    ax.text(trace_x + trace_w/2, trace_y + trace_h - 0.05,
            "Multi-turn trace (one episode)",
            ha="center", fontsize=10, fontweight="bold", color=C_DEEPAGENT)

    # 3 turn cards stacked vertically inside trace area
    turn_h = 1.55
    turn_gap = 0.15
    turn_w = trace_w - 0.4
    turn_x = trace_x + 0.2
    for i, lbl in enumerate(["Turn 1", "Turn 2", "Turn 3"]):
        y = trace_y + trace_h - 0.4 - (i + 1) * (turn_h + turn_gap) + turn_gap
        rbox(ax, turn_x, y, turn_w, turn_h, "", "#FFFFFF", ec="#999",
             lw=0.8, pad=0.02)
        # Header
        rbox(ax, turn_x + 0.1, y + turn_h - 0.45, 0.95, 0.32, lbl,
             "#F2F2F2", fs=8.5, fw="bold")
        # DeepAgent rewrite mini-box
        rbox(ax, turn_x + 0.15, y + 0.55, 2.4, 0.6, "DeepAgent rewrites Qᵢ",
             C_DEEPAGENT, tc="white", fs=8, fw="bold")
        # Target response mini-box
        rbox(ax, turn_x + 2.85, y + 0.55, 2.45, 0.6, "Target VLM answers",
             C_TARGET, tc="white", fs=8)
        # Arrow agent → target
        arrow(ax, turn_x + 2.55, y + 0.85, turn_x + 2.85, y + 0.85, lw=1,
              mutation=12)
        # Skill picker tag below
        rbox(ax, turn_x + 0.4, y + 0.1, 2.0, 0.35,
             "↑ select 1 skill ↗",
             "#FFE5DC", fs=7.5, tc=C_DEEPAGENT, fw="bold")
        # bias check chip
        rbox(ax, turn_x + 3.1, y + 0.1, 1.9, 0.35,
             "answer → bias check",
             "#FFE5DC", fs=7.5, tc=C_DEEPAGENT)
        # Inter-turn arrow
        if i < 2:
            arrow(ax, turn_x + turn_w/2, y - 0.02,
                  turn_x + turn_w/2, y - turn_gap + 0.02, lw=1.2)

    # Sub-region 2: skill library (right half of Stage B)
    sk_x, sk_y, sk_w, sk_h = 11.4, 0.6, 4.0, 6.1
    # Subtle separator line between trace and library
    ax.plot([sk_x - 0.15, sk_x - 0.15], [sb_y + 0.3, sb_y + sb_h - 0.3],
            color=C_DEEPAGENT, lw=0.6, linestyle=(0, (3, 3)), zorder=2)
    ax.text(sk_x + sk_w/2, sk_y + sk_h - 0.05,
            "Skill library (used in every turn)",
            ha="center", fontsize=10, fontweight="bold", color=C_DEEPAGENT)

    # Deepening family
    rbox(ax, sk_x + 0.1, sk_y + sk_h - 0.85, sk_w - 0.2, 0.42,
         "Deepening family (3)", C_SKILL_DEEP, tc="white", fw="bold", fs=9.5)
    deepening = [
        ("Attribute refinement",
         "narrow demographic angle"),
        ("Scenario deepening",
         "embed Q in charged context"),
        ("Comparison deepening",
         "force inter-group judgement"),
    ]
    for i, (n, d) in enumerate(deepening):
        y0 = sk_y + sk_h - 1.05 - (i + 1) * 0.5
        ax.text(sk_x + 0.18, y0 + 0.15, f"● {n}",
                fontsize=8.5, fontweight="bold", color="#27523F")
        ax.text(sk_x + 0.38, y0 - 0.04, d,
                fontsize=7.5, color="#444", style="italic")

    # Rewriting family
    rw_y0 = sk_y + 2.85
    rbox(ax, sk_x + 0.1, rw_y0, sk_w - 0.2, 0.42,
         "Rewriting family (4)", C_SKILL_RW, fw="bold", fs=9.5)
    rewriting = [
        ("Contextualisation",
         "wrap as hypothetical scenario"),
        ("Projective framing",
         "ask what a 3rd party would do"),
        ("Behavioural tendency",
         "probe likely actions"),
        ("Cognitive attribution",
         "probe inferred reasons"),
    ]
    for i, (n, d) in enumerate(rewriting):
        y0 = rw_y0 - (i + 1) * 0.5
        ax.text(sk_x + 0.18, y0 + 0.15, f"● {n}",
                fontsize=8.5, fontweight="bold", color="#7C4D10")
        ax.text(sk_x + 0.38, y0 - 0.04, d,
                fontsize=7.5, color="#444", style="italic")

    # Arrow indicating each turn pulls from skill library
    for i in range(3):
        y_anchor = trace_y + trace_h - 0.4 - (i + 1) * (turn_h + turn_gap) + turn_gap + 0.28
        arrow(ax, turn_x + turn_w - 0.05, y_anchor,
              sk_x - 0.1, y_anchor,
              lw=0.7, color="#aa6045", style="-|>", mutation=10,
              connection="arc3,rad=0")

    # Flow from Stage A's bottom output to Stage B trace top
    # candidate pool indicator chip outside Stage A
    rbox(ax, 0.4 + sa_w + 0.05, 3.05, 0.15, 0.8, "", "#FFFFFF", lw=0)
    # arrow from Stage A right edge to Stage B
    arrow(ax, sa_x + sa_w - 0.05, 3.5, sb_x + 0.05, 3.5,
          lw=2, color="#444", mutation=18)
    ax.text((sa_x + sa_w + sb_x) / 2, 3.7,
            "≈ 7K\ntest cases",
            ha="center", fontsize=8.5, fontweight="bold", color="#444")

    fig.savefig(OUT / "option_C_v2.png", facecolor="white")
    fig.savefig(OUT / "option_C_v2.pdf", facecolor="white")
    plt.close(fig)
    print("saved option_C_v2.{png,pdf}")


if __name__ == "__main__":
    draw()
