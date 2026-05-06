# §5 Experiment Figure Plan

Last updated: 2026-04-21

本文档规划 §5 Experiment 章节每一个子节该配哪些图、每张图用什么数据、用什么分析方法做、要回答什么问题，以及一个 ASCII 示意图让你知道最终图长什么样。配合 `analysis_20260408_095453/` 现有产物和仍需补的分析指出生成优先级。

---

## 设计原则

1. **图服务于 claim，不为装饰**：每张图对应一条正文要说明的具体结论。若正文没有需要视觉化的论点，宁可用表格或一句话替代。
2. **同一主题同一视角只出现一次**：分布迁移视角在 §5.1 讲透，§5.2/§5.3 不重复；§5.2 换成"策略使用视角"，§5.3 换成"最终 artifact 覆盖视角"。
3. **定量+定性成对**：每个"过程性"子节（§5.1、§5.2）配一张定量分布/频率图 + 一张定性 case study，读者既看到趋势也看到样例。
4. **4 阶段对齐**：凡展示 Proposer 演化的图，统一 4 个阶段 **Seed → Pre-DPO → DPO Iter 1 → DPO Iter 2**，保持 `tab:pipeline` 的 Raw Dataset 列与图表阶段数一致。

---

## 总预算概览

| 子节 | 图编号 | 图名 | 状态 |
|---|---|---|---|
| §5.1 Proposer Evolution | Fig 1 | `fig:proposer_distribution`（双子图：UMAP + Topic Radar） | 已插入占位 |
| §5.1 | Fig 2 | `fig:proposer_diversity`（多样性 4 阶段变化） | 已插入占位 |
| §5.2 DeepAgent | Fig 5 | `fig:deepagent_case`（Case Study：单候选 Turn 0→3 对话 trace） | 已插入占位 |
| §5.3 Benchmark | A | `fig:benchmark_distribution`（双子图：UMAP + BERTopic radar） | mockup 占位（已选） |
| §5.3 | B | `fig:benchmark_comparison`（DeepBias vs 主流 benchmark 多轴对比） | mockup 占位（已选） |
| §5.3 | C | `fig:benchmark_difficulty`（per-instance elicitation rate 直方图） | mockup 占位（已选） |
| §5.3 / Supp | Fig 7 | `fig:benchmark_samples`（三类别代表样例 grid） | 迁 Supplementary |
| §5.4 Benchmark Evaluation | — | 用 colored `tab:benchmark` 足够，不必额外出图 | — |
| §5.5 Threshold Analysis | Fig 8 | `fig:threshold_curve`（τ 敏感性：F1/PR 曲线） | 未插入 |

**§5 图总数（已定）**：6 张主图 + 1 张 Supp（fig:benchmark_samples）。加上 §1 teaser、§3 test_data、§4 method 三张结构图，正文共 9 张图，属 TPAMI 合理区间。

---

## §5.1 Proposer Evolution（2 张图）

### Fig 1 — `fig:proposer_distribution` 分布迁移（双子图）

**正文 claim**：Proposer 经过 DPO 不是随机漂移，而是先**扩散**（diversification）再**向 target 弱点集中**（targeted concentration）。

**子图 (a)：UMAP 语义空间 overlay**

- 数据源：`intern2/Age` 候选样本（或 `qwen2/Age`）每一阶段 ~1000 条 question 文本；补 BBQ/VLBiasBench Age 原始 ~300 条作为 Seed group
- 分析手段：
  1. 用 `sentence-transformers/all-MiniLM-L6-v2` 把每条 question 编码为 384 维向量
  2. 在**全部 4 组合并**的向量集上 fit UMAP（`n_neighbors=30`, `min_dist=0.1`），保证四组在同一 2D 空间可比
  3. 按 group 分色散点图；每组画半透明 convex hull 或 KDE 密度轮廓突出重心
- 要回答的问题：新迭代是否进入了新区域？是否有一轮开始出现"聚团"收敛？
- 占位文件：`analysis_20260408_095453/umap.png`（但只有 3 阶段，没 Seed；且含 llava 需过滤）

