"""Stage A v7 sketch — show the paired-track decomposition.

Key visualisation goal:
  1. ProposerAgent emits compound cards (each card = 2 stripes:
     top yellow = Ctx+Q text, bottom peach = image prompts).
  2. Cards decompose into TWO parallel tracks that REMAIN PAIRED
     (sample-i text card linked to sample-i image card by a thin
     dotted vertical line).
  3. Top track: text passes straight, bypasses T2I.
     Bottom track: image-prompts enter T2I, exit as Images.
  4. Both tracks converge into Target VLM (one arrow from top,
     one arrow from bottom). The fact that Target VLM consumes a
     paired (text, images) multimodal input is shown by the
     pairing lines persisting all the way through.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon
import matplotlib as mpl
from pathlib import Path

mpl.rcParams["font.family"] = "DejaVu Sans"
mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["savefig.dpi"] = 180
mpl.rcParams["savefig.bbox"] = "tight"

OUT = Path("/home/lianqi/papers/deepbias-tpami/figure2_options")

# Palette
C_PROPOSER     = "#4A78C8"
C_TARGET       = "#566573"
C_T2I          = "#7FB8A3"
C_TEXT_STRIPE  = "#FFF6DC"   # yellow-cream for Ctx+Q
C_IMG_STRIPE   = "#FCE2D6"   # peach for image prompts
C_RENDERED_IMG = "#CDE7CC"   # mint for rendered Images
C_DPO          = "#7e6dad"
C_POS_BG       = "#DEF0DC"
C_POS_BORDER   = "#5A9F5A"
C_NEG_BG       = "#F8DCDC"
C_NEG_BORDER   = "#A35454"
C_PAIR_LINE    = "#999999"
C_TXT          = "#222"


def rbox(ax, x, y, w, h, label, fc, ec=C_TXT, lw=1.0, fs=9, fw="normal",
         tc="black", pad=0.02, rs=0.05, ha="center", va="center"):
    box = FancyBboxPatch((x, y), w, h,
                          boxstyle=f"round,pad={pad},rounding_size={rs}",
                          fc=fc, ec=ec, lw=lw, zorder=3)
    ax.add_patch(box)
    if label:
        ax.text(x + w/2 if ha == "center" else x + 0.08,
                y + h/2 if va == "center" else y + h - 0.1,
                label, ha=ha, va=va,
                fontsize=fs, fontweight=fw, color=tc, zorder=4)


def arrow(ax, x1, y1, x2, y2, lw=1.3, color=C_TXT, mutation=14,
          style="-|>", connection="arc3,rad=0"):
    a = FancyArrowPatch((x1, y1), (x2, y2),
                         arrowstyle=style, color=color, lw=lw,
                         connectionstyle=connection,
                         mutation_scale=mutation, zorder=5)
    ax.add_patch(a)


def compound_card_stack(ax, x_center, y_base, w, h, n=3, gap=0.18):
    """Draw a stack of n compound two-stripe cards (Ctx+Q on top, image
    prompts on bottom)."""
    centers = []
    for i in range(n):
        x = x_center - w/2 + i * gap
        y = y_base - i * gap * 0.6
        # Outer card
        Rectangle((x, y), w, h, fc="white", ec="#444", lw=0.8, zorder=3 + i)
        # We need to add patches in order. Build manually:
        outer = Rectangle((x, y), w, h, fc="white", ec="#666",
                           lw=0.8, zorder=3 + i)
        ax.add_patch(outer)
        # Top stripe (Ctx+Q)
        ax.add_patch(Rectangle((x + 0.04, y + h/2 + 0.02),
                                w - 0.08, h/2 - 0.06,
                                fc=C_TEXT_STRIPE, ec="none",
                                zorder=3 + i + 0.1))
        # Bottom stripe (image prompts)
        ax.add_patch(Rectangle((x + 0.04, y + 0.04),
                                w - 0.08, h/2 - 0.06,
                                fc=C_IMG_STRIPE, ec="none",
                                zorder=3 + i + 0.1))
        # Labels only on the FRONTMOST card
        if i == n - 1:
            ax.text(x + w/2, y + h*0.75,
                    "Ctx + Q", ha="center", va="center",
                    fontsize=7.5, fontweight="bold", color="#444",
                    zorder=10)
            ax.text(x + w/2, y + h*0.25,
                    "image prompts", ha="center", va="center",
                    fontsize=7.5, fontweight="bold", color="#7a4a20",
                    zorder=10)
        centers.append((x + w/2, y + h/2, y + h*0.75, y + h*0.25))
    return centers


def text_card(ax, x, y, w, h, label="Ctx + Q"):
    ax.add_patch(Rectangle((x, y), w, h, fc=C_TEXT_STRIPE,
                            ec="#888", lw=0.7, zorder=3))
    ax.text(x + w/2, y + h/2, label, ha="center", va="center",
            fontsize=7.5, fontweight="bold", color="#7a6020", zorder=4)


def image_prompt_card(ax, x, y, w, h, label="image\nprompts"):
    ax.add_patch(Rectangle((x, y), w, h, fc=C_IMG_STRIPE,
                            ec="#888", lw=0.7, zorder=3))
    ax.text(x + w/2, y + h/2, label, ha="center", va="center",
            fontsize=7, fontweight="bold", color="#7a4a20", zorder=4)


def rendered_image_card(ax, x, y, w, h):
    ax.add_patch(Rectangle((x, y), w, h, fc=C_RENDERED_IMG,
                            ec="#5a8c5a", lw=0.7, zorder=3))
    # Draw three tiny silhouettes inside
    for k in range(3):
        cx = x + 0.18 + k * (w - 0.36) / 2
        ax.add_patch(Rectangle((cx - 0.05, y + 0.08), 0.1, h - 0.16,
                                fc="#9ec39a", ec="#3C5A40",
                                lw=0.4, zorder=4))
        # tiny head
        from matplotlib.patches import Circle
        ax.add_patch(Circle((cx, y + h - 0.13), 0.035,
                             fc="#abc7a8", ec="#3C5A40",
                             lw=0.4, zorder=5))


def pool_box(ax, x, y, w, h, kind="pos"):
    bg = C_POS_BG if kind == "pos" else C_NEG_BG
    bd = C_POS_BORDER if kind == "pos" else C_NEG_BORDER
    rbox(ax, x, y, w, h, "", bg, ec=bd, lw=1.0, pad=0.02, rs=0.04)
    label = "🟢 Positive samples\n(x⁺, y) — bias triggered" \
        if kind == "pos" else "🔴 Negative samples\n(x⁻, y) — no bias"
    ax.text(x + 0.1, y + h - 0.18, label, ha="left", va="top",
            fontsize=8, fontweight="bold",
            color="#1f5240" if kind == "pos" else "#7C2A2A",
            zorder=5)
    # 3 stacked chip-cards inside
    for k in range(3):
        cx = x + 0.16 + k * (w - 0.32) / 2 - 0.05
        cy = y + 0.18
        chip_color = "#F2B3B3" if kind == "pos" else "#A8D5A9"
        rbox(ax, cx, cy, 0.45, 0.4, "✗" if kind == "pos" else "✓",
             chip_color, ec="#444", lw=0.5, fs=10, fw="bold",
             rs=0.04, pad=0.005, tc="#222")


def draw():
    fig_w, fig_h = 16, 8.8
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=170)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # Title
    ax.text(fig_w / 2, fig_h - 0.4,
            "Stage A sketch (v7) — paired text/image tracks with sample-aligned dotted connectors",
            ha="center", va="center", fontsize=12, fontweight="bold",
            color="#222")
    ax.text(fig_w / 2, fig_h - 0.85,
            "ProposerAgent emits compound 2-stripe cards → decompose into 2 parallel tracks → pairing preserved → both reach Target VLM",
            ha="center", va="center", fontsize=9.5, color="#666",
            style="italic")

    # =========================================================
    # ProposerAgent (mascot box + label)
    # =========================================================
    pa_x, pa_y = 0.6, 4.4
    rbox(ax, pa_x, pa_y, 1.5, 1.0, "🤖\nProposerAgent\n(Qwen3-32B)",
         C_PROPOSER, tc="white", fw="bold", fs=9, rs=0.07)

    # Arrow → speech bubble label
    arrow(ax, pa_x + 1.5, pa_y + 0.5, pa_x + 1.95, pa_y + 0.5,
          lw=1.4)
    ax.text(pa_x + 1.7, pa_y + 0.85, "Instruction\nbatch",
            ha="center", va="bottom", fontsize=7.5, style="italic",
            color="#555")

    # =========================================================
    # Compound 2-stripe card stack — 3 cards
    # =========================================================
    stack_x = 2.4
    stack_y = 4.2
    stack_card_w = 1.3
    stack_card_h = 1.3
    stack_gap = 0.18
    # Centers we will use for arrows / pairing
    pair_anchors = []  # list of (text_y_anchor, image_y_anchor, x_right_edge)
    for i in range(3):
        x = stack_x + i * stack_gap
        y = stack_y + (2 - i) * 0.18 * 0.3  # subtle vertical offset

        # Outer card
        ax.add_patch(Rectangle((x, y), stack_card_w, stack_card_h,
                                fc="white", ec="#666", lw=0.8,
                                zorder=3 + i))
        # Top stripe (Ctx+Q)
        ax.add_patch(Rectangle((x + 0.06, y + stack_card_h/2 + 0.03),
                                stack_card_w - 0.12,
                                stack_card_h/2 - 0.08,
                                fc=C_TEXT_STRIPE, ec="#cc9",
                                lw=0.4, zorder=3 + i + 0.05))
        # Bottom stripe (image prompts)
        ax.add_patch(Rectangle((x + 0.06, y + 0.05),
                                stack_card_w - 0.12,
                                stack_card_h/2 - 0.08,
                                fc=C_IMG_STRIPE, ec="#caa",
                                lw=0.4, zorder=3 + i + 0.05))
        # On frontmost card, label
        if i == 2:
            ax.text(x + stack_card_w/2, y + stack_card_h * 0.78,
                    "Ctx + Q", ha="center", va="center",
                    fontsize=8.5, fontweight="bold",
                    color="#7a6020", zorder=12)
            ax.text(x + stack_card_w/2, y + stack_card_h * 0.25,
                    "image prompts", ha="center", va="center",
                    fontsize=8, fontweight="bold",
                    color="#7a4a20", zorder=12)

    # Compute frontmost card's right edge and the y for top/bottom stripes
    front_x = stack_x + 2 * stack_gap
    front_y = stack_y
    text_y_anchor = front_y + stack_card_h * 0.78
    image_y_anchor = front_y + stack_card_h * 0.25
    right_edge_x = front_x + stack_card_w

    # =========================================================
    # Decomposition splitter (dotted vertical line just after stack)
    # =========================================================
    split_x = right_edge_x + 0.25
    ax.plot([split_x, split_x],
            [stack_y - 0.1, stack_y + stack_card_h + 0.1],
            color="#999", lw=1.2, linestyle=(0, (2, 2)),
            zorder=4)
    ax.text(split_x, stack_y + stack_card_h + 0.2,
            "decompose", ha="center", va="bottom",
            fontsize=7.5, style="italic", color="#555")

    # =========================================================
    # TWO parallel tracks, each carrying 3 single-stripe sample cards
    # =========================================================
    track_card_w = 0.85
    track_card_h = 0.45
    n_samples = 3
    track_gap_x = 1.0

    # Top track (text) — y level
    top_track_y = stack_y + stack_card_h * 0.65
    # Bottom track (image prompts) — y level
    bot_track_y = stack_y + stack_card_h * 0.05

    # Track 1 text cards (right after splitter, before T2I region)
    text_track_xs = []
    for i in range(n_samples):
        tx = split_x + 0.4 + i * track_gap_x
        text_card(ax, tx, top_track_y, track_card_w, track_card_h)
        text_track_xs.append(tx + track_card_w/2)

    # Track 1: same 3 sample cards continue past T2I (they don't change)
    # We'll keep going on the same track until Target VLM
    # The text track is unchanged — let's keep 1 set of 3 cards before
    # Target VLM. Then a long arrow into Target VLM.
    # We need T2I in the middle of the bottom track but text track
    # passes ABOVE it.

    # Place T2I mascot below the text track (in line with image track)
    t2i_x = split_x + 0.5 + 1 * track_gap_x + 0.15
    t2i_y = bot_track_y - 0.25
    rbox(ax, t2i_x, t2i_y, 1.0, 0.95,
         "🎨\nT2I\n(SDXL)", C_T2I, tc="white", fw="bold", fs=8,
         rs=0.08)

    # Image-prompt cards: 3 BEFORE T2I, then 3 RENDERED-image cards AFTER T2I
    # Before T2I: place 3 peach image-prompt cards
    for i in range(n_samples):
        tx = split_x + 0.4 + i * 0.32
        image_prompt_card(ax, tx, bot_track_y, 0.28, track_card_h,
                           label=f"")
    # After T2I: place 3 mint rendered-image cards
    rendered_xs = []
    for i in range(n_samples):
        tx = t2i_x + 1.05 + i * 0.45
        rendered_image_card(ax, tx, bot_track_y - 0.1, 0.4, 0.65)
        rendered_xs.append(tx + 0.2)

    # Adjust: rendered image cards are bigger so they sit a bit lower
    # Don't draw arrow from T2I — just imply by position
    # Arrow into T2I from the image-prompt cards' rightmost edge
    arrow(ax, split_x + 0.4 + 3 * 0.32 + 0.05, bot_track_y + track_card_h/2,
          t2i_x, t2i_y + 0.475, lw=1.2)
    # Arrow out of T2I to rendered cards
    arrow(ax, t2i_x + 1.0, t2i_y + 0.475,
          t2i_x + 1.05, bot_track_y + 0.225, lw=1.2)

    # === Pairing dotted lines ===
    # Connect each text card to its corresponding image card
    # Sample 1: text_track_xs[0] ↔ rendered_xs[0]
    # We'll draw dotted vertical lines (not strictly vertical — slight
    # diagonal because positions differ). But for clarity, just connect
    # via near-vertical dotted line at the rightmost end (just before
    # Target VLM).
    # Use the LAST text card x and the LAST rendered card x — they should
    # be approximately aligned vertically near Target VLM.

    # Better: connect at the start of each track, near the splitter
    # First pair: text card 0 ↔ image card 0
    for i in range(n_samples):
        if i < len(text_track_xs) and i < len(rendered_xs):
            tx = text_track_xs[i] + 0.05
            bx = rendered_xs[i] - 0.05
            # Just dotted vertical line at the average x
            avg_x = (tx + bx) / 2 - 0.6
            ax.plot([avg_x, avg_x],
                    [bot_track_y + track_card_h, top_track_y],
                    color="#888", lw=0.8, linestyle=(0, (1.5, 1.5)),
                    zorder=4)

    # Label the pairing area
    ax.text(t2i_x - 1.2, top_track_y + track_card_h + 0.4,
            "(sample-aligned pairs)",
            ha="center", va="bottom",
            fontsize=7.5, style="italic", color="#888")

    # Track captions under the arrows
    ax.text(split_x + 0.5 + 1.5 * track_gap_x, top_track_y + track_card_h + 0.1,
            "text — passes through unchanged",
            ha="center", va="bottom",
            fontsize=7.5, style="italic", color="#7a6020")
    ax.text(t2i_x + 0.5, bot_track_y - 0.55,
            "image prompts → SDXL → rendered images",
            ha="center", va="top",
            fontsize=7.5, style="italic", color="#7a4a20")

    # =========================================================
    # Target VLM — receives BOTH tracks
    # =========================================================
    tvlm_x = t2i_x + 1.05 + 3 * 0.45 + 0.4
    tvlm_y = (top_track_y + bot_track_y) / 2 - 0.2
    rbox(ax, tvlm_x, tvlm_y, 1.6, 1.2,
         "🎯\nTarget VLM",
         C_TARGET, tc="white", fw="bold", fs=9, rs=0.08)

    # Arrows from last text card → Target VLM top edge
    last_text_x = split_x + 0.4 + (n_samples - 1) * track_gap_x + track_card_w
    arrow(ax, last_text_x, top_track_y + track_card_h/2,
          tvlm_x + 0.2, tvlm_y + 1.0, lw=1.5)
    # Arrows from last rendered image card → Target VLM bottom edge
    last_rendered_x = t2i_x + 1.05 + (n_samples - 1) * 0.45 + 0.4
    arrow(ax, last_rendered_x, bot_track_y + 0.2,
          tvlm_x + 0.2, tvlm_y + 0.2, lw=1.5)

    # =========================================================
    # Target VLM → Response → decode + classify → pos/neg pools → DPO
    # =========================================================
    arrow(ax, tvlm_x + 1.6, tvlm_y + 0.6,
          tvlm_x + 2.0, tvlm_y + 0.6, lw=1.4)
    # speech bubble for response
    ax.text(tvlm_x + 1.85, tvlm_y + 0.95,
            "Response y", ha="center", va="bottom",
            fontsize=7.5, style="italic", color="#446")

    # decode + classify rhombus
    rh_x = tvlm_x + 2.05
    rh_y = tvlm_y + 0.35
    rhombus = Polygon([
        (rh_x, rh_y + 0.45),
        (rh_x + 0.8, rh_y + 0.9),
        (rh_x + 1.6, rh_y + 0.45),
        (rh_x + 0.8, rh_y),
    ], closed=True, fc="white", ec="#666", lw=1.0, zorder=4)
    ax.add_patch(rhombus)
    ax.text(rh_x + 0.8, rh_y + 0.45,
            "decode\n+ classify", ha="center", va="center",
            fontsize=7.5, style="italic", color="#333", zorder=5)

    # Split → pos/neg pools on far right
    pool_x = rh_x + 1.85
    pool_box(ax, pool_x, tvlm_y + 0.95, 1.7, 0.9, kind="pos")
    pool_box(ax, pool_x, tvlm_y - 0.65, 1.7, 0.9, kind="neg")

    # Arrows from rhombus to pools
    arrow(ax, rh_x + 1.6, rh_y + 0.6,
          pool_x, tvlm_y + 1.4, lw=1.2)
    arrow(ax, rh_x + 1.6, rh_y + 0.3,
          pool_x, tvlm_y - 0.2, lw=1.2)

    # DPO update node
    dpo_x = pool_x + 1.85
    dpo_y = tvlm_y + 0.1
    rbox(ax, dpo_x, dpo_y, 1.0, 0.8, "🧠\nDPO\nupdate",
         C_DPO, tc="white", fw="bold", fs=9, rs=0.08)
    # Arrows from pools to DPO
    arrow(ax, pool_x + 1.7, tvlm_y + 1.4, dpo_x, dpo_y + 0.6, lw=1.2)
    arrow(ax, pool_x + 1.7, tvlm_y - 0.2, dpo_x, dpo_y + 0.2, lw=1.2)

    # Curved purple arrow back to ProposerAgent
    arrow(ax, dpo_x + 0.5, dpo_y, pa_x + 0.75, pa_y, lw=1.6,
          color=C_DPO, connection="arc3,rad=0.25", mutation=18)
    ax.text(fig_w / 2, 1.3, "↻ DPO update", ha="center", va="center",
            fontsize=10, fontweight="bold", style="italic", color=C_DPO)

    # Bottom italic caption
    ax.text(fig_w / 2, 0.55,
            "Iterative DPO from Target VLM failures",
            ha="center", va="center", fontsize=11, fontweight="bold",
            style="italic", color="#D86A4A")

    fig.savefig(OUT / "stageA_v7_sketch.png", facecolor="white")
    fig.savefig(OUT / "stageA_v7_sketch.pdf", facecolor="white")
    plt.close(fig)
    print("saved stageA_v7_sketch.{png,pdf}")


if __name__ == "__main__":
    draw()
