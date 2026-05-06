# §5 Experiment Figure Mockups

Last updated: 2026-04-21

这份文档里每张图都是 `matplotlib` 渲染的**假数据示意图**，目的是让你一眼看清最终图的样貌和版面，**不用等真实实验数据**就能评判版面是否合理、要不要调整。

- 详细的数据源、分析手段、TODO 列表见配套文档 `doc/experiment_figure_plan.md`（ASCII 版）。
- 全部 mockup 由 `doc/generate_figure_mockups.py` 一键生成，想改样式直接改脚本重跑。
- PNG 产物在 `doc/figure_mockups/`。

---

## §5.1 Proposer Evolution（2 张图）

### Fig 1a — `fig:proposer_distribution` 子图 (a)：UMAP 语义空间迁移

![UMAP mockup](figure_mockups/fig1a_proposer_umap.png)

- **数据**：4 阶段 Proposer question 文本的句向量，经 UMAP 2D 投影。
- **读法**：Seed 集中在左上；Pre-DPO 已扩散；Iter 1 进入多个新子区域（diversification）；Iter 2 明显向两个子团收敛（targeted concentration）。
- **支持 claim**：DPO 先扩散再收敛。

### Fig 1b — `fig:proposer_distribution` 子图 (b)：BERTopic 主题雷达

![Topic Radar mockup](figure_mockups/fig1b_proposer_radar.png)

- **数据**：10 个 top BERTopic 主题在 4 阶段上的占比。
- **读法**：Seed 多边形最小（主题集中在少数区域）；Iter 1 面积最大（广覆盖）；Iter 2 在 "Expert/Tech"、"Public Speaking"、"Education" 方向凸出（定向加码）。
- **支持 claim**：同上，从主题层面补充证据。

*版面建议*：两子图合并为一张 `figure*` 跨栏图，各占 0.48\textwidth。

---

### Fig 2 — `fig:proposer_diversity` 多样性轨迹（6 指标 × 2 target × 4 阶段）

![Diversity Trajectory mockup](figure_mockups/fig2_proposer_diversity.png)

- **数据**：每阶段全部候选 question 上算 6 个指标；每指标一条 InternVL3-8B 线 + 一条 Qwen2.5-VL-7B 线。
- **读法**：
  - 上排（Diversification 指标）：Effective Topic Count / Topic Entropy / Distinct-2 / Unique-Instruction Ratio —— 都在 Iter 1 达峰，Iter 2 轻微回落。
  - 下排（Concentration 指标）：Mean Cosine Sim. 在 Iter 2 抬升；Vocabulary Size 在 Iter 2 明显缩水。
- **支持 claim**：六个独立指标同时呈现"先扩散后收敛"的一致模式。

---

## §5.2 DeepAgent Multi-Turn Probing（2 张图）

### Fig 4 — `fig:deepagent_strategy` 子策略使用频率堆叠条

![DeepAgent Strategy mockup](figure_mockups/fig4_deepagent_strategy.png)

- **数据**：从 DeepAgent log 解析出每 turn 选的 sub-strategy；每根柱子归一化到 100%。
- **读法**：
  - 左 3 柱 InternVL3-8B / 右 3 柱 Qwen2.5-VL-7B。
  - Turn 1 以 Rewriting 四条策略（红/紫/棕/灰）为主 → 绕过安全阀。
  - Turn 3 切换成 Deepening 三条策略（蓝/橙/绿）为主 → 深挖已暴露的偏见。
  - 两 target 的策略偏好略有差异（比如 Qwen 早轮 Rewriting 红色块比 InternVL 稍少）。
- **支持 claim**：多轮策略选择有规律的"先绕过后深挖"演化 + 跨模型适配性。

### Fig 5 — `fig:deepagent_case` DeepAgent Case Study（单候选 Turn 0→3 trace）

![DeepAgent Case mockup](figure_mockups/fig5_deepagent_case.png)

- **数据**：一条候选从 Turn 0（Proposer DPO Iter 2 输出）到 Turn 3 的完整对话记录；每 turn 标注策略 + question + target response。
- **读法**：灰色 badge = 起点；橙色 badge = Rewriting；绿色 badge = Deepening。Response 颜色由灰→深红，反映偏见程度递增。
- **支持 claim**：直观展现 history-aware 策略选择如何把一个模糊 question 推向明确偏见。
- **建议**：这条 trace 的 Turn 0 可以**复用 §5.1 `fig:proposer_distribution` 中 Iter 2 阶段的一个代表候选**作为起点，让 §5.1 ↔ §5.2 叙事自然衔接。

