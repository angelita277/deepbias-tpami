"""Stage A v3 — split the Proposer output into TWO branches feeding Target VLM:
  - Text branch (Q + context) goes straight down to Target VLM
  - Image-prompt branch goes to T2I (SDXL) → attribute-varied images → also to Target VLM
Target VLM thus receives BOTH text and images, not just images.
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
C_TEXT_DATA    = "#FFF6DC"   # yellow for text data
C_IMG_PROMPT   = "#FCE2D6"   # peach for image-prompt
C_DPO          = "#E5D7F2"
C_T2I          = "#D7E8DA"
C_IMG          = "#BFD9C3"
C_POS          = "#A8D5A9"
C_NEG          = "#F2B3B3"
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


def arrow(ax, x1, y1, x2, y2, lw=1.3, color=C_TXT, mutation=14,
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
    fig, ax = plt.subplots(figsize=(6.5, 9.8), dpi=180)
    ax.set_xlim(0, 6.5)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(3.25, 9.65, "Stage A v3 (text + image both feed Target VLM)",
            ha="center", fontsize=12, fontweight="bold")

    rbox(ax, 0.15, 0.25, 6.2, 9.1, "", C_PROPOSER_BG, ec=C_PROPOSER,
         lw=1.2, pad=0.02, rs=0.05)

    cx_left = 1.95     # text branch column center
    cx_right = 4.55    # image-prompt branch column center
    cx = 3.25          # global center

    # 1. ProposerAgent — full width
    rbox(ax, cx - 1.7, 8.45, 3.4, 0.55, "ProposerAgent  (Qwen3-32B)",
         C_PROPOSER, tc="white", fw="bold", fs=10)
    # Arrow down into 2-branch fork
    arrow(ax, cx, 8.45, cx, 8.15)

    # 2. Instruction output — small label box (fork point)
    rbox(ax, cx - 1.45, 7.55, 2.9, 0.55,
         "instruction package", "#FFFFFF", fs=9, fw="bold", ec="#888")

    # Fork arrows going to two branches
    arrow(ax, cx - 0.7, 7.55, cx_left, 7.0, lw=1.3,
          connection="arc3,rad=-0.05")
    arrow(ax, cx + 0.7, 7.55, cx_right, 7.0, lw=1.3,
          connection="arc3,rad=0.05")

    # --- LEFT BRANCH (text) ---
    # Q + context text box
    rbox(ax, cx_left - 1.5, 6.4, 3.0, 0.6,
         "Context + Question\n(text)", C_TEXT_DATA, fs=9, fw="bold")
    # Long straight arrow down through T2I row (text bypasses T2I)
    arrow(ax, cx_left, 6.4, cx_left, 3.85, lw=1.4)
    ax.text(cx_left - 1.5, 4.6, "text passes through\nunchanged",
            fontsize=7.5, color="#888", style="italic", ha="left", va="center")

    # --- RIGHT BRANCH (image prompts → T2I → images) ---
    rbox(ax, cx_right - 1.5, 6.4, 3.0, 0.6,
         "image prompts\n(text → for T2I)", C_IMG_PROMPT, fs=8.5, fw="bold")
    arrow(ax, cx_right, 6.4, cx_right, 6.1)

    # T2I
    rbox(ax, cx_right - 1.3, 5.5, 2.6, 0.55, "T2I  (SDXL)",
         C_T2I, fs=9.5, fw="bold")
    arrow(ax, cx_right, 5.5, cx_right, 5.25)

    # Stacked image cards
    img_w, img_h = 0.9, 1.0
    base_y = 4.2
    rect_bb = Rectangle((cx_right - img_w/2 + 0.32, base_y - 0.28),
                         img_w, img_h, fc="#90BC97", ec="#3C5A40",
                         lw=0.6, zorder=2)
    ax.add_patch(rect_bb)
    rect_b = Rectangle((cx_right - img_w/2 + 0.16, base_y - 0.14),
                        img_w, img_h, fc="#A8C9AE", ec="#3C5A40",
                        lw=0.7, zorder=3)
    ax.add_patch(rect_b)
    portrait_icon(ax, cx_right - img_w/2, base_y, img_w, img_h)
    ax.text(cx_right + img_w/2 + 0.35, base_y + img_h/2,
            "attribute-\nvaried\nimages",
            ha="left", va="center", fontsize=7, color="#666", style="italic")
    arrow(ax, cx_right, base_y - 0.08, cx_right, 3.85, lw=1.4)

    # --- MERGE into Target VLM ---
    # Target VLM box, wide
    rbox(ax, cx - 2.4, 3.25, 4.8, 0.6,
         "Target VLM  (receives Context + Question  +  images)",
         C_TARGET, tc="white", fs=9.5, fw="bold")
    arrow(ax, cx, 3.25, cx, 2.95)

    # decode chip
    rbox(ax, cx - 1.6, 2.45, 3.2, 0.45, "decode answer per image",
         "#F7F7F7", fs=8.5)
    arrow(ax, cx - 0.5, 2.45, cx - 1.2, 1.85, lw=1.3,
          connection="arc3,rad=-0.05")
    arrow(ax, cx + 0.5, 2.45, cx + 1.2, 1.85, lw=1.3,
          connection="arc3,rad=0.05")

    # pos / neg chips
    pos_w = 2.2
    rbox(ax, cx - 2.3, 1.25, pos_w, 0.55,
         "✓ non-Unknown  →  positive",
         C_POS, fs=8.5, fw="bold", tc="#1f5240")
    rbox(ax, cx + 0.1, 1.25, pos_w, 0.55,
         "✗ Unknown  →  negative",
         C_NEG, fs=8.5, fw="bold", tc="#7C2A2A")

    arrow(ax, cx - 1.2, 1.25, cx - 0.4, 0.75, lw=1.2,
          connection="arc3,rad=0.05")
    arrow(ax, cx + 1.2, 1.25, cx + 0.4, 0.75, lw=1.2,
          connection="arc3,rad=-0.05")

    # DPO preference pair
    rbox(ax, cx - 1.7, 0.4, 3.4, 0.45,
         "DPO preference pair", C_DPO, fs=9, fw="bold")

    # DPO closed-loop arrow back to ProposerAgent
    arrow(ax, 0.4, 0.65, 0.4, 8.7, lw=1.6, color="#7e6dad",
          connection="arc3,rad=-0.2", mutation=18)
    ax.text(0.6, 4.7, "DPO\nupdate",
            ha="left", fontsize=9, color="#7e6dad", fontweight="bold",
            rotation=90, va="center")

    fig.savefig(OUT / "stageA_v3_text_image_split.png", facecolor="white")
    fig.savefig(OUT / "stageA_v3_text_image_split.pdf", facecolor="white")
    plt.close(fig)
    print("saved stageA_v3_text_image_split.{png,pdf}")


if __name__ == "__main__":
    draw()
