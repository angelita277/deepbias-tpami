"""Stage A — Y variant + positive/negative sample split.

After Target VLM answers, branch the flow into two chips:
  ✓ non-Unknown  → positive sample
  ✗ Unknown      → negative sample
Both feed into the DPO preference pair box.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import matplotlib as mpl
from pathlib import Path

mpl.rcParams["font.family"] = "DejaVu Sans"
mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["savefig.dpi"] = 180
mpl.rcParams["savefig.bbox"] = "tight"

OUT = Path("/home/lianqi/papers/deepbias-tpami/figure2_options")

C_PROPOSER     = "#4A78C8"
C_PROPOSER_BG  = "#E9F0FA"
C_TARGET       = "#566573"
C_DATA         = "#FFF6DC"
C_DPO          = "#E5D7F2"
C_T2I          = "#D7E8DA"
C_IMG          = "#BFD9C3"
C_POS          = "#A8D5A9"  # green for positive sample
C_NEG          = "#F2B3B3"  # red for negative sample
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


def arrow(ax, x1, y1, x2, y2, lw=1.3, color=C_TEXT, mutation=14,
          style="-|>", connection="arc3,rad=0"):
    a = FancyArrowPatch((x1, y1), (x2, y2),
                         arrowstyle=style, color=color, lw=lw,
                         connectionstyle=connection,
                         mutation_scale=mutation, zorder=4)
    ax.add_patch(a)


def portrait_icon(ax, x, y, w, h, ec="#3C5A40"):
    bg = Rectangle((x, y), w, h, fc=C_IMG, ec=ec, lw=0.8, zorder=3)
    ax.add_patch(bg)
    head_r = min(w, h) * 0.18
    ax.add_patch(Circle((x + w/2, y + h*0.62), head_r,
                         fc="#9BBFA1", ec=ec, lw=0.6, zorder=4))
    shoulder = FancyBboxPatch((x + w*0.18, y + h*0.18), w*0.64, h*0.22,
                               boxstyle="round,pad=0,rounding_size=0.04",
                               fc="#9BBFA1", ec=ec, lw=0.6, zorder=4)
    ax.add_patch(shoulder)


def draw():
    fig, ax = plt.subplots(figsize=(5.2, 9.6), dpi=180)
    ax.set_xlim(0, 5.2)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(2.6, 9.65, "Stage A (Y + pos/neg split)",
            ha="center", fontsize=13, fontweight="bold")

    # Outer Stage A box
    rbox(ax, 0.15, 0.25, 4.9, 9.1, "", C_PROPOSER_BG, ec=C_PROPOSER,
         lw=1.2, pad=0.02, rs=0.05)

    cx = 2.6

    # 1. ProposerAgent
    rbox(ax, cx - 1.5, 8.45, 3.0, 0.55, "ProposerAgent  (Qwen3-32B)",
         C_PROPOSER, tc="white", fw="bold", fs=10)
    arrow(ax, cx, 8.45, cx, 8.15)

    # 2. Instruction
    rbox(ax, cx - 1.7, 7.55, 3.4, 0.55, "Q + image prompt",
         C_DATA, fs=9.5)
    arrow(ax, cx, 7.55, cx, 7.25)

    # 3. T2I
    rbox(ax, cx - 1.5, 6.65, 3.0, 0.55, "T2I  (SDXL)",
         C_T2I, fs=10, fw="bold")
    arrow(ax, cx, 6.65, cx, 6.35)

    # 4. Stacked image cards
    img_w, img_h = 1.0, 1.1
    base_y = 5.15
    rect_bb = Rectangle((cx - img_w/2 + 0.36, base_y - 0.3),
                         img_w, img_h, fc="#90BC97", ec="#3C5A40", lw=0.6, zorder=2)
    ax.add_patch(rect_bb)
    rect_b = Rectangle((cx - img_w/2 + 0.18, base_y - 0.15),
                        img_w, img_h, fc="#A8C9AE", ec="#3C5A40", lw=0.7, zorder=3)
    ax.add_patch(rect_b)
    portrait_icon(ax, cx - img_w/2, base_y, img_w, img_h)
    ax.text(cx + img_w/2 + 0.45, base_y + img_h/2,
            "attribute-\nvaried\nimages",
            ha="left", va="center", fontsize=7.5, color="#666", style="italic")
    arrow(ax, cx, base_y - 0.05, cx, 4.5)

    # 5. Target VLM
    rbox(ax, cx - 1.7, 3.95, 3.4, 0.55, "Target VLM",
         C_TARGET, tc="white", fs=10, fw="bold")
    arrow(ax, cx, 3.95, cx, 3.7)

    # 6. Branch indicator — "decode each image's answer"
    rbox(ax, cx - 1.4, 3.15, 2.8, 0.45, "decode answer per image",
         "#F7F7F7", fs=8.5)
    # Branch arrows downward to two chips
    arrow(ax, cx - 0.45, 3.15, cx - 1.1, 2.55, lw=1.3,
          connection="arc3,rad=-0.05")
    arrow(ax, cx + 0.45, 3.15, cx + 1.1, 2.55, lw=1.3,
          connection="arc3,rad=0.05")

    # 7. Pos / Neg chips
    pos_w = 2.0
    rbox(ax, cx - 2.15, 1.95, pos_w, 0.55,
         "✓ non-Unknown\n→ positive",
         C_POS, fs=8.5, fw="bold", tc="#1f5240")
    rbox(ax, cx + 0.15, 1.95, pos_w, 0.55,
         "✗ Unknown\n→ negative",
         C_NEG, fs=8.5, fw="bold", tc="#7C2A2A")

    # Converging arrows into DPO preference pair
    arrow(ax, cx - 1.15, 1.95, cx - 0.5, 1.4, lw=1.2,
          connection="arc3,rad=0.05")
    arrow(ax, cx + 1.15, 1.95, cx + 0.5, 1.4, lw=1.2,
          connection="arc3,rad=-0.05")

    # 8. DPO preference pair
    rbox(ax, cx - 1.6, 0.8, 3.2, 0.55,
         "DPO preference pair  (pos vs neg)",
         C_DPO, fs=9, fw="bold")

    # 9. DPO closed-loop arrow back to ProposerAgent
    arrow(ax, 0.4, 1.05, 0.4, 8.7, lw=1.6, color="#7e6dad",
          connection="arc3,rad=-0.22", mutation=18)
    ax.text(0.62, 4.85, "DPO\nupdate",
            ha="left", fontsize=9, color="#7e6dad", fontweight="bold",
            rotation=90, va="center")

    fig.savefig(OUT / "stageA_Y_with_posneg.png", facecolor="white")
    fig.savefig(OUT / "stageA_Y_with_posneg.pdf", facecolor="white")
    plt.close(fig)
    print("saved stageA_Y_with_posneg.{png,pdf}")


if __name__ == "__main__":
    draw()