---

## §5.3 Benchmark Construction（4 候选图 A/B/C/D + Fig 7 可选）

**背景**：之前的 `fig:benchmark_coverage` heatmap 已废（6×3 矩阵改用 `colortbl` 着色版 `tab:benchmark_building` 承担难度可视化）。但 §5.3 作为论文的核心产出节，仅靠一张样例图（Fig 7）不足以完整刻画 benchmark 的结构与定位。以下是 **4 张候选补充图（A/B/C/D）**，请挑选实际要放哪一张或几张。

---

### Option A — `fig:benchmark_distribution` Benchmark 分布图（双子图）

**一句话概括**：用 UMAP + Topic Radar 展示最终 benchmark 三类别在语义空间里的覆盖与重叠，回答"benchmark 是否有合理的 topical 多样性、三类别是否共享 template 结构"。

#### 子图 (a)：UMAP 语义散点

![Benchmark UMAP mockup](figure_mockups/figA_benchmark_distribution_umap.png)

- **坐标**：2D UMAP 降维，每点一条 question；按 Age / Gender / Race 三色着色
- **读法**：三类别占据部分重叠、部分差异化的区域——说明 benchmark 既有共享"偏见触发 template"（重叠区）又有类别特异的语境（各自核心区）
- **支持的 claim**：benchmark 在语义层面不是三个互不相干的子集，而是共享结构的 coherent 整体

#### 子图 (b)：BERTopic 主题雷达

![Benchmark Topic Radar mockup](figure_mockups/figA_benchmark_distribution_radar.png)

- **坐标**：10 个 BERTopic 主题作径向轴；三类别各画一条多边形
- **读法**：
  - Age 在 "Job/Hiring / Expert-Tech / Education" 方向突出——反映年龄偏见的能力/经验触发点
  - Gender 在 "Job/Hiring / Social Role / Public Speaking" 突出——反映职业/权威触发点
  - Race 在 "Security-Legal / Space-Venue / Consumer" 突出——反映空间/消费场景触发点
- **支持的 claim**：三类别的主题画像在结构上差异化，说明 benchmark 对每类 bias 的触发场景有针对性覆盖而非随机拼接

**版面建议**：跨栏 `figure*`，两子图各 0.48\textwidth。

---

### Option B — `fig:benchmark_comparison` 跨 benchmark 对比图

![Benchmark Comparison mockup](figure_mockups/figB_benchmark_comparison.png)

**一句话概括**：把 DeepBias 与主流 bias benchmark（BBQ / VLBiasBench / GenderBias-VL / PAIRS）在 5 个关键轴上逐一对比，回答"为什么 DeepBias 作为一个新 benchmark 值得存在"。

- **坐标**：5 个 small-multiples 子图（并列）；每子图 = 5 个 benchmark × 一个指标柱状图；DeepBias 用橙色高亮，其余灰色
- **5 个对比轴**：
  1. `# Instances`（规模）
  2. `# Categories`（demographic 覆盖）
  3. `Validity Rate (%)`（是否经过人/模型一致性验证，BBQ 早期多未报告 → N/R）
  4. `Avg. Bias Elicitation Rate on Strong LVLMs (%)`（难度 / 挑战性）
  5. `Multimodal`（是否含图像模态）
- **支持的 claim**：DeepBias 在 Validity Rate 和 Elicitation Rate 两个关键质量轴上显著领先（mockup 数字 88% / 48% vs others 45-62% / 19-31%），Size / Categories 与主流持平或略少但质量更高。这是 §5.3 "定位贡献" 的核心视觉论证
- **数据需要**：每个 benchmark 的真实数字需手动查论文或自己测量（尤其 elicitation rate 需在相同 LVLM 上跑其它 benchmark）

**版面建议**：跨栏 `figure*`，宽 \textwidth，高度压缩（约 0.25\textheight）。

---

### Option C — `fig:benchmark_difficulty` 难度分布直方图

![Benchmark Difficulty mockup](figure_mockups/figC_benchmark_difficulty.png)

**一句话概括**：展示 benchmark 中每条 instance 在 6 个 anchor 上的 bias elicitation rate 分布，回答"benchmark 是不是合理难度（不太易也不太难）"。

- **坐标**：
  - X = per-instance bias elicitation rate（6 anchor 中触发 bias 的比例），0--100% 分成 10 个 bin
  - Y = 落入该 bin 的 instance 数量
  - 按 Age / Gender / Race 堆叠着色
  - 虚线 = 全部 instance 的总 median
