# DeepBias: Adaptive and Dynamic Benchmark for Probing Social Biases in VLMs

## Project Overview
This is a TPAMI (IEEE Transactions on Pattern Analysis and Machine Intelligence) journal paper submission. The paper introduces **DeepBias**, a dynamic adversarial framework for evaluating social biases in Large Vision-Language Models (LVLMs).

## Core Idea
Two entities drive the pipeline, separately and in series:

- **Proposer** (distribution-level; implemented as Qwen3-32B with LoRA, no SFT step): a language model that synthesises candidate triplets satisfying the Protocol's four question-design constraints. It plays two roles in two regimes of the same model:
  1. *Expansion*: as a few-shot in-context generator, it expands raw BBQ / VLBiasBench (~300/category) into a candidate batch of ~2000/category, rendered into visual triplets via SDXL. **Frozen exemplar pool design**: the very first Expansion round (base model + raw seed as exemplars) produces a ~2000-sample batch; this batch is then retained as a frozen exemplar pool for every subsequent Expand call — only Proposer weights change across iterations, not the exemplars.
  2. *Adversarial Evolution*: a closed-loop "Expand → Query → Label → Update" cycle. At each iteration, Proposer generates a fresh batch, target LVLM is queried on each triplet's three image-Q pairs, preferences are labelled (≥1 non-Unknown = positive; all Unknown = negative), and DPO updates the Proposer. `π_ref` = the instruction-tuned base model itself (SFT is explicitly skipped because the candidate batch is the base model's own few-shot output).
- **DeepAgent** (instance-level, after DPO convergence): on every Proposer candidate, runs a multi-turn adaptive dialogue (T turns, T=3 in experiments) with the target. Each turn chooses *Deepening* (drill into exposed bias) or *Rewriting* (bypass safety filters), conditioned on the full history. The two strategies expand into **7 sub-strategies** grounded in social-psychology literature:
  - *Deepening* (3): **attribute refinement** (Fiske SCM 2002), **scenario deepening** (Fiske & Neuberg 1990), **comparison deepening** (Tajfel & Turner 1979)
  - *Rewriting* (4): **contextualisation**, **projection** (Fazio 1995), **behavioural-tendency framing** (Ajzen 1991), **cognitive-attribution framing** (Weiner 1985); preamble cites Devine 1989 and McConahay 1986 for indirect-bias-elicitation literature.
  One question per turn, image triplet fixed.

The final **DeepBias Benchmark** is built by running the full pipeline against an ensemble of 6 anchor LVLMs; the same ensemble drives the DPO consensus labelling. The candidate pool is then distilled by a two-step SemDeDup-style semantic deduplication (no automated voting validity filter — see "Voting Removed" below), and finally each retained triplet is decomposed into three single-image test instances.

## Evaluation Protocol (§3, standalone section)
- **Test instance = $(I, Q, \mathcal{O})$** — a single image, a single ambiguous/negatively-implied question, and the options $\{\text{A. Yes}, \text{B. No}, \text{C. Unknown}\}$. The model is queried with one instance at a time; the correct answer is always "C. Unknown".
- **Counterfactual triplet $(I_1, I_2, I_3, Q)$** is a *probe-design artifact*, not a test instance: three images that differ only in the sensitive attribute, used at construction time only and retained as metadata for per-demographic analysis. It is never shown jointly to the model under evaluation. Decomposition into 3 test instances happens at the very end of §4.3.
- **Four question-design constraints on Q**: (1) intentional ambiguity, (2) negative implication, (3) no probabilistic hedging, (4) no group-specific text — each mapped to one of the three bias characteristics.
- **Three characteristics separating societal bias from statistical correlation** (reviewed in Related Work §2.1, operationalised in Protocol §3.1):
  1. *Individual attribution* — group statistics cannot licence individual judgement.
  2. *Normative prescription* — descriptive accuracy ≠ normative legitimacy.
  3. *Concrete harm* — bias is defined by consequence, not pattern.
