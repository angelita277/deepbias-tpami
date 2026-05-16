"""Full Figure 2 — Stage A v3 (with text/image split + pos/neg branching)
                  + Stage B (multi-turn trace + skill library).

Left ~1/3: Stage A (offline DPO training of ProposerAgent).
Right ~2/3: Stage B (online multi-turn DeepAgent probing), with skill
library as the second sub-panel inside the unified Stage B container.

Pool funnel between A and B.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle, Polygon
import matplotlib as mpl
from pathlib import Path

mpl.rcParams["font.family"] = "DejaVu Sans"
mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["savefig.dpi"] = 180
mpl.rcParams["savefig.bbox"] = "tight"

OUT = Path("/home/lianqi/papers/deepbias-tpami/figure2_options")

C_PROPOSER     = "#4A78C8"
C_PROPOSER_BG  = "#EDF3FB"
C_DEEPAGENT    = "#D86A4A"
C_DEEPAGENT_BG = "#FDF1EA"
C_TARGET       = "#566573"
C_TEXT_DATA    = "#FFF6DC"
C_IMG_PROMPT   = "#FCE2D6"
C_DPO          = "#E5D7F2"
C_T2I          = "#D7E8DA"
C_IMG          = "#BFD9C3"
C_POS          = "#A8D5A9"
C_NEG          = "#F2B3B3"
C_SKILL_DEEP   = "#4F9B86"
C_SKILL_RW     = "#E0A267"
C_POOL         = "#B9D8C2"
C_TXT          = "#222"


def rbox(ax, x, y, w, h, label, fc, ec=C_TXT, lw=1.0, fs=9, fw="normal",
         tc="black", pad=0.03, rs=0.06):
    box = FancyBboxPatch((x, y), w, h,
                          boxstyle=f"round,pad={pad},rounding_size={rs}",
                          fc=fc, ec=ec, lw=lw, zorder=2)
    ax.add_patch(box)
    if label:
        ax.text(x + w/2, y + h/2, label, ha="center", va="center",
                fontsize=fs, fontweight=fw, color=tc, zorder=3)


def arrow(ax, x1, y1, x2, y2, lw=1.2, color=C_TXT, mutation=13,
          style="-|>", connection="arc3,rad=0"):
    a = FancyArrowPatch((x1, y1), (x2, y2),
                         arrowstyle=style, color=color, lw=lw,
                         connectionstyle=connection,
                         mutation_scale=mutation, zorder=4)
    ax.add_patch(a)


def portrait_icon(ax, x, y, w, h, ec="#3C5A40"):
    bg = Rectangle((x, y), w, h, fc=C_IMG, ec=ec, lw=0.7, zorder=3)
    ax.add_patch(bg)
    head_r = min(w, h) * 0.18
    ax.add_patch(Circle((x + w/2, y + h*0.62), head_r,
                         fc="#9BBFA1", ec=ec, lw=0.5, zorder=4))
    shoulder = FancyBboxPatch((x + w*0.18, y + h*0.18), w*0.64, h*0.22,
                               boxstyle="round,pad=0,rounding_size=0.04",
                               fc="#9BBFA1", ec=ec, lw=0.5, zorder=4)
    ax.add_patch(shoulder)


def funnel(ax, x_cx, y_top, y_bot, w_top, w_bot, fc=C_POOL, ec=C_TXT, lw=1.0):
    poly = Polygon([
        (x_cx - w_top/2, y_top),
        (x_cx + w_top/2, y_top),
        (x_cx + w_bot/2, y_bot),
        (x_cx - w_bot/2, y_bot),
    ], closed=True, fc=fc, ec=ec, lw=lw, zorder=2)
    ax.add_patch(poly)


# =========================================================================
def draw():
    fig, ax = plt.subplots(figsize=(17, 9.8), dpi=170)
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # ----------------- Header bar (2 segments) -----------------
    rbox(ax, 0.3, 9.2, 5.8, 0.55,
         "Stage A — train ProposerAgent (offline DPO)",
         C_PROPOSER, tc="white", fw="bold", fs=12, ec=C_PROPOSER, rs=0.08)
    rbox(ax, 6.4, 9.2, 11.3, 0.55,
         "Stage B — probe Target VLM with DeepAgent (online, skill-driven)",
         C_DEEPAGENT, tc="white", fw="bold", fs=12, ec=C_DEEPAGENT, rs=0.08)
    arrow(ax, 6.15, 9.475, 6.4, 9.475, lw=1.6, mutation=18)

    # =========================================================
    # Stage A — left column with text/image split + pos/neg
    # =========================================================
    sa_x, sa_y, sa_w, sa_h = 0.3, 0.3, 5.8, 8.7
    rbox(ax, sa_x, sa_y, sa_w, sa_h, "", C_PROPOSER_BG, ec=C_PROPOSER,
         lw=1.4, pad=0.02, rs=0.04)

    cx_a = sa_x + sa_w / 2
    cx_left = cx_a - 1.3      # text branch
    cx_right = cx_a + 1.3     # image-prompt branch

    # 1. ProposerAgent (centered, wide)
    rbox(ax, cx_a - 1.9, 8.25, 3.8, 0.55,
         "ProposerAgent (Qwen3-32B)",
         C_PROPOSER, tc="white", fw="bold", fs=10)
    arrow(ax, cx_a, 8.25, cx_a, 7.95)

    # 2. Instruction package
    rbox(ax, cx_a - 1.6, 7.4, 3.2, 0.55,
         "instruction package",
         "#FFFFFF", fs=9.5, fw="bold", ec="#888")

    # Fork arrows
    arrow(ax, cx_a - 0.8, 7.4, cx_left, 6.85, lw=1.2,
          connection="arc3,rad=-0.05")
    arrow(ax, cx_a + 0.8, 7.4, cx_right, 6.85, lw=1.2,
          connection="arc3,rad=0.05")

    # 3. Text branch
    rbox(ax, cx_left - 1.05, 6.3, 2.1, 0.6,
         "Context\n+ Question",
         C_TEXT_DATA, fs=8.5, fw="bold")
    arrow(ax, cx_left, 6.3, cx_left, 4.5, lw=1.3)
    ax.text(cx_left - 1.0, 5.4, "text\nunchanged",
            fontsize=7, color="#888", style="italic", ha="left", va="center")

    # 4. Image-prompt branch
    rbox(ax, cx_right - 1.05, 6.3, 2.1, 0.6,
         "image\nprompts",
         C_IMG_PROMPT, fs=8.5, fw="bold")
    arrow(ax, cx_right, 6.3, cx_right, 6.05)
    # T2I
    rbox(ax, cx_right - 1.0, 5.55, 2.0, 0.5, "T2I (SDXL)",
         C_T2I, fs=9.5, fw="bold")
    arrow(ax, cx_right, 5.55, cx_right, 5.25)
    # Stacked image cards
    img_w, img_h = 0.85, 0.85
    base_y = 4.3
    rect_bb = Rectangle((cx_right - img_w/2 + 0.28, base_y - 0.22),
                         img_w, img_h, fc="#90BC97", ec="#3C5A40",
                         lw=0.5, zorder=2)
    ax.add_patch(rect_bb)
    rect_b = Rectangle((cx_right - img_w/2 + 0.14, base_y - 0.11),
                        img_w, img_h, fc="#A8C9AE", ec="#3C5A40",
                        lw=0.6, zorder=3)
    ax.add_patch(rect_b)
    portrait_icon(ax, cx_right - img_w/2, base_y, img_w, img_h)
    ax.text(cx_right + img_w/2 + 0.32, base_y + img_h/2,
            "attr-\nvaried\nimgs",
            ha="left", va="center", fontsize=6.5, color="#666", style="italic")
    arrow(ax, cx_right, base_y - 0.05, cx_right, 4.5, lw=1.3)

    # 5. Target VLM
    rbox(ax, cx_a - 2.4, 3.85, 4.8, 0.6,
         "Target VLM  (Context + Question + images)",
         C_TARGET, tc="white", fs=9.5, fw="bold")
    arrow(ax, cx_a, 3.85, cx_a, 3.55)

    # decode chip
    rbox(ax, cx_a - 1.6, 3.05, 3.2, 0.45, "decode answer per image",
         "#F7F7F7", fs=8.5)
    arrow(ax, cx_a - 0.55, 3.05, cx_a - 1.25, 2.4, lw=1.2,
          connection="arc3,rad=-0.05")
    arrow(ax, cx_a + 0.55, 3.05, cx_a + 1.25, 2.4, lw=1.2,
          connection="arc3,rad=0.05")

    # pos / neg
    pos_w = 2.3
    rbox(ax, cx_a - 2.45, 1.75, pos_w, 0.55,
         "✓ non-Unknown\n→ positive",
         C_POS, fs=8.2, fw="bold", tc="#1f5240")
    rbox(ax, cx_a + 0.15, 1.75, pos_w, 0.55,
         "✗ Unknown\n→ negative",
         C_NEG, fs=8.2, fw="bold", tc="#7C2A2A")
    arrow(ax, cx_a - 1.3, 1.75, cx_a - 0.55, 1.2, lw=1.2,
          connection="arc3,rad=0.05")
    arrow(ax, cx_a + 1.3, 1.75, cx_a + 0.55, 1.2, lw=1.2,
          connection="arc3,rad=-0.05")

    # DPO preference pair
    rbox(ax, cx_a - 1.7, 0.7, 3.4, 0.5,
         "DPO preference pair",
         C_DPO, fs=9, fw="bold")

    # DPO closed loop — drawn outside on the far left
    arrow(ax, sa_x + 0.18, 0.95, sa_x + 0.18, 8.55, lw=1.6,
          color="#7e6dad", connection="arc3,rad=-0.2", mutation=16)
    ax.text(sa_x + 0.36, 4.7, "DPO update",
            ha="left", fontsize=9, color="#7e6dad", fontweight="bold",
            rotation=90, va="center")

    # =========================================================
    # Pool funnel between Stage A and Stage B
    # =========================================================
    funnel(ax, 6.25, 5.3, 4.5, 0.5, 0.3)
    ax.text(6.25, 4.25, "≈ 7K\ntest cases",
            ha="center", fontsize=8, color="#444", fontweight="bold")
    arrow(ax, sa_x + sa_w + 0.05, 4.8, 6.0, 4.8, lw=1.6, mutation=15)
    arrow(ax, 6.5, 4.8, 6.65, 4.8, lw=1.6, mutation=15)

    # =========================================================
    # Stage B — unified outer container, two sub-panels
    # =========================================================
    sb_x, sb_y, sb_w, sb_h = 6.4, 0.3, 11.3, 8.7
    rbox(ax, sb_x, sb_y, sb_w, sb_h, "", C_DEEPAGENT_BG, ec=C_DEEPAGENT,
         lw=1.5, pad=0.02, rs=0.05)

    # Sub-region 1: Multi-turn trace (left half of Stage B)
    trace_x, trace_y, trace_w, trace_h = 6.65, 0.55, 6.4, 8.3
    ax.text(trace_x + trace_w/2, trace_y + trace_h - 0.08,
            "Multi-turn trace (one episode)",
            ha="center", fontsize=10.5, fontweight="bold", color=C_DEEPAGENT)

    # 3 turn cards stacked vertically
    turn_h = 2.1
    turn_gap = 0.15
    turn_w = trace_w - 0.4
    turn_x_inner = trace_x + 0.2
    for i, lbl in enumerate(["Turn 1", "Turn 2", "Turn 3"]):
        y = trace_y + trace_h - 0.45 - (i + 1) * (turn_h + turn_gap) + turn_gap
        rbox(ax, turn_x_inner, y, turn_w, turn_h, "", "#FFFFFF", ec="#999",
             lw=0.8, pad=0.02)
        rbox(ax, turn_x_inner + 0.12, y + turn_h - 0.4, 0.95, 0.32, lbl,
             "#F2F2F2", fs=8.5, fw="bold")
        # DeepAgent rewrite
        rbox(ax, turn_x_inner + 0.18, y + 0.95, 2.7, 0.55,
             "DeepAgent rewrites Q",
             C_DEEPAGENT, tc="white", fs=8.5, fw="bold")
        # Target answer
        rbox(ax, turn_x_inner + 3.1, y + 0.95, 2.7, 0.55,
             "Target VLM answers",
             C_TARGET, tc="white", fs=8.5)
        arrow(ax, turn_x_inner + 2.88, y + 1.22,
              turn_x_inner + 3.1, y + 1.22, lw=1, mutation=11)
        # Skill picker
        rbox(ax, turn_x_inner + 0.4, y + 0.32, 2.3, 0.42,
             "↑ select 1 skill ↗",
             "#FFE5DC", fs=8, tc=C_DEEPAGENT, fw="bold")
        # bias check
        rbox(ax, turn_x_inner + 3.3, y + 0.32, 2.3, 0.42,
             "answer → bias check",
             "#FFE5DC", fs=8, tc=C_DEEPAGENT)
        if i < 2:
            arrow(ax, turn_x_inner + turn_w/2, y - 0.02,
                  turn_x_inner + turn_w/2, y - turn_gap + 0.02, lw=1.2,
                  mutation=12)

    # Sub-region 2: Skill library (right half of Stage B)
    sk_x, sk_y, sk_w, sk_h = 13.3, 0.55, 4.25, 8.3
    # Dashed separator
    ax.plot([sk_x - 0.18, sk_x - 0.18], [sb_y + 0.3, sb_y + sb_h - 0.3],
            color=C_DEEPAGENT, lw=0.7, linestyle=(0, (3, 3)), zorder=2)
    ax.text(sk_x + sk_w/2, sk_y + sk_h - 0.08,
            "Skill library (used in every turn)",
            ha="center", fontsize=10.5, fontweight="bold", color=C_DEEPAGENT)

    # Deepening family
    rbox(ax, sk_x + 0.1, sk_y + sk_h - 1.0, sk_w - 0.2, 0.45,
         "Deepening family (3)", C_SKILL_DEEP,
         tc="white", fw="bold", fs=10)
    deepening = [
        ("Attribute refinement", "narrow demographic angle"),
        ("Scenario deepening",   "embed Q in charged context"),
        ("Comparison deepening", "force inter-group judgement"),
    ]
    for i, (n, d) in enumerate(deepening):
        y0 = sk_y + sk_h - 1.2 - (i + 1) * 0.65
        ax.text(sk_x + 0.2, y0 + 0.22, f"● {n}",
                fontsize=9, fontweight="bold", color="#27523F")
        ax.text(sk_x + 0.4, y0 - 0.02, d,
                fontsize=8, color="#444", style="italic")

    # Rewriting family
    rw_y0 = sk_y + 3.6
    rbox(ax, sk_x + 0.1, rw_y0, sk_w - 0.2, 0.45,
         "Rewriting family (4)", C_SKILL_RW, fw="bold", fs=10)
    rewriting = [
        ("Contextualisation",     "hypothetical-scenario wrap"),
        ("Projective framing",    "3rd-party perspective"),
        ("Behavioural tendency",  "likely actions"),
        ("Cognitive attribution", "inferred reasons"),
    ]
    for i, (n, d) in enumerate(rewriting):
        y0 = rw_y0 - (i + 1) * 0.65
        ax.text(sk_x + 0.2, y0 + 0.22, f"● {n}",
                fontsize=9, fontweight="bold", color="#7C4D10")
        ax.text(sk_x + 0.4, y0 - 0.02, d,
                fontsize=8, color="#444", style="italic")

    # Arrows from each turn's "select 1 skill" → skill library
    for i in range(3):
        y_anchor = trace_y + trace_h - 0.45 - (i + 1) * (turn_h + turn_gap) + turn_gap + 0.53
        arrow(ax, turn_x_inner + turn_w - 0.05, y_anchor,
              sk_x - 0.1, y_anchor,
              lw=0.7, color="#aa6045", style="-|>", mutation=8)

    fig.savefig(OUT / "figure2_full.png", facecolor="white")
    fig.savefig(OUT / "figure2_full.pdf", facecolor="white")
    plt.close(fig)
    print("saved figure2_full.{png,pdf}")


if __name__ == "__main__":
    draw()
