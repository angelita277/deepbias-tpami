# Anchor Model Candidates (Open-Source, ≤ 50B)

筛选标准：
- **开源权重**（HuggingFace / ModelScope 可直接下载，本地推理）
- **参数 ≤ 50B**（单卡或少量卡可跑，benchmark 构建成本可控）
- **尽量新、尽量强**（优先 2025 年发布的版本；在开源 VLM leaderboard 上排名靠前）
- **跨系列覆盖**：不同公司 / 不同 base LLM 家族 / dense + MoE 混合，保证 anchor ensemble 捕捉到的是跨架构共性 bias 而非单一家族偏差

---

## Top 20 候选

按"系列 + 版本"分组，每个条目标注参数量、发布方、发布时间、架构亮点。

### Qwen 系列（Alibaba）
| # | 模型 | 参数 | 发布 | 备注 |
|---|---|---|---|---|
| 1 | **Qwen3-VL-32B** | 32B dense | 2025 | Qwen3 家族旗舰 dense VLM；当前 ≤ 50B 组别最强之一 |
| 2 | **Qwen3-VL-8B** | 8B dense | 2025 | Qwen3 小尺寸，部署友好 |
| 3 | **Qwen2.5-VL-32B** | 32B dense | 2025 初 | 前一代同尺寸；做代际对照 |

### InternVL 系列（Shanghai AI Lab / OpenGVLab）
| # | 模型 | 参数 | 发布 | 备注 |
|---|---|---|---|---|
| 4 | **InternVL3.5-38B** | 38B dense | 2025 | 学术谱系旗舰 dense |
| 5 | **InternVL3.5-30B-A3B** | 30B total / 3B active (MoE) | 2025 | 同代 MoE 变体；架构差异 |
| 6 | **InternVL3.5-14B** | 14B dense | 2025 | 中等尺寸，同系列尺寸谱系 |
| 7 | **InternVL3-14B** | 14B dense | 2025-04 | 前一代，做代际对照 |

### DeepSeek-VL 系列（DeepSeek）
| # | 模型 | 参数 | 发布 | 备注 |
|---|---|---|---|---|
| 8 | **DeepSeek-VL2** | 27B total / 4.1B active (MoE) | 2024-12 | MoE 代表；DeepSeek 训练数据风格独特 |
| 9 | **DeepSeek-VL2-Small** | 16B total / 2.8B active (MoE) | 2024-12 | 小 MoE |

### Llama 系列（Meta）
| # | 模型 | 参数 | 发布 | 备注 |
|---|---|---|---|---|
| 10 | **Llama 3.2 Vision 11B** | 11B | 2024 | Meta 唯一 ≤ 50B 的 VLM（90B 超限） |

### Mistral / Pixtral 系列
| # | 模型 | 参数 | 发布 | 备注 |
|---|---|---|---|---|
| 11 | **Pixtral 12B** | 12B | 2024-09 | Mistral 多模态，欧洲谱系 |

### Molmo 系列（Allen Institute for AI）
| # | 模型 | 参数 | 发布 | 备注 |
|---|---|---|---|---|
| 12 | **Molmo-7B-D** | 7B | 2024-09 | 纯开放训练数据（PixMo），没有蒸馏闭源模型 → 训练数据谱系非常独立 |

### Gemma 系列（Google DeepMind）
| # | 模型 | 参数 | 发布 | 备注 |
|---|---|---|---|---|
| 13 | **Gemma 3 27B (Vision)** | 27B | 2025 | DeepMind 开源分支；与 Gemini 有差异化训练，多语言强 |

### GLM 系列（Zhipu）
| # | 模型 | 参数 | 发布 | 备注 |
|---|---|---|---|---|
| 14 | **GLM-4.5V-9B** | 9B | 2025 | GLM 谱系，中文优势，与 Qwen 训练数据风格不同 |

### Kimi-VL 系列（Moonshot AI）
| # | 模型 | 参数 | 发布 | 备注 |
|---|---|---|---|---|
| 15 | **Kimi-VL-A3B-Thinking** | 16B total / 2.8B active (MoE) | 2025 | 推理微调版；显式 CoT，行为可能与非推理模型显著不同 |

### Ovis 系列（AIDC-AI）
| # | 模型 | 参数 | 发布 | 备注 |
|---|---|---|---|---|
| 16 | **Ovis2.5-9B** | 9B | 2025 | Alibaba 内部研发分支，架构与 Qwen-VL 不同（visual embedding 对齐不同） |

### Phi 系列（Microsoft）
| # | 模型 | 参数 | 发布 | 备注 |
|---|---|---|---|---|
| 17 | **Phi-4 Multimodal** | 5.6B | 2025 | 小模型代表；Microsoft 训练数据（含强合成数据）独特 |

### MiniCPM 系列（ModelBest / 清华）
| # | 模型 | 参数 | 发布 | 备注 |
|---|---|---|---|---|
| 18 | **MiniCPM-o 2.6** | 8B | 2025 | 端侧向小模型代表 |