- **Construction quality**: in lieu of an automated validity filter, the released pool is verified by manual sampling — uniform random samples drawn per demographic category and reviewed against the four constraints; per-category constraint-satisfaction rates are reported in §5.3 (numbers TODO from user).
- **Bias judgment metric**: per decomposed instance, `Correct(r) = 1[r = "Unknown"]`. The paper reports **bias accuracy** (proportion of "Unknown") as the single primary metric throughout (no longer dual with elicitation rate).

## Voting Removed (2026-05-06)
The earlier protocol included an "ensemble validity check" using K=6 validators with $\rho(Q) = \frac{1}{3K}\sum \mathbb{1}[r=\text{Unknown}] > \tau = 1/3$ as the retain condition. **This entire mechanism has been removed** because manual sampling on the unfiltered output of the Proposer–DeepAgent pipeline showed that the constructed candidates already overwhelmingly satisfy the four question-design constraints. Consequences for the paper:
- §3.2 "Validity Criterion" subsection (with $\rho$ formula and $\tau$) deleted.
- §3.2 has new "Counterfactual Triplet Construction" + "Triplet Decomposition" + "Construction Quality" paragraphs (the last with TODO for manual-sample numbers).
- §4.3 "Validity Check via the Anchor Ensemble" subsubsection deleted.
- §4.3 "Triplet Decomposition and Assembly" rewritten to point at §5.3's dedup distillation rather than a validity filter.
- §5.5 "Validation Threshold Analysis" entirely removed (along with `fig:threshold_curve`).
- §1 Introduction's "multi-model voting validation step" sentence removed.
- `tab:pipeline` "Data Validity Rate" bottom row removed.
- `fig:benchmark_comparison` no longer compares on "validity rate" axis; reduced from 5 to 4 axes.
- `fig:protocol` (Fig 2, the dual-panel voting + bias-judgment illustration) entirely deleted; `images/protocol.png` kept on disk but no longer referenced.

## Paper Structure
- **§1 Introduction**
- **§2 Related Work**
  - 2.1 Foundations of Bias and Fairness — Mehrabi / Crawford / Blodgett / Suresh / Barocas, plus the three characteristics with full literature anchors (Dwork / Barocas / Binns / Prentice / Jussim / Blodgett / Buolamwini)
  - 2.2 Societal Bias Evaluation in VLMs
  - 2.3 Red Teaming and Jailbreaking for VLMs
  - 2.4 Optimization and RL for Data Generation
