"""Sketch three layout options for Figure 2 (method overview).

These are *schematic* drawings — boxes + arrows + labels — to help the user
pick a structural layout. Not the final figure.

Option A: Vertical narrative (Stage A above, pool funnel in middle, Stage B below)
Option B: Horizontal pipeline with shared top Target
Option C: Three-panel NeurIPS style (Train | Probe | Skill Library)
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon
from matplotlib.lines import Line2D
import matplotlib as mpl
from pathlib import Path

mpl.rcParams["font.family"] = "DejaVu Sans"
mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["savefig.dpi"] = 160
mpl.rcParams["savefig.bbox"] = "tight"

OUT = Path("/home/lianqi/papers/deepbias-tpami/figure2_options")
OUT.mkdir(parents=True, exist_ok=True)

# Color palette — minimal,顶刊风格
C_PROPOSER = "#5B8DEF"   # blue
C_DEEPAGENT = "#E76F51"  # warm orange-red
C_TARGET = "#6C757D"     # neutral gray
C_POOL = "#B9D8C2"       # mint
C_SKILL_DEEP = "#7FB8A3"  # teal
C_SKILL_RW = "#F2B880"   # warm sand
C_BG = "#FAFAFA"
C_OUTLINE = "#222"


def rounded_box(ax, x, y, w, h, label, fc, ec=C_OUTLINE, lw=1.2, fontsize=10,
                fontweight="normal", text_color="black", pad=0.04):
    box = FancyBboxPatch((x, y), w, h,
                          boxstyle=f"round,pad={pad},rounding_size=0.08",
                          fc=fc, ec=ec, lw=lw, zorder=2)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, label, ha="center", va="center",
            fontsize=fontsize, fontweight=fontweight, color=text_color, zorder=3)


def arrow(ax, x1, y1, x2, y2, lw=1.4, color=C_OUTLINE, style="-|>", connection="arc3,rad=0",
          mutation=18):
    a = FancyArrowPatch((x1, y1), (x2, y2),
                         arrowstyle=style,
                         color=color, lw=lw,
                         connectionstyle=connection,
                         mutation_scale=mutation, zorder=4)
    ax.add_patch(a)


def funnel(ax, x_cx, y_top, y_bot, w_top, w_bot, fc=C_POOL, ec=C_OUTLINE, lw=1.2):
    poly = Polygon([
        (x_cx - w_top/2, y_top),
        (x_cx + w_top/2, y_top),
        (x_cx + w_bot/2, y_bot),
        (x_cx - w_bot/2, y_bot),
    ], closed=True, fc=fc, ec=ec, lw=lw, zorder=2)
    ax.add_patch(poly)


# =========================================================================
# Option A — Vertical narrative
# =========================================================================
def draw_option_a():
    fig, ax = plt.subplots(figsize=(9.5, 12), dpi=140)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 13)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # Title
    ax.text(5, 12.6, "Option A — Vertical narrative",
            ha="center", fontsize=16, fontweight="bold")
    ax.text(5, 12.2,
            "Stage A on top → pool funnel in middle → Stage B on bottom (skill library as right panel)",
            ha="center", fontsize=10, color="#555", style="italic")

    # ============ Stage A — top third ============
    ax.text(0.3, 11.5, "Stage A: train ProposerAgent (DPO loop)",
            ha="left", fontsize=12, fontweight="bold", color=C_PROPOSER)

    # ProposerAgent box (left)
    rounded_box(ax, 0.5, 9.4, 2.3, 1.4, "ProposerAgent\n(Qwen3-32B)", C_PROPOSER,
                text_color="white", fontweight="bold", fontsize=10)
    # Target VLM (right)
    rounded_box(ax, 6.8, 9.4, 2.3, 1.4, "Target VLM", C_TARGET,
                text_color="white", fontweight="bold", fontsize=10)
    # Generated test cases (middle)
    rounded_box(ax, 3.4, 10.0, 2.7, 0.8,
                "(I₁,I₂,I₃, Q + ABC options)", "#FFF8E7", fontsize=9)
    # DPO update (bottom)
    rounded_box(ax, 3.4, 9.0, 2.7, 0.6, "DPO preference update", "#EFE3FA",
                fontsize=9)

    # Arrows: ProposerAgent → test case → Target
    arrow(ax, 2.8, 10.4, 3.4, 10.4)
    arrow(ax, 6.1, 10.4, 6.8, 10.4)
    # Target → DPO update (responses bias signal)
    arrow(ax, 7.95, 9.4, 6.1, 9.3, connection="arc3,rad=0.15")
    # DPO → ProposerAgent (closes loop)
    arrow(ax, 3.4, 9.3, 1.65, 9.4, connection="arc3,rad=-0.15")

    # ============ Funnel — middle ============
    funnel(ax, 5, 8.6, 7.0, 7.0, 1.0)
    ax.text(5, 7.8, "candidate pool\n→ 5-anchor voting +\nSemDeDup", ha="center",
            fontsize=9, color="#333")
    ax.text(9.4, 7.8, "≈ 7K\ntest cases", fontsize=9, color="#555", ha="left")

    # ============ Stage B — bottom 2/3 (left main + right skill library) ============
    ax.text(0.3, 6.6, "Stage B: multi-turn probing with DeepAgent (skill-driven)",
            ha="left", fontsize=12, fontweight="bold", color=C_DEEPAGENT)

    # Three-turn dialogue trace — vertical
    turn_x = 0.8
    turn_w = 5.8
    turn_h = 1.5
    for i, (turn_label, y) in enumerate([("Turn 1", 4.6), ("Turn 2", 2.8), ("Turn 3", 1.0)]):
        # Turn header strip
        rounded_box(ax, turn_x, y + turn_h - 0.4, turn_w, 0.4,
                    f"{turn_label}", "#F5F5F5", fontsize=10, fontweight="bold")
        # Agent rewrite bubble
        rounded_box(ax, turn_x + 0.1, y + 0.7, 2.6, 0.5,
                    "DeepAgent\nrewrite Qᵢ", C_DEEPAGENT,
                    text_color="white", fontsize=8.5)
        # Skill picker indicator
        arrow(ax, turn_x + 1.4, y + 0.7, turn_x + 1.4, y + 0.2, color=C_DEEPAGENT,
              lw=1)
        rounded_box(ax, turn_x + 0.5, y - 0.1, 1.8, 0.3,
                    "↑ picks 1 of 7 skills",
                    "#FFE5DC", fontsize=8, text_color=C_DEEPAGENT)
        # Target response bubble
        rounded_box(ax, turn_x + 3.0, y + 0.7, 2.6, 0.5,
                    "Target VLM\nresponse", C_TARGET,
                    text_color="white", fontsize=8.5)
        # Arrow between agent and target
        arrow(ax, turn_x + 2.7, y + 0.95, turn_x + 3.0, y + 0.95, lw=1, mutation=12)
        # Arrow from one turn to next
        if i < 2:
            arrow(ax, turn_x + turn_w/2, y - 0.15, turn_x + turn_w/2, y - 0.55,
                  lw=1.2, color="#444")

    # Right panel — Skill Library
    sk_x, sk_y, sk_w, sk_h = 7.0, 0.7, 2.8, 5.8
    rounded_box(ax, sk_x, sk_y, sk_w, sk_h, "", "#FFFFFF", ec="#888", lw=1, pad=0.02)
    ax.text(sk_x + sk_w/2, sk_y + sk_h - 0.35, "Skill Library",
            ha="center", fontsize=11, fontweight="bold")
    ax.text(sk_x + sk_w/2, sk_y + sk_h - 0.7, "(7 skills, 2 families)",
            ha="center", fontsize=8, color="#555", style="italic")
    # Deepening family
    rounded_box(ax, sk_x + 0.15, sk_y + sk_h - 1.5, sk_w - 0.3, 0.4,
                "Deepening (3)", C_SKILL_DEEP, fontsize=9, fontweight="bold",
                text_color="white")
    deepening = ["attribute refinement", "scenario deepening", "comparison deepening"]
    for i, name in enumerate(deepening):
        ax.text(sk_x + 0.3, sk_y + sk_h - 1.95 - i*0.32, f"• {name}",
                fontsize=8.5, color="#333")
    # Rewriting family
    rw_y0 = sk_y + sk_h - 3.4
    rounded_box(ax, sk_x + 0.15, rw_y0, sk_w - 0.3, 0.4,
                "Rewriting (4)", C_SKILL_RW, fontsize=9, fontweight="bold",
                text_color="black")
    rewriting = ["contextualisation", "projective framing",
                 "behavioural tendency", "cognitive attribution"]
    for i, name in enumerate(rewriting):
        ax.text(sk_x + 0.3, rw_y0 - 0.45 - i*0.32, f"• {name}",
                fontsize=8.5, color="#333")

    # Dashed connection from one turn's "picks" to skill library
    arrow(ax, turn_x + 1.4 + 0.8, 4.6 + 0.05, sk_x + 0.1, sk_y + sk_h - 1.3,
          color="#888", lw=0.8, style="-|>",
          connection="arc3,rad=0.3", mutation=10)

    fig.savefig(OUT / "option_A_vertical.png", facecolor="white")
    fig.savefig(OUT / "option_A_vertical.pdf", facecolor="white")
    plt.close(fig)
    print("saved option_A_vertical.{png,pdf}")


# =========================================================================
# Option B — Horizontal pipeline with shared top Target
# =========================================================================
def draw_option_b():
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=140)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(8, 8.6, "Option B — Horizontal pipeline (shared top Target)",
            ha="center", fontsize=16, fontweight="bold")
    ax.text(8, 8.2,
            "Target VLM spans top → Stage A | Pool funnel | Stage B run below; skill library inset right",
            ha="center", fontsize=10, color="#555", style="italic")

    # Top strip — shared Target VLM
    rounded_box(ax, 1.0, 7.0, 14.0, 0.9, "Target VLM   (one model probed by both stages)",
                C_TARGET, text_color="white", fontweight="bold", fontsize=12)

    # Stage A box (bottom-left)
    rounded_box(ax, 0.5, 1.8, 5.0, 4.5, "", "#F3F8FE", ec=C_PROPOSER, lw=1.5)
    ax.text(3.0, 6.0, "Stage A: ProposerAgent + DPO",
            ha="center", fontsize=11, fontweight="bold", color=C_PROPOSER)
    # Internal proposer loop
    rounded_box(ax, 0.9, 4.4, 1.8, 0.9, "ProposerAgent\n(Qwen3-32B)", C_PROPOSER,
                text_color="white", fontsize=9, fontweight="bold")
    rounded_box(ax, 3.4, 4.4, 1.7, 0.9, "(I,Q)\ntest cases", "#FFF8E7", fontsize=9)
    rounded_box(ax, 1.6, 2.6, 3.0, 0.7, "DPO preference update",
                "#EFE3FA", fontsize=9)
    # Loop arrows
    arrow(ax, 2.7, 4.85, 3.4, 4.85)              # Proposer → test cases
    arrow(ax, 4.25, 4.4, 4.25, 3.3, connection="arc3,rad=0")  # test cases → Target above
    arrow(ax, 4.25, 6.95, 4.25, 5.3, color=C_OUTLINE,
          connection="arc3,rad=0")             # but for sketch we just point upward
    arrow(ax, 1.6, 2.95, 1.05, 4.4, connection="arc3,rad=-0.2")  # DPO → Proposer

    # Target up-arrow from Stage A
    arrow(ax, 3.0, 6.3, 3.0, 7.0, lw=2, color=C_PROPOSER, mutation=20)
    ax.text(3.3, 6.65, "test\ncases", fontsize=8, color=C_PROPOSER)
    arrow(ax, 4.0, 7.0, 4.0, 6.3, lw=2, color=C_PROPOSER, mutation=20)
    ax.text(4.25, 6.65, "responses\n(bias signal)", fontsize=8, color=C_PROPOSER)

    # Funnel — between A and B
    funnel(ax, 7.2, 5.6, 4.5, 1.6, 0.7)
    ax.text(7.2, 5.0, "candidate\npool", ha="center", fontsize=9)
    ax.text(7.2, 4.2, "≈ 7K", ha="center", fontsize=8, color="#555")

    # Stage B box (bottom-right)
    rounded_box(ax, 8.7, 1.8, 6.8, 4.5, "", "#FDF4F0", ec=C_DEEPAGENT, lw=1.5)
    ax.text(12.1, 6.0, "Stage B: DeepAgent multi-turn probing",
            ha="center", fontsize=11, fontweight="bold", color=C_DEEPAGENT)

    # 3-turn dialogue trace inside Stage B (compact horizontal)
    for i, (turn_label, x0) in enumerate([("T1", 8.95), ("T2", 10.65), ("T3", 12.35)]):
        rounded_box(ax, x0, 3.0, 1.5, 2.5, f"{turn_label}\nAgent ⇄ Target", "#FFFFFF",
                    fontsize=9, ec="#666")
        # Skill picked indicator
        rounded_box(ax, x0 + 0.1, 2.4, 1.3, 0.4, "↑ skill", "#FFE5DC",
                    text_color=C_DEEPAGENT, fontsize=8)
        if i < 2:
            arrow(ax, x0 + 1.5, 4.25, x0 + 1.7, 4.25, lw=1.4)

    # Skill library inset on right
    sk_x, sk_y, sk_w, sk_h = 14.05, 2.0, 1.35, 4.0
    rounded_box(ax, sk_x, sk_y, sk_w, sk_h, "", "#FFFFFF", ec="#888", lw=1)
    ax.text(sk_x + sk_w/2, sk_y + sk_h - 0.3, "Skill\nLibrary", ha="center",
            fontsize=9, fontweight="bold")
    rounded_box(ax, sk_x + 0.1, sk_y + sk_h - 1.3, sk_w - 0.2, 0.35,
                "Deepen ×3", C_SKILL_DEEP, fontsize=8, fontweight="bold",
                text_color="white")
    rounded_box(ax, sk_x + 0.1, sk_y + sk_h - 2.6, sk_w - 0.2, 0.35,
                "Rewrite ×4", C_SKILL_RW, fontsize=8, fontweight="bold")
    ax.text(sk_x + sk_w/2, sk_y + sk_h - 1.6, "attr-ref\nscen-deep\ncmp-deep",
            ha="center", fontsize=7, color="#333")
    ax.text(sk_x + sk_w/2, sk_y + sk_h - 3.0, "ctx\nproj\nbehav\ncog",
            ha="center", fontsize=7, color="#333")

    # Arrows: stage B 3 turns ↔ shared target on top
    arrow(ax, 11.5, 5.5, 11.5, 7.0, lw=2, color=C_DEEPAGENT, mutation=20)
    arrow(ax, 12.5, 7.0, 12.5, 5.5, lw=2, color=C_DEEPAGENT, mutation=20)
    ax.text(11.0, 6.4, "Q,Iᵢ", fontsize=8, color=C_DEEPAGENT)
    ax.text(12.55, 6.4, "answer", fontsize=8, color=C_DEEPAGENT)

    # Funnel → Stage B arrow
    arrow(ax, 7.9, 4.7, 8.95, 4.7, lw=2)
    # Stage A → Funnel
    arrow(ax, 5.5, 4.7, 6.5, 4.7, lw=2)

    fig.savefig(OUT / "option_B_horizontal.png", facecolor="white")
    fig.savefig(OUT / "option_B_horizontal.pdf", facecolor="white")
    plt.close(fig)
    print("saved option_B_horizontal.{png,pdf}")


# =========================================================================
# Option C — Three-panel (Train | Probe | Skill Library)
# =========================================================================
def draw_option_c():
    fig, ax = plt.subplots(figsize=(15, 7.5), dpi=140)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(8, 7.7, "Option C — Three-panel (NeurIPS style)",
            ha="center", fontsize=16, fontweight="bold")
    ax.text(8, 7.3,
            "Train | Probe | Skill Library — three equal columns; top header carries the Stage A → Stage B arrow",
            ha="center", fontsize=10, color="#555", style="italic")

    # Top header bar showing Stage A → Stage B
    header_y = 6.4
    rounded_box(ax, 0.5, header_y, 4.7, 0.55, "Stage A: train ProposerAgent",
                C_PROPOSER, text_color="white", fontweight="bold", fontsize=11)
    arrow(ax, 5.4, header_y + 0.27, 5.9, header_y + 0.27, lw=2)
    rounded_box(ax, 5.9, header_y, 4.6, 0.55, "Stage B: probe with DeepAgent",
                C_DEEPAGENT, text_color="white", fontweight="bold", fontsize=11)
    # Right column header
    rounded_box(ax, 10.7, header_y, 4.8, 0.55, "Skill Library (used by Stage B)",
                "#FFFFFF", ec="#888", fontsize=11, fontweight="bold")

    # ---------- Column 1: Train ----------
    rounded_box(ax, 0.5, 0.6, 4.7, 5.5, "", "#F3F8FE", ec=C_PROPOSER, lw=1.5)
    ax.text(2.85, 5.6, "ProposerAgent + DPO loop", ha="center",
            fontsize=11, fontweight="bold", color=C_PROPOSER)
    # Proposer box
    rounded_box(ax, 0.95, 4.4, 1.7, 0.8, "ProposerAgent", C_PROPOSER,
                text_color="white", fontsize=9, fontweight="bold")
    # Target
    rounded_box(ax, 3.05, 4.4, 1.7, 0.8, "Target VLM", C_TARGET,
                text_color="white", fontsize=9, fontweight="bold")
    # Test case box in the middle low
    rounded_box(ax, 1.4, 3.0, 2.9, 0.65, "(I₁,I₂,I₃, Q)", "#FFF8E7", fontsize=9)
    # DPO update box
    rounded_box(ax, 1.4, 1.6, 2.9, 0.65, "DPO preference update",
                "#EFE3FA", fontsize=9)
    # arrows
    arrow(ax, 2.65, 4.8, 3.05, 4.8)
    arrow(ax, 2.85, 4.4, 2.85, 3.65)
    arrow(ax, 3.9, 4.4, 4.0, 3.65, connection="arc3,rad=-0.2")
    arrow(ax, 2.85, 3.0, 2.85, 2.25)
    arrow(ax, 1.4, 1.95, 0.65, 4.4, connection="arc3,rad=-0.3")
    # Output to pool
    rounded_box(ax, 0.8, 0.85, 4.1, 0.55, "↓ candidate pool",
                C_POOL, fontsize=9, fontweight="bold")

    # ---------- Column 2: Probe ----------
    rounded_box(ax, 5.4, 0.6, 5.0, 5.5, "", "#FDF4F0", ec=C_DEEPAGENT, lw=1.5)
    ax.text(7.9, 5.6, "DeepAgent multi-turn trace", ha="center",
            fontsize=11, fontweight="bold", color=C_DEEPAGENT)

    # 3 turns stacked vertically
    for i, (lbl, y) in enumerate([("Turn 1", 4.45), ("Turn 2", 3.0), ("Turn 3", 1.55)]):
        rounded_box(ax, 5.6, y, 4.6, 1.0, "", "#FFFFFF", ec="#888", lw=0.8)
        ax.text(5.75, y + 0.78, lbl, fontsize=9, fontweight="bold")
        # left mini-box: DeepAgent
        rounded_box(ax, 5.75, y + 0.15, 1.9, 0.55, "DeepAgent\nrewrite",
                    C_DEEPAGENT, text_color="white", fontsize=8)
        # right mini-box: Target
        rounded_box(ax, 8.05, y + 0.15, 2.0, 0.55, "Target\nresponse",
                    C_TARGET, text_color="white", fontsize=8)
        arrow(ax, 7.65, y + 0.42, 8.05, y + 0.42, lw=1, mutation=12)
        # Skill picked label
        ax.text(6.7, y + 0.78, "  ← picks skill", fontsize=7.5, color=C_DEEPAGENT,
                style="italic")
        if i < 2:
            arrow(ax, 7.9, y - 0.05, 7.9, y - 0.45)

    # ---------- Column 3: Skill Library ----------
    rounded_box(ax, 10.7, 0.6, 4.8, 5.5, "", "#FFFFFF", ec="#888", lw=1)
    # Deepening family header
    rounded_box(ax, 10.95, 4.9, 4.3, 0.55, "Deepening family (3 skills)",
                C_SKILL_DEEP, text_color="white", fontweight="bold", fontsize=10)
    deepening = [
        ("Attribute refinement",
         "Narrow the demographic angle (age band, occupation, region…)"),
        ("Scenario deepening",
         "Embed the question into a richer, charged context"),
        ("Comparison deepening",
         "Force a head-to-head judgement across groups"),
    ]
    for i, (n, d) in enumerate(deepening):
        y0 = 4.55 - i * 0.55
        ax.text(11.0, y0, f"● {n}", fontsize=9, fontweight="bold", color="#1f5240")
        ax.text(11.25, y0 - 0.22, d, fontsize=7.5, color="#444",
                style="italic")

    # Rewriting family header
    rounded_box(ax, 10.95, 2.55, 4.3, 0.55, "Rewriting family (4 skills)",
                C_SKILL_RW, fontweight="bold", fontsize=10)
    rewriting = [
        ("Contextualisation",
         "Wrap as a story / hypothetical situation"),
        ("Projective framing",
         "Ask what a third party would think / do"),
        ("Behavioural tendency",
         "Probe likely actions instead of judgements"),
        ("Cognitive attribution",
         "Probe inferred reasons / character traits"),
    ]
    for i, (n, d) in enumerate(rewriting):
        y0 = 2.2 - i * 0.45
        ax.text(11.0, y0, f"● {n}", fontsize=9, fontweight="bold", color="#7a4d10")
        ax.text(11.25, y0 - 0.2, d, fontsize=7.5, color="#444",
                style="italic")

    # Big curving dashed arrow from probe column to skill library, signalling "uses"
    arrow(ax, 10.4, 3.0, 10.7, 3.0, lw=1.2, color="#888",
          style="-|>", connection="arc3,rad=0", mutation=14)

    # Pool flow arrow from column 1 (pool box) to column 2 (probe top)
    arrow(ax, 4.9, 1.1, 5.4, 1.1, lw=2, color="#444")

    fig.savefig(OUT / "option_C_three_panel.png", facecolor="white")
    fig.savefig(OUT / "option_C_three_panel.pdf", facecolor="white")
    plt.close(fig)
    print("saved option_C_three_panel.{png,pdf}")


if __name__ == "__main__":
    draw_option_a()
    draw_option_b()
    draw_option_c()
    print("\nAll three layout sketches written to:")
    print(f"  {OUT}/")