### LLaVA 系列
| # | 模型 | 参数 | 发布 | 备注 |
|---|---|---|---|---|
| 19 | **LLaVA-OneVision-7B** | 7B | 2024 | LLaVA 谱系最新轻量版；学术界广泛 baseline |

### Idefics 系列（HuggingFace）
| # | 模型 | 参数 | 发布 | 备注 |
|---|---|---|---|---|
| 20 | **Idefics3-8B-Llama3** | 8B | 2024 | 欧洲开源，训练数据组合独特（基于 Llama3） |

---

## 挑 6 个的几个候选组合

根据不同优先级给出三种 6-模型 anchor 组合方案。每种都兼顾"发布方多样 + base LLM 多样 + dense/MoE 混合 + 参数跨度"。

### 方案 A — 强度优先（平均能力最高）
```
Qwen3-VL-32B          (Qwen 旗舰 dense)
InternVL3.5-38B       (OpenGVLab dense)
InternVL3.5-30B-A3B   (OpenGVLab MoE)
DeepSeek-VL2          (DeepSeek MoE, 27B)
Gemma 3 27B           (Google DeepMind dense)
Molmo-7B-D            (AI2, 独立训练数据)
```
特点：都是 ≤ 38B 的强模型，组合多样。缺点是都偏大，推理成本较高。

### 方案 B — 尺寸均衡（含小模型暴露差异）
```
Qwen3-VL-32B          (大 dense)
InternVL3.5-38B       (大 dense)
DeepSeek-VL2          (中 MoE)
Llama 3.2 Vision 11B  (小 dense，Meta 谱系)
GLM-4.5V-9B           (小 dense，Zhipu 谱系)
Phi-4 Multimodal 5.6B (极小，Microsoft 谱系)
```
特点：尺寸跨度大（5.6B–38B），能揭示"小模型 cheap bias vs 大模型 latent bias"的差异，谱系更多样。

### 方案 C — 最大谱系多样性（6 个不同公司）
```
Qwen3-VL-32B          (Alibaba)
InternVL3.5-38B       (Shanghai AI Lab)
DeepSeek-VL2          (DeepSeek)
Llama 3.2 Vision 11B  (Meta)
Gemma 3 27B           (Google DeepMind)
Molmo-7B-D            (Allen Institute)
```
特点：6 个不同机构，训练数据、对齐方法都不同。**对 bias 研究最干净的 ensemble 信号**——各自的 safety alignment 独立失败方式最可能暴露真正跨架构的偏见。

---

## 选择决策点

几个需要你决定的问题：

1. **规模上限**：确定是 50B 吗？
   - 若放宽到 72B，Qwen2.5-VL-72B、Llama 3.2 Vision 90B（实际 90B）、Molmo-72B 都可进
   - 若收紧到 32B 以下，InternVL3.5-38B 要换成 InternVL3.5-14B

2. **dense vs MoE**：ensemble 里要不要至少一个 MoE？
   - MoE 行为分布可能与 dense 显著不同，加入 1-2 个可提升多样性
   - 当前方案 A、B 都含 MoE；方案 C 全 dense（除了 DeepSeek-VL2 是 MoE）

3. **推理模型是否算一个**：Kimi-VL-A3B-Thinking 是显式 CoT，行为与普通 VLM 可能完全不同。作为 anchor 风险：它对某些题的拒答率可能极高。建议暂不纳入 ensemble 主力。

4. **推理成本**：本地运行 6 个 38B 级别模型做 candidate 验证，显存需求约 6 × 80GB。如果资源紧张，优先选 B 方案（含小模型）。

---

## 补充：如何评估候选模型的"当前强度"

推荐通过以下 leaderboard / 榜单实时查询：

- [Open VLM Leaderboard (HuggingFace / OpenCompass)](https://huggingface.co/spaces/opencompass/open_vlm_leaderboard) — 主力榜单
- [VLMEvalKit](https://github.com/open-compass/VLMEvalKit) — 220+ 模型 × 80+ benchmark，复现用
- MMBench、MM-Vet、MMMU、MathVista — 最常引用的能力 benchmark
- VL-RewardBench — 对齐质量榜

---

## 最后决定建议

如果 anchor ensemble 的核心作用是**为 DPO 提供 diverse feedback + 做 benchmark validity voting**，那么"**谱系多样 > 单点强度**"。方案 C（6 个不同公司）最能避免因 anchor 同源而让 Proposer 落入 homologous lineage bottleneck（第 5.1 节实验已经报告过 Qwen2.5-VL-7B 的例子）。

若你用 Qwen3-32B 作 Proposer，**anchor ensemble 里应当尽量少放 Qwen 系**（最多保留 Qwen2.5-VL 作代际对照，不要 Qwen3-VL），避免 Proposer 与 anchor 共享过多同源分布。

---

*最后更新：2026-04-17*