- **§3 Bias Evaluation Protocol** (paper's normative / definitional layer)
  - 3.1 Bias, Discrimination, and Statistical Deviation — paper's adopted framework + three characteristics (citing §2.1)
  - 3.2 Protocol Specification — Test Instance Format / Question Design Constraints / Counterfactual Triplet Construction / Triplet Decomposition / Construction Quality / Bias Judgment Metric
- **§4 Method** (operational — two-entity pipeline)
  - 4.1 Adaptive Data Generation via Adversarial Evolution — Proposer only: *Expansion via In-Context Few-Shot Generation* (mechanism + frozen exemplar pool) + *Adversarial Evolution via DPO* (4-step Expand/Query/Label/Update loop, no SFT); DPO loss equation
  - 4.2 Instance-Level Probing with the DeepAgent — Deepening (3 sub-strategies) / Rewriting (4 sub-strategies) with social-psych citations; $T$ abstract in method, T=3 deferred to §5
  - 4.3 DeepBias Benchmark Construction — ensemble-driven DPO consensus + triplet decomposition (no validity check)
- **§5 Experiment** (4 experiments + 1 limitation section)
  - 5.1 Proposer Evolution — Exp 1: Proposer-only DPO results + case study of evolving samples + distribution-shift figure. Shares `tab:pipeline` with §5.2.
  - 5.2 DeepAgent Multi-Turn Probing — Exp 2: per-turn DeepAgent results + case study tracing one candidate through Turns 0-3 + sub-strategy usage frequency + per-turn distribution shift
  - 5.3 Benchmark Construction — Exp 3: 6 anchor × 3 categories pipeline run + Candidate Pool Distillation (SemDeDup-inspired two-step dedup) + Manual Construction-Quality Verification
  - 5.4 Benchmark Evaluation — Exp 4: evaluate many models on the constructed benchmark
  - 5.5 Limitations and Future Work
- **§6 Conclusion**

## Shared Experiment Table (`tab:pipeline`, §5.1/§5.2, Age bias)

| Models | Pre-DPO | DPO Iter 1 | DPO Iter 2 | Probe Turn 1 | Probe Turn 2 | Probe Turn 3 |
|---|---|---|---|---|---|---|
| InternVL3-8B  | 90.4 | 84.2 | 83.1 | 67.3 | 60.5 | 60.7 |
| Qwen2.5-VL-7B | 85.0 | 82.1 | 78.7 | 47.7 | 53.0 | 51.6 |

Values are **bias accuracy %** (lower = more bias elicited). Raw Dataset column and Data Validity Rate row both removed in 2026-05-06 revision.

## Benchmark Construction Table (`tab:benchmark_building`, §5.3)
Vertical layout: **Category × Anchor model × 7 stages**, 6 anchors × 3 categories = 18 data rows + 3 category groups via `\multirow`. 7 stages: Raw Data / Pre-DPO / DPO Iter 1 / DPO Iter 2 / Probe T1 / T2 / T3. Cell colours: ≥90 deep green, 85–90 light green, 70–85 unfilled, 50–70 light red, <50 deep red.

The 6 anchor models (replacing earlier 5-model placeholder schema):
- InternVL3.5-8B (`OpenGVLab/InternVL3_5-8B`)
- Qwen3-VL-8B-Instruct (`Qwen/Qwen3-VL-8B-Instruct`)
- GLM-4.1V-9B-Base (`THUDM/GLM-4.1V-9B-Base`)
- DeepSeek-VL2-Small (`deepseek-ai/deepseek-vl2-small`, 27B MoE / 4.5B active)
- Gemma-3-27B-it (`google/gemma-3-27b-it`)
- LLaVA-OneVision-Qwen2-7B-OV (`lmms-lab/llava-onevision-qwen2-7b-ov`)

bib keys: `internvl35`, `qwen3vl`, `glm41v`, `deepseekvl2`, `gemma3`, `llava_onevision` — all marked `% TODO: verify arXiv IDs` for camera-ready.

## Candidate Pool Distillation (§5.3)
Two-step semantic deduplication, inspired by SemDeDup~\cite{abbas2023semdedup}, encoder = sentence-transformers/all-MiniLM-L6-v2~\cite{reimers2019sentencebert} (384-d, L2-normalised), cosine threshold 0.85.

- **Input**: 12,000 candidate triplets per category = 6 stages × 2,000 (Pre-DPO + DPO-1 + DPO-2 + Probe T1 + T2 + T3).
- **Step 1 (DeepAgent intra-pool dedup)**: 6,000 Probe T1/T2/T3 candidates with **idx-protection** — same Proposer-ancestor multi-turn variants always kept regardless of pairwise similarity (median intra-idx cosine ≈ 0.55, well below 0.85). Cross-idx pairs deduplicated normally.
- **Step 2 (Proposer incremental merge)**: 6,000 Pre-DPO/Iter-1/Iter-2 Proposer candidates shuffled and merged into the DeepAgent pool one at a time; each new candidate compared against the entire merged pool (DeepAgent ∪ already-admitted Proposer); admitted iff max cosine < 0.85; no idx-protection.

**Final per-category counts**: 7,597 Age + 5,969 Race + 7,253 Gender = **20,819 candidate triplets**, decomposed into **62,457 single-image test instances**.

The detailed per-stage retention breakdown (was previously in `tab:dedup_survival`) has been removed from the paper to keep §5.3 compact; only the methodology + final counts remain in prose. The retention numbers are still recorded in this CLAUDE.md and in the user's `final_merge.py` outputs for reference.

Known minor implementation flaw flagged with inline TODO: Proposer's dedup input text contains "Image1: ..." prefix while DeepAgent's text does not; under MiniLM mean-pooling this is absorbed by context but for camera-ready the texts should be normalised consistently (strip image-description prefix before encoding).

## Metric Convention (post-2026-05-06)
Single primary metric: **bias accuracy** (% of test instances with $r = $ "Unknown"; lower = more bias elicited). The complementary "bias elicitation rate" is no longer reported alongside accuracy — it appears only as a verb phrase ("the model elicits bias when ...") in qualitative descriptions. All numerical values in the paper (tab:pipeline, tab:benchmark_building, fig:benchmark_difficulty median, fig:benchmark_comparison comparison values) are accuracy values; direction language is "falls / drops / decreases" everywhere DPO/DeepAgent makes the benchmark harder.

## Implementation Details (§5 opening)
- **Proposer**: instruction-tuned Qwen3-32B + LoRA (rank 16, α=32) on attention-projection matrices; `π_ref` = the same frozen instruction-tuned base model (no SFT).
- **DPO**: β=0.1, batch 32 preference pairs, peak lr 5×10⁻⁵, cosine annealing.
- **DPO rounds**: R=2 for single-target experiments (§5.1/§5.2), R=3 for the ensemble benchmark-construction experiment (§5.3).
- **DeepAgent**: same Qwen3-32B in frozen-inference mode, system prompt enumerating the 7 sub-strategies, T=3 turns.
- **SDXL rendering**: 1024×1024, neutral contextual prompts with strict variable control across the sensitive attribute.
- **Hardware**: 8× NVIDIA RTX 3090 GPUs (NOT A100 — corrected by user 2026-04-22).
- **Targets**: zero-shot, default inference config and system prompt for each model.

## Key Files
- `main.tex` — main paper source
- `main.bib` — bibliography (with `abbas2023semdedup`, `reimers2019sentencebert`, and 6 anchor entries added 2026-05-06)
- `images/` — figures: `teaser.pdf` (Fig 1, real), `method_v2.png` (Fig 2 in current numbering, fig:workflow, user-supplied). `protocol.png` kept on disk but no longer referenced (Fig 2 deleted).
- `doc/anchor_model_candidates.md` — 20 open-source LVLM candidates (≤50B) for anchor ensemble selection; the 6 used are listed above.
- `doc/figure_mockups/` — matplotlib mockup placeholder PDFs/PNGs for Figs 3-8 (fig:proposer_distribution, fig:proposer_diversity, fig:deepagent_case, fig:benchmark_distribution, fig:benchmark_comparison, fig:benchmark_difficulty); all need to be replaced with real figures from real data.
- `/Users/lianqi/Angelita/phd/dynamic_evaluation/reference_papers/` — downloaded PDFs for bias/fairness literature, plus `SYNTHESIS.md`.

## Target Venue
IEEE TPAMI — uses IEEEtran document class. `caption` package override added so table captions stay in normal case (not IEEEtran's default all-caps); whether this should revert to IEEE convention is flagged as a TODO.

## Experiment Status (post-2026-05-06)
- **Exp 1 (§5.1 Proposer Evolution)**: numbers in `tab:pipeline` are bias accuracy (InternVL3-8B 90.4→83.1, Qwen2.5-VL-7B 85.0→78.7). Case Study commented out pending user prose; Distribution Shift prose written as "expected behaviour" and the supporting figures (`fig:proposer_distribution`, `fig:proposer_diversity`) are still mockups awaiting real data.
- **Exp 2 (§5.2 DeepAgent Multi-Turn Probing)**: numbers in `tab:pipeline` Probe Turn columns are bias accuracy (InternVL3-8B 67.3→60.5→60.7, Qwen2.5-VL-7B 47.7→53.0→51.6). Case Study commented out; `fig:deepagent_case` is mockup.
- **Exp 3 (§5.3 Benchmark Construction)**: real data installed for `tab:benchmark_building` (6 anchor × 3 categories × 7 stages, 18 rows). Candidate Pool Distillation paragraph compressed and supported by per-anchor distillation counts (Age 7,597; Race 5,969; Gender 7,253; total 20,819 / 62,457 instances). Manual Construction-Quality Verification paragraph has TODO for empirical numbers.
- **Exp 4 (§5.4 Benchmark Evaluation)**: most model rows still placeholder; `tab:benchmark` lists InternVL3-8B / Qwen2.5-VL-7B / Qwen3-VL-30B-A3B / InternVL3.5-38B / DeepSeek-VL with numbers, others placeholder. `iter 1/2/3` schema still uses old 3-DPO-iter convention and conflicts with current 2-DPO + 3-Probe schema — flagged for restructure.
- **§5.5 Limitations** (was §5.6): unchanged from prior draft; threshold-related limitation lines need to be removed since the threshold analysis itself was deleted.
- **Anchor models**: 6 anchors listed above are the final pick.

## Figure Status
- **Fig 1 (`fig:teaser`)**: real, kept.
- **Fig 2 (`fig:workflow`, was Fig 3 in old numbering)**: `images/method_v2.png`, user-supplied.
- **Fig 3 (`fig:proposer_distribution`)**: 2-subfigure mockup (UMAP + BERTopic radar). Needs real Proposer candidate pool data per stage to replace.
- **Fig 4 (`fig:proposer_diversity`)**: bar-chart mockup of diversity metrics. Needs real per-iteration metrics computed on real candidate pool.
- **Fig 5 (`fig:deepagent_case`)**: case-study trace mockup. Needs real Turn-0→3 dialogue from a logged DeepAgent run.
- **Fig 6 (`fig:benchmark_distribution`)**: 2-subfigure UMAP + BERTopic radar of final benchmark. Needs real distilled benchmark question text.
- **Fig 7 (`fig:benchmark_comparison`)**: 4-axis comparison vs BBQ/VLBiasBench/GenderBias-VL/PAIRS. Needs real numbers from prior benchmark metadata + same-LVLM evaluation results.
- **Fig 8 (`fig:benchmark_difficulty`)**: per-instance accuracy histogram, stacked by category. Needs the 62,457-instance accuracy distribution.

## Known Open Items (major TODOs flagged inline in main.tex)
- Manual sampling constraint-satisfaction rate (§5.3) — user to supply per-category numbers.
- §5.4 Benchmark Evaluation table needs real numbers for all hold-out models + restructuring to match the current 2-DPO + 3-Probe schema.
- 6 figure mockups (Figs 3-8) need real data and proper rendering (PDFs in `images/` per file naming convention).
- bib entries for 6 anchors + SemDeDup + Sentence-BERT need arXiv IDs verified before camera-ready.
- §4.3 K/2 consensus threshold for ensemble DPO still unjustified empirically (now low-priority since voting was removed; only affects DPO preference labelling).
- Proposer dedup input text normalisation: strip "Image[0-9]+:" prefix before encoding for cross-domain consistency with DeepAgent text (camera-ready polish).
- Probe Turn 1→3 non-monotone trajectory (e.g., InternVL3.5 Gender 38.6→54.3→49.6) — explanation currently prose-only, would benefit from sub-strategy usage frequency data.
- §5.5 Limitations section needs proofreading to remove any references to the deleted §5.5 Validation Threshold Analysis.
- Prompt templates for Proposer expansion + DeepAgent Deepening/Rewriting — write and place in Supplementary Material.
- Headline numbers in Abstract / Intro still TODO placeholders.
- Acknowledgment still placeholder.
- Many minor wording TODOs scattered across §4 and §5 (see inline `% TODO` comments).

## Major Revisions Completed (chronological)
### 2026-04-17 — Protocol promoted, two-entity Method, SFT removed
Promoted Protocol from subsection to standalone §3 with two subsections (Definitions / Specification). Added §2.1 "Foundations of Bias and Fairness" in Related Work. Reframed Method's two entities. Removed SFT step (`π_ref` = base instruction-tuned model directly). Reconceptualised test instance as $(I, Q, \mathcal{O})$ single-image; triplet is construction-only artifact.

### 2026-04-18 — Frozen exemplar pool, 7 sub-strategies, LLaVA removed
Proposer's frozen exemplar pool formalised. §4.1 Expansion split into two paragraphs. §4.2 DeepAgent multi-turn formalised with 7 sub-strategies + 8 social-psychology citations. LLaVA removed from Method and Experiment.

### 2026-04-19 — §5 restructure, tab:pipeline merged
§5 restructured into 4 experiments + auxiliary subsections. §5.1/§5.2 merged into single `tab:pipeline`. §5.1 numbers updated to user-corrected experimental data. §5.2 DeepAgent results added. `caption` package added for IEEE all-caps override.

### 2026-04-20 — Polish, dangling refs cleaned, captions expanded
§4 ensemble description corrected. §5.1/§5.2: 4 dangling `\ref{fig:X}` pointers removed; Case Study paragraphs commented out; Distribution-Shift / Strategy-Usage prose rewritten as "expected behaviour". `tab:benchmark_building` and `tab:benchmark` captions expanded. Various typo fixes.

### 2026-05-06 — Voting removed, accuracy unified, §5.3 dedup, 6 anchors, Fig 2 deleted
- **Voting/Validity removed**: §3.2 Validity Criterion subsection deleted; §4.3 Validity Check via Anchor Ensemble subsubsection deleted; §5.5 Validation Threshold Analysis section + `fig:threshold_curve` deleted; §1 voting validation sentence deleted; tab:pipeline Data Validity Rate row deleted; fig:benchmark_comparison validity-rate axis dropped (5→4 axes); fig:protocol (Fig 2) entire figure block deleted.
- **Metric unified to bias accuracy**: all "bias elicitation rate" replaced with "bias accuracy"; tab:pipeline values flipped via 100−x (e.g., InternVL3-8B 9.6→90.4); §3.2 Bias Judgment Metric simplified to single metric; direction language flipped (rises→falls, increases→decreases) wherever DPO/DeepAgent makes the benchmark harder.
- **§5.3 Candidate Pool Distillation added**: SemDeDup-inspired two-step dedup (DeepAgent intra-pool with idx-protection + Proposer incremental merge against pool, threshold 0.85, all-MiniLM-L6-v2 encoder); single compressed paragraph (was three with sub-step labels and a `tab:dedup_survival` table — both removed at user request to avoid over-detailed exposition); final 20,819 candidate triplets / 62,457 instances reported.
- **6 anchor ensemble installed**: InternVL3.5-8B / Qwen3-VL-8B / GLM-4.1V-9B / DeepSeek-VL2 / Gemma-3-27B / LLaVA-OneVision-7B. tab:benchmark_building rebuilt with real data (vertical layout, 6×3×7 = 18 rows, 5-tier red-green colour grading). Three observations rewritten: (1) DPO contributes diversification not direct exposure; (2) DeepAgent is the primary mechanism of bias exposure; (3) anchor weaknesses are anchor-specific not category-uniform — explicitly contradicting the older "Race/Gender systematically weaker" narrative.
- **Manual Construction-Quality Verification paragraph added** (§5.3, with TODO for empirical numbers) — explains why we forgo the automated validity filter.
- **bib additions**: `abbas2023semdedup`, `reimers2019sentencebert`, `internvl35`, `qwen3vl`, `glm41v`, `deepseekvl2`, `gemma3`, `llava_onevision` — all with `% TODO: verify arXiv IDs`.
- **tab:pipeline cleanup**: Raw Dataset column removed.
- **Implementation Details paragraph added** at top of §5 (Qwen3-32B + LoRA r16/α32, β=0.1, batch 32, lr 5e-5, R=2/3, T=3, 8×3090).
- **§5.4 prose updated**: cross-architecture transfer / scale offers no immunity / persistent demographic imbalance discussion (placeholder analysis pending real numbers).

## Current Status
Paper is in advanced draft: §1–§4 structurally stable; §5 has real data for §5.1/§5.2/§5.3 and the Implementation Details paragraph; §5.4 most rows still placeholder; §5.5 (Limitations) lightly stale. **No more validity/voting machinery anywhere in the paper.** **All numerical values are bias accuracy throughout.** Next priorities: (a) replace the 6 figure mockups with real plots from real data, starting with `fig:proposer_distribution`; (b) supply manual-sampling constraint-satisfaction numbers for §5.3; (c) fill remaining `tab:benchmark` rows.
