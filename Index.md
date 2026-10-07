# Index.md — 关键词路由表

**用法**：在下面找到最接近的一条，**只读那一列指向的文件**。不要全读。

> 前提：你已经跑过 `git pull --rebase`（见 `SKILL.md` / `00StartHere.md` 第 0 步）。

---

## 🔤 触发词 → 文件

| 你提到 / 你需要 | 读这个 |
|---|---|
| 记忆、记得、以前、回忆、我上次说 | `Skills/Memory/SKILL.md` |
| 聊天记录、日志、当天发生了什么 | `Memory/<Agent>/Daily/YYYY-MM-DD.md` |
| 技能、怎么写 Skill、审查 Skill、装 Skill | `Skills/SkillForge/SKILL.md` |
| GitHub、PR、merge、issue、仓库、commit、gh | `Skills/Github/SKILL.md` |
| 邮件、发信、写信、回复、收件箱、inbox | `Skills/Email/SKILL.md` |
| 报告、深度报告、发布网页、reports | `Skills/Reports/SKILL.md` |
| 传文件、发我文件、下载、交付 | `Skills/Files/SKILL.md` |
| SSH、服务器、远程、NAS、VPS、那台机器 | `Skills/RemoteAccess/SKILL.md` |
| 搜索、查资料、最新消息、网页、调研 | `Skills/WebSearch/SKILL.md` |
| 写代码、重构、大项目、写功能 | `Skills/Coding/SKILL.md` |
| 截图、桌面、鼠标、键盘、窗口、自动化 | `Skills/Desktop/SKILL.md` |
| 密钥、密码、token、key、凭据 | `05Secrets.example.md` |
| 设备、配置、域名、网络、我家 | `06World.md` |
| 朋友、家人、同事、关系 | `06World.md` |
| 你是谁、性格、语气、怎么说话 | `02Identity.md` |
| 能力清单、能干什么 | `03Capabilities.md` |
| 本机装了什么 / 要不要装 | `01Environment.md` |
| 仓库规则 / 权限 / 提交格式 | `AGENTS.md`（仓库根，**协议**） |
| 为什么这么设计 | `Docs/Architecture.md`、`Docs/Why.md` |
| 怎么部署 / 多机 / 多用户 | `Docs/Deployment.md` |
| 没有服务器怎么办 | `Docs/ZeroServer.md` |
| 谁来当维护者 / 定时任务 | `Docs/Orchestrator.md` |
| 看板怎么跑 | `Docs/Dashboard.md` |
| 让 Agent 干活（上线/部署/写技能/当维护者） | `Prompts/` |
| **其他任何能力** | `SkillsList.md` |

---

## 📁 顶层文件清单

| 路径 | 一句话 |
|---|---|
| `AGENTS.md` | **仓库协作协议（唯一权威）** |
| `CLAUDE.md` | 协议的精简指针（Claude Code 自动加载） |
| `SKILL.md` | 本仓库作为 Skill 的入口 |
| `00StartHere.md` | 新 Agent 上手 8 步 |
| `Index.md` | 本文件（关键词路由） |
| `SkillsList.md` | 技能总清单 |
| `01Environment.md` | 本机环境（已装 / 没装） |
| `02Identity.md` | 人格与语气 |
| `03Capabilities.md` | 能力总表 |
| `04RemoteAccess.md` | 远端机器与 SSH |
| `05Secrets.example.md` | 凭据**字段**清单（真实值不在仓库） |
| `06World.md` | 设备 / 网络 / 人 |
| `README.md` | 给**人**看的仓库说明（英文） |
| `README.zh.md` | 给**人**看的仓库说明（中文） |
| `Docs/` | 设计文档：为什么、架构、部署、看板…… |
| `Prompts/` | 直接丢给 Agent 的提示词 |
| `Skills/` | 技能库 |
| `Memory/<Agent>/` | 各 Agent 的私有记忆（每人只写自己的） |
| `Scripts/` | 治理脚本 |
| `Dashboard/` | 只读活动看板 |
| `Credentials/` | 真实密钥（**已 gitignore，不在仓库里**） |

---

## 🧭 按任务找东西

| 我想…… | 去哪 |
|---|---|
| 让它记住一件事 | 写进 `Memory/<我的名字>/` |
| 让**所有** Agent 都会做某件事 | 写一个 `Skills/<Name>/SKILL.md`，开 PR |
| 让**所有** Agent 都知道某件事 | 提 PR 更新顶层文档或 `06World.md` |
| 知道谁在干活 | `Dashboard/` 或 `Scripts/audit.sh` |
| 检查有没有密钥泄漏 | `bash Scripts/leakscan.sh` |
| 加一个新的 Agent | 新建 `Memory/<AgentName>/`，在 `AGENTS.md` 第 13 条登记 |
