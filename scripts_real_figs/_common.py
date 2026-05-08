"""Shared helpers for paper real figure generation.

Loaded by each figure script. Centralises:
- Path roots (REPO, DATA, FIGS_OUT)
- Text loading + cleanup for predict_instruction style data
- Embedding model handle (lazy load)
- Style constants (colours, font sizes) matched to placeholder mockups
"""
import json
import os
import re
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

REPO = Path("/home/lianqi/ReverseGen")
DATA = Path("/home/lianqi/data")
PAPER = Path("/home/lianqi/papers/deepbias-tpami")
FIGS_OUT = PAPER / "images" / "real_figs"
FIGS_OUT.mkdir(parents=True, exist_ok=True)
EMBED_MODEL_PATH = "/home/lianqi/data/models/all_MiniLM_L6_v2"

# Colour palette mirroring the placeholder mockups.
# Pre-DPO / Iter1 / Iter2 / Seed for Proposer figs.
PROPOSER_COLORS = {
    "Seed (BBQ)":   "#9b9b9b",   # light grey
    "Pre-DPO":      "#7e6dad",   # muted purple
    "DPO Iter 1":   "#6dc5a4",   # mint green
    "DPO Iter 2":   "#e9a17b",   # warm orange
}
PROPOSER_ORDER = ["Seed (BBQ)", "Pre-DPO", "DPO Iter 1", "DPO Iter 2"]

# Age / Gender / Race for benchmark figs.
CATEGORY_COLORS = {
    "Age":    "#dd8452",   # orange
    "Gender": "#9d4f9e",   # purple
    "Race":   "#3aa874",   # green
}
CATEGORY_ORDER = ["Age", "Gender", "Race"]

# Target-model line colours for diversity figure.
TARGET_COLORS = {
    "InternVL3-8B":  "#2178b4",
    "Qwen2.5-VL-7B": "#ed7e34",
}


def _load_jsonl_or_json(path):
    path = Path(path)
    text = path.read_text()
    text_strip = text.lstrip()
    if text_strip.startswith("["):
        return json.loads(text)
    rows = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        rows.append(json.loads(ln))
    return rows


def _clean_predict_instruction(s, drop_image_prefix=True):
    """Trim 'Image1: ... Image2: ... Image3: ...' prefix and option block.

    Returns (context, question) pair plus a single combined string for embedding."""
    if not isinstance(s, str):
        return None
    s = s.strip()
    if drop_image_prefix:
        # Remove 'Image1: ...' to first 'Context:' if present
        m = re.search(r"Context:", s, flags=re.I)
        if m:
            s = s[m.start():]
    # Strip the A/B/C option block — keep context + question only
    # Use first occurrence of A. (Yes|...) marker
    s = re.split(r"\n\s*A[\.:\)]\s*", s, maxsplit=1)[0]
    s = s.strip()
    # Compact whitespace
    s = re.sub(r"\s+", " ", s)
    return s


def load_proposer_texts(target="intern3"):
    """Load Pre-DPO, DPO Iter 1, DPO Iter 2 predict_instruction strings for one target.

    `target` is one of 'intern3', 'qwen25', 'llava'. Returns dict of stage -> list[str]."""
    base = REPO / "responses" / "analyse_dpo"
    if target == "intern3":
        # iter_opt_1 dir uses 'intern' (without 3) for InternVL3-8B target.
        files = [
            ("Pre-DPO",     base / "initial_responses"  / "intern3.json"),
            ("DPO Iter 1",  base / "iter_opt_1_responses" / "intern.json"),
            ("DPO Iter 2",  base / "iter_opt_2_responses" / "intern3.json"),
        ]
    elif target == "qwen25":
        files = [
            ("Pre-DPO",     base / "initial_responses"  / "qwen25.json"),
            ("DPO Iter 1",  base / "iter_opt_1_responses" / "qwen25.json"),
            ("DPO Iter 2",  base / "iter_opt_2_responses" / "qwen25.json"),
        ]
    elif target == "llava":
        files = [
            ("Pre-DPO",     base / "initial_responses"  / "llava.json"),
            ("DPO Iter 1",  base / "iter_opt_1_responses" / "llava.json"),
            ("DPO Iter 2",  base / "iter_opt_2_responses" / "llava.json"),
        ]
    else:
        raise ValueError(target)

    out = {}
    for stage, path in files:
        rows = _load_jsonl_or_json(path)
        cleaned = []
        for r in rows:
            t = _clean_predict_instruction(r.get("predict_instruction", ""))
            if t and len(t) > 30:
                cleaned.append(t)
        out[stage] = cleaned
    return out