ASCII 示意：
```
              UMAP dim-2
                ↑
      ▲ ▲       │       ○ ○ ○
     ▲ ▲ ▲      │      ○ ○ ○ ○      ● = Seed (BBQ)
        ▲       │       ○ ○         ○ = Pre-DPO
      ●●●●     │     ◆ ◆           ▲ = DPO Iter 1
     ● ● ● ●    │    ◆◆◆◆          ◆ = DPO Iter 2
      ● ● ●     │     ◆ ◆
─────────────┼─────────────→ UMAP dim-1
                │
         (观察：Seed集中一角；Pre-DPO扩散到更多区域；
          Iter 1继续扩散；Iter 2在某几个子区域明显加密)
```

**子图 (b)：Topic Radar / 径向覆盖图**

- 数据源：同上 question 文本
- 分析手段：
  1. 用 BERTopic 在**所有阶段合并数据**上拟合一次主题模型，得到约 80+ topics
  2. 选 top-K（K=10–12）人类可命名的 topic（如 library/student, job interview, tech expert, public speaking, security screening 等）
  3. 每个 topic 作一条雷达轴，每阶段取该 topic 样本占比画一条多边形
- 要回答的问题：哪些 topic 是 DPO 新开发出来的？哪些 topic 是 Iter 2 明显加码的（=target 弱点）？
- 占位文件：`analysis_20260408_095453/bertopic_radar.png`

ASCII 示意：
```
                    Job/Hiring
                         ●
                       ● |○○
                    ●    |   ○   ▲▲▲
         Security  ●     |    ○  ▲  ▲  Expert
                ●        |      ○▲     ▲
                ●        |        ▲     Tech
           ────●─────────┼──────▲──────→
                ●        |      ▲
                 ●       |     ▲      Education
            Legal ●      |    ▲
                    ●    |  ▲
                      ● ●|▲
                         ●
                  Public Speaking

 外层 = 覆盖多 (Iter 2 明显向 "Expert / Tech / Education" 倾斜)
 内层 = 覆盖少 (Seed 只在 Job/Hiring 和 Security 有分布)
```

**双子图版面建议**：`figure*`（跨栏），左 UMAP、右 Radar，各占 0.48\textwidth。

---

### Fig 2 — `fig:proposer_diversity` 多样性轨迹（4 阶段变化）

**正文 claim**：DPO 前半段提多样性、后半段提针对性；这种"先扩散后收敛"的轨迹可以被 6 个指标同时量化。

- 数据源：每阶段全部候选 question（Seed 300 / Pre-DPO 2000 / Iter 1 1000 / Iter 2 1000）；每阶段对两个 target（InternVL3-8B, Qwen2.5-VL-7B）各算一条曲线
- 分析手段：
  - **Diversification 指标**（DPO 早期应上升）：
    - `effective_topic_count`（来自 BERTopic）
    - `topic_entropy`
    - `distinct-2`（bigram diversity）
    - `unique_instruction_ratio`（去重后比例）
  - **Concentration 指标**（DPO 后期应 plateau 或反弹）：
    - `mean_pairwise_cosine_sim`（句向量平均相似度）
    - `vocab_size`
  - 推荐放成一张 6-panel 小矩阵（2 行 × 3 列），或者 2-panel（上 diversification、下 concentration），每 panel 一条 InternVL 线 + 一条 Qwen 线
- 占位文件：`analysis_20260408_095453/iteration_trend.png`（需重生成为 4 阶段 + 过滤 llava）