- **支持的 claim**：
  1. **分布以中间为主**：大多数 instance 在 30--60% 难度区间——既不是 "过简单" 也不是 "过难"
  2. **没有 trivial 或 impossible 样本堆积**：两端稀疏，说明 validity filter 过滤掉了不合格数据
  3. **三类别分布形状近似**：stack 各色比例相近说明难度调节不依赖于具体 demographic 类别
- **与 Option A 的差异**：A 是"语义空间覆盖"，C 是"难度空间分布"——两个维度互补

**版面建议**：单栏 `figure`，\linewidth。

---

### Fig 7（已有，移至 Supplementary）— `fig:benchmark_samples` 代表样例 grid

![Sample Grid mockup](figure_mockups/fig7_benchmark_samples.png)

**一句话概括**：让读者在看完数字 / 分布 / 组成后，还能看到 benchmark 里的题目到底长什么样——3 类别 × 2 代表样例的缩略展示。

- **坐标**：3 行（Age / Gender / Race）× 2 列（每类别 2 个代表样例）
- **每格内容**：一张三联图占位方块 + 该样例的 question + 在 6 anchor 上的 *ensemble majority response*
- **支持的 claim**：
  1. **Question 表面中性**：偏见只在图像属性触发下才泄露——对应 §3 Protocol 的 "intentional ambiguity" 约束
  2. **三类别触发点各异**：呼应 Option A 雷达图观察到的 topic 差异
  3. **Ensemble majority 背书样本质量**：≥4/6 anchor 一致输出 = 跨模型结构性偏见
- **可选性**：若 A/B/C/D 已讨论充分，Fig 7 可砍到 Supplementary

---

### §5.3 选定组合（2026-04-22 用户决定）

- **正文**：Option A（分布）+ Option B（对比）+ Option C（难度直方图）共 3 张
- **Supplementary**：Fig 7（样例 grid）
- **Option D**：已弃用（3 × 3 组成矩阵依赖三特征人工标注成本高，图信息量与 A 重复过多）

---

## §5.5 Validation Threshold Analysis（1 张图）

### Fig 8 — `fig:threshold_curve` 阈值 τ 敏感性

![Threshold Curve mockup](figure_mockups/fig8_threshold_curve.png)

- **数据**：200 条人工 ambiguity 标注集上，τ ∈ {0, 1/6, 2/6, …, 1} 扫出的 F1 / Precision / Recall。
- **读法**：
  - 红实线 F1 在 τ ≈ 1/3 处到达平台段最优；
  - Precision（蓝虚）随 τ 增加单调上升；
  - Recall（绿虚）随 τ 增加单调下降；
  - 黑色星号标记最终选定的 τ = 1/3。
- **支持 claim**：τ = 1/3 的选择不是任意拍脑袋，而是 F1 平衡点 + Precision/Recall tradeoff 的定量依据。

---

## §5.4 Benchmark Evaluation

**不出图**——用一张大 leaderboard table (`tab:benchmark`) 承载所有对比模型。

---

## 版面总览

| # | 图 | 版面 | 宽度 |
|---|---|---|---|
| 1 | `fig:proposer_distribution` (a)+(b) | `figure*` 跨栏 | 2 × 0.48\textwidth |
| 2 | `fig:proposer_diversity` | `figure*` 跨栏 | \textwidth |
| 5 | `fig:deepagent_case` | `figure` 单栏 | \linewidth |
| A | `fig:benchmark_distribution` (a)+(b) | `figure*` 跨栏 | 2 × 0.48\textwidth |
| B | `fig:benchmark_comparison` | `figure*` 跨栏 | \textwidth |
| C | `fig:benchmark_difficulty` | `figure` 单栏 | \linewidth |
| 7 | `fig:benchmark_samples`（移至 Supp） | `figure*` 跨栏 | \textwidth |
| 8 | `fig:threshold_curve` | `figure` 单栏 | \linewidth |

**TPAMI 风格友好度**：§5.3 四张候选（A/B/C/D）全放会超预算——推荐组合见 §5.3 末尾。最终加几张取决于你选哪版（保守 / 标准 / 完整）。

---

## 怎么用这份 mockup 去迭代

1. 先浏览 8 张图，标记哪些"看着不对劲"——版面拥挤？色彩混淆？图太矮？
2. 有需要改的告诉我，我改 `generate_figure_mockups.py` 重跑。
3. 定稿后再根据真实数据替换每张图（对每张图真实数据的收集清单见 `doc/experiment_figure_plan.md` 最后的"总图单与生成优先级"表）。
