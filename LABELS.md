# 标签体系

本仓库的标签不是装饰，是**分类 + 信号**。下表是完整定义。

> 用法：一个 issue / PR 通常带 **1 个类型 + 1 个优先级 +（可选）1 个影响面 + 1 个区域**。
> 评分标签（`rating:`）只用在 PR 上，表示合并质量。

---

## 🐛 类型（Type）

每个 issue / PR **必须**带一个。

| 标签 | 含义 |
|---|---|
| 🐛 bug | 行为不符合预期 |
| ✨ enhancement | 新增或改进能力 |
| 📚 documentation | 文档、协议、提示词 |
| ❓ question | 使用或设计上的疑问 |
| 🙋 help wanted | 需要外部帮助 |
| 🌱 good first issue | 适合第一次贡献 |

---

## 🔴 优先级（Priority）

| 标签 | 含义 |
|---|---|
| 🔴 P0 | **紧急**：密钥泄漏、记忆丢失、仓库被写坏 |
| 🟠 P1 | 高：阻塞正常使用 |
| 🟡 P2 | 中：正常优先级 |
| 🟢 P3 | 低：锦上添花 |

---

## 🚧 状态（Status）

| 标签 | 含义 |
|---|---|
| 🚧 in progress | 有人在做了 |
| 🧱 blocked | 卡住了，需要外部输入 |
| ✅ ready to merge | 可以合并（审阅通过） |
| 🎉 merged | 已合并 |
| 🚫 wontfix | 明确不做（并说明为什么） |

---

## 💥 影响面（Impact）

这个项目的真实失效模式，**不是通用模板**：

| 标签 | 含义 |
|---|---|
| 💥 impact: security | 密钥 / 凭据边界被突破 |
| 🗑️ impact: data-loss | 记忆被覆盖或丢失 |
| 🧨 impact: repo-integrity | 脚本写坏仓库、历史被改写 |
| ⚖️ impact: protocol | 协议有歧义，导致各 Agent 行为分歧 |
| 🔌 impact: portability | 只在我的机器上能跑 |
| 🧷 impact: other | 其它值得标注的影响 |

---

## rating: —— PR 质量分档（**从小到大**）

主题取自这个项目本身：**从孤立节点，到完整网格。**

| 标签 | 含义 |
|---|---|
| ⚪ lone node | **孤立节点**——只解决单点，没有接入既有结构 |
| 🔗 linked pair | **相连两点**——与相邻部分接通，但仍是局部 |
| 🧩 patched cluster | **局部成块**——自身自洽可用 |
| 🕸️ woven web | **织入网络**——与既有协议、风格、目录结构一致 |
| 🌐 full mesh | **完整网格**——完全融入，可当作范例被引用 |

**顺序：⚪ lone node → 🔗 linked pair → 🧩 patched cluster → 🕸️ woven web → 🌐 full mesh**

> 评分针对的是**这次改动与既有系统的贴合度**，不是「代码写得好不好」。

---

## 区域（Area）

| 标签 | 含义 |
|---|---|
| area: protocol | `AGENTS.md` 与协作规则 |
| area: skills | `Skills/` 下的技能 |
| area: scripts | `Scripts/` 治理脚本 |
| area: dashboard | `Dashboard/` 只读看板 |
| area: docs | `docs/` 与 `Prompts/` |

---

## 为什么没有「自动关闭 / 机器人」类标签

标签体系里有一类特殊的**信号标签**——它们本身不是分类，而是给自动化读的
（`r: spam`、`triage: ...`、`close: ...`）。**本仓库没有跑任何自动化机器人**，
所以这类标签一律不加：**没有机器人读的标签是死重量。**

如果将来接入了自动化（例如一个负责关闭离题 issue 的 workflow），再按实际规则补。