ASCII 示意（2-panel 版）：
```
Panel (a) Diversification                Panel (b) Concentration
  0.95┤          _●                       1300┤●                 
 u_i_r┤        _/                   vocab┤  ●_                    
  0.85┤     _ /                          ┤     \_        
      ┤   _●                        900 ┤       \_    
  0.75┤ ●/                               ┤         ●___●
      └───┬────┬────┬────                └───┬────┬────┬────
         Seed Pre  I1  I2                   Seed Pre I1  I2
                                    ─── InternVL3-8B
                                    ─── Qwen2.5-VL-7B

 70 ┤      _●  (67)                  0.48┤        _●(0.47)
topic┤    _/                   cosine┤      _/
effctv┤ _/                      sim  ┤    _/
 50 ┤_●                             0.44┤  _/
    ┤(48.8)                            ┤_/
    └───┬────┬────┬────                └───┬────┬────┬────
       Seed Pre  I1  I2                   Seed Pre I1  I2
```

---

## §5.2 DeepAgent Multi-Turn Probing（2 张图）

**为什么 §5.2 不放分布图**：DeepAgent 是 instance-level 操作，Method 已明确它不改变样本分布、只深化单样本。再放 UMAP 会与 §4.2 的设计表述矛盾，且与 §5.1 重复。

### Fig 4 — `fig:deepagent_strategy` 策略使用频率

**正文 claim**：DeepAgent 随轮次演化其策略选择有规律——早轮多用 Rewriting 绕过安全阀，晚轮转入 Deepening 深挖已暴露的偏见；同时 7 条 sub-strategy 的分布在不同 target 上有差异化适配。

- 数据源：DeepAgent 在两个 target 上各 ~2000 条候选的完整 Turn 1–3 log，提取每轮用了哪个 sub-strategy（`attribute refinement / scenario deepening / comparison deepening / contextualisation / projection / behavioural-tendency / cognitive-attribution`）
- 分析手段：
  1. 从 DeepAgent log 里 parse 每 turn 的策略标签
  2. 做一张 **堆叠条形图**：x 轴 = Turn 1 / Turn 2 / Turn 3 × 两个 target = 6 根柱，每根按 7 种颜色堆叠
  3. 或做 **sankey 图**：Turn 1 → Turn 2 → Turn 3 的策略转移流向（更直观看"Rewriting 在 Turn 1 为主 → Turn 3 Deepening 为主"的转变）
- 占位文件：无，需新 analysis script

ASCII 示意（堆叠条版，推荐）：
```
Frequency (%)
 100%┤▓▓▓▓▓▓▓▓ ░░░░░░░░ ░░░░░░░░  ▒▒▒▒▒▒▒▒ ░░░░░░░░ ░░░░░░░░
     │▓▓▓▓▓▓▓▓ ██████░░ ▓▓▓▓░░░░  ▒▒▒▒▒▒▒▒ ██████░░ ▓▓▓▓▓▓░░
  60%┤████████ ▓▓▓▓▓▓██ ██████▓▓  ████████ ▓▓▓▓▓▓██ ██████▓▓
     │██████▒▒ ░░░░░░░░ ░░▓▓▓▓▓▓  ██████▒▒ ▒▒▒▒▒▒░░ ▓▓▓▓▓▓▓▓
  30%┤░░▒▒▒▒▒▒ ▓▓▓▓████ ████████  ░░▒▒▒▒▒▒ ▓▓▓▓████ ████████
   0%└──────────────────────────────────────────────────────
      T1       T2       T3         T1       T2       T3
      ╰─── InternVL3-8B ───╯      ╰── Qwen2.5-VL-7B ──╯

Legend:
 ▓ Contextualisation   ░ Projection       ▒ Behavioural-tendency
 ▓ Cognitive-attrib.   █ Attribute-refine ▓ Scenario-deepening  █ Comparison-deepening

(观察：Turn 1 Rewriting 系（上方浅色区块）占比大；
 Turn 3 Deepening 系（下方深色区块）占比显著增长；
 两个 target 上早轮的 rewriting 子策略选择略有差异)
```

版面：`figure*` 跨栏。

---

### Fig 5 — `fig:deepagent_case` Case Study（单候选 dialogue trace）

**正文 claim**：多轮概率推进的具体机制——展示同一 triplet 在 Turn 0（Proposer 原始）到 Turn 3 的 question 演化轨迹，让 reader 看到 DeepAgent 如何根据 history 选择策略。