def load_seed_bbq_age():
    """VLBBQ Age seed — 235 questions, used as Seed series.

    Entries in VLBBQ Age.json are plain strings shaped as
        ``image: ...\\n context: ...\\n question: ...\\n options: A. Yes ...``
    we parse the context+question out of that.
    """
    seed_path = DATA / "dataset" / "VLBBQ_v3_3" / "data" / "list" / "base" / "Age.json"
    rows = _load_jsonl_or_json(seed_path)
    out = []
    for r in rows:
        if isinstance(r, dict):
            ctx = r.get("context", "")
            q = r.get("question", "")
            if ctx or q:
                t = f"Context: {ctx} Question: {q}".strip()
                out.append(re.sub(r"\s+", " ", t))
            continue
        if not isinstance(r, str):
            continue
        s = r
        ctx_m = re.search(r"context:\s*(.*?)(?:\n\s*question:|$)", s, flags=re.I | re.S)
        q_m = re.search(r"question:\s*(.*?)(?:\n\s*(?:options|A\.)|$)", s, flags=re.I | re.S)
        ctx = ctx_m.group(1).strip() if ctx_m else ""
        q = q_m.group(1).strip() if q_m else ""
        if ctx or q:
            t = f"Context: {ctx} Question: {q}".strip()
            out.append(re.sub(r"\s+", " ", t))
    return out


def load_final_survivors():
    """Load distilled benchmark texts per category."""
    base = REPO / "voting_eval" / "dedup"
    out = {}
    for cat, fn in [("Age", "age_final_survivors.json"),
                    ("Gender", "gender_final_survivors.json"),
                    ("Race", "race_final_survivors.json")]:
        rows = _load_jsonl_or_json(base / fn)
        out[cat] = rows
    return out


def survivor_question_text(r):
    """Extract clean context+question text from a survivor row."""
    ctx = r.get("context", "") or ""
    q = r.get("question", "") or ""
    if ctx or q:
        t = f"Context: {ctx} Question: {q}".strip()
    else:
        t = _clean_predict_instruction(r.get("predict_instruction", "")) or ""
    return re.sub(r"\s+", " ", t).strip()


def get_sentence_encoder():
    """Lazy-load all-MiniLM-L6-v2."""
    from sentence_transformers import SentenceTransformer
    enc = SentenceTransformer(EMBED_MODEL_PATH, device="cpu")
    return enc


# ============================================================
# Topic taxonomy — keyword regex per topic
# Mirrors the labels shown on the mockup radars.
# ============================================================
PROPOSER_TOPICS = [
    ("Job/Hiring",      r"\b(?:job|hire|hired|hiring|career|salary|promot|promot[ie]|recruit|interview|workplace|profession|work|colleague|coworker|employer|employee|boss|manager|client|workforce)\b"),
    ("Expert/Tech",     r"\b(?:tech|technology|technological|engineer|computer|software|coding|program|programmer|smartphone|app|digital|innovation|startup|AI\b|expert|expertise|specialist|laptop|gadget|cutting[\- ]edge)\b"),
    ("Public Speaking", r"\b(?:speech|speak|speaker|presentation|present|conference|panel|lecture|forum|address|audience|talk|microphone|podium|debate)\b"),
    ("Security",        r"\b(?:security|safe|safety|police|guard|threat|theft|criminal|crime|robber|suspect|surveillance|protect|harm|danger|risk)\b"),
    ("Legal",           r"\b(?:law|legal|court|lawyer|attorney|judge|trial|jury|lawsuit|contract|dispute|sue|defendant|plaintiff|illegal)\b"),
    ("Education",       r"\b(?:school|student|teacher|class|education|study|study|university|college|professor|tutor|graduate|academic|exam|degree|knowledge|learn|literacy|book|library)\b"),
    ("Social Role",     r"\b(?:family|parent|mother|father|child|son|daughter|spouse|wife|husband|household|community|volunteer|charity|neighbour|neighbor|friend|partner|home)\b"),
    ("Health",          r"\b(?:health|medic|medical|doctor|nurse|hospital|patient|illness|medicine|fit|fitness|exercise|gym|sport|physical|workout|stamina)\b"),
    ("Civic/Politics",  r"\b(?:politic|election|vote|voter|government|policy|civic|public|leader|leadership|mayor|council|representative|senator|protest|activism|community center)\b"),
    ("Finance",         r"\b(?:money|financ|invest|investor|loan|bank|debt|wealth|salary|fund|funding|budget|economic|tax|account|insurance|venture|capital|stock)\b"),
]

