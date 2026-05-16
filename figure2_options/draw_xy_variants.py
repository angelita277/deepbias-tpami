"""Sketch the two T2I-output variants (X: single image + ×N tag, Y: stacked cards)
so the user can decide how to soft-pedal the triplet in Stage A.

Each variant shows the full mini-vertical-flow of Stage A so the user can see
how it slots into the figure, not just the icon in isolation.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
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
    """A small portrait icon — head circle + shoulders trapezoid."""
    bg = Rectangle((x, y), w, h, fc=C_IMG, ec=ec, lw=0.8, zorder=3)
    ax.add_patch(bg)
    # Head
    from matplotlib.patches import Circle
    head_r = min(w, h) * 0.18
    ax.add_patch(Circle((x + w/2, y + h*0.62), head_r,
                         fc="#9BBFA1", ec=ec, lw=0.6, zorder=4))
    # Shoulders — simple arc
    from matplotlib.patches import FancyBboxPatch as FB
    shoulder = FB((x + w*0.18, y + h*0.18), w*0.64, h*0.22,
                   boxstyle="round,pad=0,rounding_size=0.04",
                   fc="#9BBFA1", ec=ec, lw=0.6, zorder=4)
    ax.add_patch(shoulder)


def draw_variant_X(ax, x0):
    """X — single image with ×N attribute-variants subscript."""
    cx = x0 + 1.7
    # Title
    ax.text(cx, 7.6, "X — single image + ×N tag",
            ha="center", fontsize=12, fontweight="bold")
    ax.text(cx, 7.25, "(triplet detail goes to caption)",
            ha="center", fontsize=8.5, color="#666", style="italic")

    # Outer Stage A box
    rbox(ax, x0 + 0.1, 0.4, 3.2, 6.5, "", C_PROPOSER_BG, ec=C_PROPOSER,
         lw=1.2, pad=0.02, rs=0.05)

    # 1. ProposerAgent
    rbox(ax, cx - 1.1, 6.0, 2.2, 0.55, "ProposerAgent",
         C_PROPOSER, tc="white", fw="bold", fs=9.5)
    arrow(ax, cx, 6.0, cx, 5.75)

    # 2. Instruction
    rbox(ax, cx - 1.3, 5.2, 2.6, 0.5, "Q + image prompt", C_DATA, fs=8.5)
    arrow(ax, cx, 5.2, cx, 4.95)

    # 3. T2I
    rbox(ax, cx - 1.1, 4.4, 2.2, 0.5, "T2I (SDXL)", C_T2I, fs=9.5, fw="bold")
    arrow(ax, cx, 4.4, cx, 4.15)

    # 4. Single image with ×N tag
    img_w, img_h = 0.95, 1.0
    portrait_icon(ax, cx - img_w/2, 3.05, img_w, img_h)
    # ×N tag — small chip to the right of the image
    rbox(ax, cx + img_w/2 + 0.08, 3.4, 0.55, 0.3, "×N",
         "#FFE5DC", fs=8.5, fw="bold", tc="#D86A4A", rs=0.04, pad=0.01)
    ax.text(cx + img_w/2 + 0.08 + 0.65, 3.25, "attribute\nvariants",
            ha="left", va="top", fontsize=6.5, color="#666", style="italic")
    arrow(ax, cx, 3.05, cx, 2.65)

    # 5. Target VLM
    rbox(ax, cx - 1.3, 2.1, 2.6, 0.5, "Target VLM", C_TARGET,
         tc="white", fs=9.5, fw="bold")
    arrow(ax, cx, 2.1, cx, 1.85)

    # 6. Bias signal
    rbox(ax, cx - 1.3, 1.3, 2.6, 0.5, "bias → preference", C_DPO,
         fs=8.5, fw="bold")

    # DPO loop
    arrow(ax, x0 + 0.25, 1.55, x0 + 0.25, 6.25, lw=1.4, color="#7e6dad",
          connection="arc3,rad=-0.25", mutation=16)
    ax.text(x0 + 0.4, 3.8, "DPO",
            ha="left", fontsize=8, color="#7e6dad", fontweight="bold",
            rotation=90, va="center")


def draw_variant_Y(ax, x0):
    """Y — stacked half-overlapping cards as abstract image bank."""
    cx = x0 + 1.7
    ax.text(cx, 7.6, "Y — stacked image cards",
            ha="center", fontsize=12, fontweight="bold")
    ax.text(cx, 7.25, "(multi-image hinted, '3' not emphasised)",
            ha="center", fontsize=8.5, color="#666", style="italic")

    rbox(ax, x0 + 0.1, 0.4, 3.2, 6.5, "", C_PROPOSER_BG, ec=C_PROPOSER,
         lw=1.2, pad=0.02, rs=0.05)

    # 1. ProposerAgent
    rbox(ax, cx - 1.1, 6.0, 2.2, 0.55, "ProposerAgent",
         C_PROPOSER, tc="white", fw="bold", fs=9.5)
    arrow(ax, cx, 6.0, cx, 5.75)

    # 2. Instruction
    rbox(ax, cx - 1.3, 5.2, 2.6, 0.5, "Q + image prompt", C_DATA, fs=8.5)
    arrow(ax, cx, 5.2, cx, 4.95)

    # 3. T2I
    rbox(ax, cx - 1.1, 4.4, 2.2, 0.5, "T2I (SDXL)", C_T2I, fs=9.5, fw="bold")
    arrow(ax, cx, 4.4, cx, 4.15)

    # 4. Stacked cards — back-to-front
    img_w, img_h = 0.95, 1.0
    base_y = 2.95
    offsets = [(0.18, -0.15, "#A8C9AE", "#5A8062"),   # back card
               (0.0, 0.0, "#BFD9C3", "#3C5A40")]      # main card slightly offset
    # back-back card
    rect_bb = Rectangle((cx - img_w/2 + 0.36, base_y - 0.3),
                         img_w, img_h, fc="#90BC97", ec="#3C5A40", lw=0.6, zorder=2)
    ax.add_patch(rect_bb)
    # back card
    rect_b = Rectangle((cx - img_w/2 + 0.18, base_y - 0.15),
                        img_w, img_h, fc="#A8C9AE", ec="#3C5A40", lw=0.7, zorder=3)
    ax.add_patch(rect_b)
    # front card (full portrait)
    portrait_icon(ax, cx - img_w/2, base_y, img_w, img_h)
    ax.text(cx + img_w/2 + 0.35, base_y + img_h/2,
            "attribute-\nvaried\nimages",
            ha="left", va="center", fontsize=7, color="#666", style="italic")
    arrow(ax, cx, base_y, cx, 2.65)

    # 5. Target VLM
    rbox(ax, cx - 1.3, 2.1, 2.6, 0.5, "Target VLM", C_TARGET,
         tc="white", fs=9.5, fw="bold")
    arrow(ax, cx, 2.1, cx, 1.85)

    # 6. Bias signal
    rbox(ax, cx - 1.3, 1.3, 2.6, 0.5, "bias → preference", C_DPO,
         fs=8.5, fw="bold")

    arrow(ax, x0 + 0.25, 1.55, x0 + 0.25, 6.25, lw=1.4, color="#7e6dad",
          connection="arc3,rad=-0.25", mutation=16)
    ax.text(x0 + 0.4, 3.8, "DPO",
            ha="left", fontsize=8, color="#7e6dad", fontweight="bold",
            rotation=90, va="center")


def draw():
    fig, ax = plt.subplots(figsize=(8, 8.5), dpi=170)
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.text(4, 7.85, "Stage A — T2I variant comparison",
            ha="center", fontsize=14, fontweight="bold")

    draw_variant_X(ax, x0=0.1)
    draw_variant_Y(ax, x0=4.4)

    fig.savefig(OUT / "stageA_xy_variants.png", facecolor="white")
    fig.savefig(OUT / "stageA_xy_variants.pdf", facecolor="white")
    plt.close(fig)
    print("saved stageA_xy_variants.{png,pdf}")


if __name__ == "__main__":
    draw()