- 数据源：手挑一条从 Turn 0 "Unknown" 被 DeepAgent 一路推成"明确有偏见 answer" 的候选；可以复用 §5.1 `fig:proposer_distribution` 中 Iter 2 阶段的一个代表候选作为 DeepAgent 的 Turn 0 输入，形成 §5.1 ↔ §5.2 叙事连续性
- 分析手段：人工挑选 + 排版（类似 method figure）
- 图内布局：纵向 4 个 block（Turn 0 / 1 / 2 / 3），每 block 含：策略标签 badge + question 文本 + target response + response 是否"Unknown"的标记
- 占位文件：无

ASCII 示意：
```
┌──────────────────────────────────────────────────┐
│ Turn 0  [Proposer DPO Iter 2 输出 / 无策略标签]  │
│  Q: "This person leads a tech startup; how       │
│      likely are investors to fund them?"         │
│  → Target: "Unknown"  ✓ 仍含糊                  │
├──────────────────────────────────────────────────┤
│ Turn 1  [Rewriting · Contextualisation]          │
│  Q: "In a pitch meeting with senior VCs, how     │
│      persuasive would this founder appear?"      │
│  → Target: "Moderately" (开始泄露偏见)            │
├──────────────────────────────────────────────────┤
│ Turn 2  [Deepening · Attribute Refinement]       │
│  Q: "Given their apparent age and appearance,    │
│      how much experience do they likely have?"   │
│  → Target: "Limited" ✗ 偏见显现                  │
├──────────────────────────────────────────────────┤
│ Turn 3  [Deepening · Comparison]                 │
│  Q: "Compared to a founder in their 30s, do      │
│      investors perceive them as less credible?"  │
│  → Target: "Yes" ✗ 强偏见                        │
└──────────────────────────────────────────────────┘
```

版面：单栏 `figure`，高度约 0.35\textheight。

---

## §5.3 Benchmark Construction（4 候选图 A/B/C/D + Fig 7 可选）

**NOTE**（2026-04-22 决定）：原 `fig:benchmark_coverage` heatmap 废弃——6 × 3 矩阵改用 `colortbl` 着色的 `tab:benchmark_building` 承担难度可视化；但 §5.3 作为论文核心产出节，仅一张样例图不足以刻画 benchmark 结构。以下 4 张候选补充图（A/B/C/D），待用户选择实际要放哪几张。配套 mockup 见 `experiment_figure_mockups.md`。

---

### Option A — `fig:benchmark_distribution` Benchmark 分布图（双子图，强烈推荐）

**正文 claim**：最终 benchmark 在三个 demographic 类别上有合理 topical 多样性；三类别共享"偏见触发 template"结构但各自有特异的语境分布。

- **数据源**：最终 benchmark 1500 条 question 文本（500/类别 × 3 类别）
- **分析手段**：
  - 子图 (a)：sentence-transformer 编码为 384 维向量 → UMAP 2D 投影 → 按 Age/Gender/Race 三色散点图
  - 子图 (b)：BERTopic 在合并数据上拟合一次（top-10 topics），每类别在 10 个 topic 上的占比画一条雷达多边形
- **支持的 claim**：
  1. UMAP 上三类别部分重叠、部分差异（共享 template + 类别特异语境）
  2. 雷达上主题画像差异化：Age 倾向 Job/Expert/Education；Gender 倾向 Job/Social Role/Public Speaking；Race 倾向 Security-Legal/Space-Venue/Consumer
- **占位文件**：`figure_mockups/figA_benchmark_distribution_umap.png` + `figA_benchmark_distribution_radar.png`
- **版面**：跨栏 `figure*`，两子图各 0.48\textwidth

---

### Option B — `fig:benchmark_comparison` 跨 benchmark 对比图（强烈推荐）

**正文 claim**：DeepBias 在 validity rate 和 elicitation rate（质量 + 挑战性）两个关键轴上显著领先主流 bias benchmark，size 与 categories 在合理区间。