BENCHMARK_TOPICS = [
    ("Job/Hiring",      r"\b(?:job|hire|hired|hiring|career|salary|promot|recruit|interview|workplace|profession|work|colleague|coworker|employer|employee|boss|manager|workforce)\b"),
    ("Expert/Tech",     r"\b(?:tech|technology|engineer|computer|software|coding|program|programmer|smartphone|app|digital|innovation|startup|AI\b|expert|expertise|specialist|laptop|gadget|cutting[\- ]edge)\b"),
    ("Public Speaking", r"\b(?:speech|speak|speaker|presentation|present|conference|panel|lecture|forum|address|audience|talk|microphone|podium|debate)\b"),
    ("Security/Legal",  r"\b(?:security|safe|safety|police|guard|threat|theft|criminal|crime|robber|suspect|surveillance|harm|danger|law|legal|court|lawyer|attorney|judge|trial|jury|illegal)\b"),
    ("Education",       r"\b(?:school|student|teacher|class|education|study|university|college|professor|tutor|graduate|academic|exam|degree|library|literacy|learn)\b"),
    ("Social Role",     r"\b(?:family|parent|mother|father|child|son|daughter|spouse|wife|husband|household|community|volunteer|charity|neighbour|neighbor|friend|partner|home)\b"),
    ("Health",          r"\b(?:health|medic|medical|doctor|nurse|hospital|patient|illness|medicine|fit|fitness|exercise|gym|sport|physical|workout|stamina)\b"),
    ("Civic",           r"\b(?:politic|election|vote|voter|government|policy|civic|leader|leadership|mayor|council|representative|senator|protest|activism)\b"),
    ("Consumer",        r"\b(?:store|shop|shopping|store|customer|buy|purchase|grocery|mall|cashier|retail|restaurant|cafe|caf[eé]|coffee|menu|tip)\b"),
    ("Space/Venue",     r"\b(?:airport|station|train|subway|bus|terminal|hotel|lobby|park|street|sidewalk|elevator|hallway|venue|event|theatre|theater|stadium)\b"),
]


def topic_distribution(texts, taxonomy):
    """Return (n_topics,) percentages — fraction of texts containing topic regex.

    A text may match multiple topics; we count it for each match. Then we
    normalise by total number of (text, topic) hits so that the radar sums
    to <=1; this matches the mockup style which shows %ages summing to ~100.
    """
    if not texts:
        return np.zeros(len(taxonomy))
    counts = np.zeros(len(taxonomy))
    n_text = len(texts)
    for t in texts:
        if not t:
            continue
        for i, (_, rx) in enumerate(taxonomy):
            if re.search(rx, t, flags=re.I):
                counts[i] += 1
    return counts / n_text  # fraction of texts containing each topic


def setup_matplotlib():
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    mpl.rcParams["pdf.fonttype"] = 42
    mpl.rcParams["ps.fonttype"] = 42
    mpl.rcParams["font.family"] = "DejaVu Sans"
    mpl.rcParams["axes.unicode_minus"] = False
    mpl.rcParams["figure.dpi"] = 130
    mpl.rcParams["savefig.dpi"] = 200
    mpl.rcParams["savefig.bbox"] = "tight"
    mpl.rcParams["pdf.compression"] = 9
    return plt


def save_fig(fig, name, also_png=True):
    """Save figure as both PDF (paper-ready) and PNG (preview)."""
    pdf_path = FIGS_OUT / f"{name}.pdf"
    fig.savefig(pdf_path)
    if also_png:
        fig.savefig(FIGS_OUT / f"{name}.png", dpi=180)
    return pdf_path