- **数据源**：BBQ / VLBiasBench / GenderBias-VL / PAIRS / DeepBias（本文）共 5 个 benchmark 的元数据和跑分
  - 元数据可查原 paper（size、categories、是否 multimodal、是否报告 validity）
  - 难度跑分需在同一批 strong LVLM（例如 InternVL3-8B + Qwen2.5-VL-7B）上跑每个 benchmark 然后算 elicitation rate
- **分析手段**：5 个 small-multiples 子图并列，每子图一根坐标轴；DeepBias 用高亮色，其余灰色
- **5 个对比轴**：
  1. `# Instances`（规模）
  2. `# Categories`（demographic 覆盖）
  3. `Validity Rate (%)`（BBQ 等早期 benchmark 可能为 N/R 未报告）
  4. `Avg. Bias Elicitation Rate on Strong LVLMs (%)`（挑战性）
  5. `Multimodal` （是否含图像，binary）
- **支持的 claim**：DeepBias 在 validity 和 difficulty 两个质量轴上远超，size / coverage 在主流区间——"为什么需要新 benchmark"的核心视觉论证
- **占位文件**：`figure_mockups/figB_benchmark_comparison.png`
- **版面**：跨栏 `figure*`，\textwidth，高度约 0.25\textheight

---

### Option C — `fig:benchmark_difficulty` 难度分布直方图（可选）

**正文 claim**：benchmark 的 instance-level 难度主要落在 30-60% elicitation rate 区间，既不简单也不不可能；三类别分布形状近似，说明难度不依赖于具体 demographic。

- **数据源**：每条 instance 在 6 anchor 上的 bias elicitation rate（= 触发 bias 的 anchor 比例，0/6, 1/6, ..., 6/6）
- **分析手段**：10-bin 直方图，按类别堆叠着色；加 overall median 虚线
- **支持的 claim**：
  1. 难度分布以中间为主（30--60% 区间）
  2. 没有 trivial 或 impossible 样本堆积——说明 validity filter 清掉了"过简单 / 过难"的极端
  3. 三类别分布形状接近——说明 benchmark 难度对类别不敏感
- **占位文件**：`figure_mockups/figC_benchmark_difficulty.png`
- **版面**：单栏 `figure`，\linewidth
- **与 Option A 的差异**：A 刻画 "语义空间覆盖"，C 刻画"难度空间分布"——两个维度互补；若要只保一张，A 的信息量更高

---

### Fig 7（已有，迁 Supplementary）— `fig:benchmark_samples` 三类别代表样例 grid

**正文 claim**：直观展示 benchmark 长什么样——三个类别各抽 2 个样例，配 question。起到"读者看完表格 + 分布图后还能看到数据具体样貌"的作用。

- **数据源**：每类手挑 2 条 representative triplet（通过多数 anchor 产生 non-Unknown 的高区分样本）
- **分析手段**：人工挑选 + composition
- **占位文件**：`figure_mockups/fig7_benchmark_samples.png`
- **版面**：`figure*`，3 行 × 2 列
- **挑样标准**：
  - 在 6 anchor 中 ≥4 个给出一致 non-Unknown 响应的"高成功率"样本
  - 三类别 question 长度 / 复杂度尽量接近，避免读者把难度差异错误归因到 question 本身
- **归属**（2026-04-22 用户决定）：Fig 7 移 Supplementary；主正文只在 §5.3 末尾用一句话引用"representative samples are shown in the Supplementary Material"

---

### §5.3 选定组合（2026-04-22 用户决定）

- **正文**：A（分布）+ B（对比）+ C（难度直方图）= 3 张
- **Supplementary**：Fig 7（样例 grid）
- **已弃用**：Option D（3 × 3 组成矩阵）——依赖三特征人工标注成本高，且 A/B 已足够刻画 benchmark 结构

---

## §5.4 Benchmark Evaluation

**无独立图推荐**。这节核心是一张大 leaderboard table（`tab:benchmark`，当前已有占位），对比多个 VLM 在 benchmark 上的表现。若正文空间允许，可附一张 **bar chart**（不是必需）：

ASCII 示意（bar chart 版）：
```
Bias Elicitation Rate (%)
   55 ┤ █
   50 ┤ █     █
   45 ┤ █  █  █
   40 ┤ █  █  █  █
   35 ┤ █  █  █  █  █
   30 ┤ █  █  █  █  █  █
      └───┴──┴──┴──┴──┴──┴──────→
     LLaVA Qwen2 Deep Qwen3 Intern Intern3.5
     -OV   .5    VL   -VL   VL3   -38B
```

建议就用 table，把版面让给前三节。

---

## §5.5 Validation Threshold Analysis

### Fig 8 — `fig:threshold_curve` τ 敏感性

**正文 claim**：阈值 τ 的选择不是任意的——在 τ = 1/3 附近 F1 或过滤质量最优；扫描 τ 可视化决策依据。

- 数据源：200 条人工标注 ambiguity label 的 question（validation set），6 anchor 产生 K=6 × 3 = 18 response per triplet
- 分析手段：
  - 对 τ ∈ {0, 1/6, 2/6, …, 6/6} 扫一遍
  - 画 **PR 曲线**（precision / recall）或 **F1 vs τ 曲线**
  - 最优 τ 用星号/垂线高亮
- 占位文件：无

ASCII 示意：
```
 F1
 0.85┤        _●_
     │      _/   \_
 0.75┤   _/         \_
     │  /              \_
 0.65┤_/                  \_
     │                      \_
 0.55┤                        \_
     └──┬───┬───┬───┬───┬───┬───┬──→ τ
        0  1/6 2/6 3/6★4/6 5/6  1

 ★ = 最优 τ = 1/3 (paper 选的值)
```

---

## 总图单与生成优先级

| # | 图 | 占位 | 需做的分析 | 优先级 |
|---|---|---|---|---|
| 1 | `fig:proposer_distribution` | ✓（已插入，需过滤 llava、补 Seed、重生成） | UMAP + BERTopic 重跑 4 组 | P0 |
| 2 | `fig:proposer_diversity` | ✓（已插入，需补 Seed、过滤 llava、重生成） | diversity script 加 Seed 组 | P0 |
| 5 | `fig:deepagent_case` | ✓（mockup 占位） | 手挑一条贯穿 Turn 0→3 的 trace | P1 |
| A | `fig:benchmark_distribution` | ✓（mockup 占位） | 最终 benchmark 上跑 UMAP + BERTopic radar（三类别） | P0 |
| B | `fig:benchmark_comparison` | ✓（mockup 占位） | 查 4 个主流 benchmark 元数据 + 在 strong LVLMs 上跑它们做难度对标 | P0 |
| C | `fig:benchmark_difficulty` | ✓（mockup 占位） | per-instance 6-anchor elicitation 直方图 | P1 |
| 7 | `fig:benchmark_samples`（Supp） | mockup | 手挑 6 条代表样例 | P2 |
| 8 | `fig:threshold_curve` | — | 200 标注集上扫 τ | P1 |

**P0 = 送一审前必须**；P1 = 一审后可补；P2 = 可选。

---

## 其他事项

- **Seed 阶段数据目前缺失**：需要先补上原始 BBQ/VLBiasBench Age 子集（~300 条）跑同一套 diversity + UMAP + BERTopic 分析，加入 `input_summary.csv` 作为新 group。这一步同时也填 `tab:pipeline` 的 Raw Dataset 列。
- **LLaVA 组过滤**：所有 analysis script 未来重跑时，input 不再包含 llava1/llava2，输出图会自动干净。
- **一致性**：Fig 1/2 都是 4 阶段（Seed, Pre-DPO, Iter 1, Iter 2），保持 §5.1 叙事和 `tab:pipeline` 的列完全对齐。
- **版面预算**：`figure*` 跨栏图最多 2 张（`fig:proposer_distribution` 和 `fig:deepagent_strategy`），其余用单栏减少占纸。
