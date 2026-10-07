# AGENTS.md — 协作协议

> 本文件是 MindMesh 仓库的**最高优先级规则**。任何 Agent 在本仓库操作前**必须先完整读完本文件**。
> 它规定的不是「怎么做某件事」，而是「**多个 Agent 怎么在同一个仓库里共存**」。

---

## 项目速览（给 AI 编码 Agent）

**MindMesh** 是一个「多 Agent 共享记忆 + 技能 + 协作规则」的 Git **参考架构**。
**没有构建过程，没有运行时依赖，仓库本身就是产物。**

| 项 | 值 |
|---|---|
| 形态 | 文档为主（Markdown）+ Shell + Python 3 |
| 构建 | 无 |
| 依赖 | 无（看板只用 Python 标准库） |
| 许可 | Apache-2.0 |

### 常用命令

| 目的 | 命令 |
|---|---|
| 治理审计 | `bash Scripts/audit.sh` |
| 提交前密钥扫描 | `bash Scripts/leakscan.sh` |
| 本机体检 | `bash Scripts/check-env.sh` |
| 记忆同步 | `bash Scripts/sync.sh <AgentName>` |
| 起看板 | `cd Dashboard && MINDMESH_ROOT="$(cd .. && pwd)" python3 server.py` |
| 全量检查 | 推送后会跑 `.github/workflows/ci.yml` |

### 改动约定

- **一个 PR = 一件事。**不要在无关文件上顺手改。
- 提交必须带 `Agent: <名字>` trailer（第 9 条）。
- **`AGENTS.md` 只能由人类维护者合并**（第 18 条）。
- **不引入新的运行时依赖**——除非有非常强的理由。

### 最容易踩的三个坑

1. 把「所有 Agent 都该知道的事」只写进自己的 `Memory/` —— **等于没写**，别人不会去翻你的目录。
2. 忘记 `git pull --rebase` 就开始写。
3. 在看板里加写操作 —— **看板必须永远只读。**

---

## 0. 拿到仓库的第一件事：`git pull --rebase`

```bash
cd <你的仓库路径>
git pull --rebase
```

**无论你接下来要做什么——哪怕只是去读记忆——第一件事都是先同步。**

| 不 pull 的后果 | |
|---|---|
| ① **基于过期内容做判断** | 别人已经改过，你读到的还是旧版本。**这是最危险的一种失败**，因为你自己察觉不到 |
| ② push 被拒 | `non-fast-forward`，白忙一场 |

> 这是本协议的第一原则。细则见第 8 条。

---

## 1. 核心目标

本仓库用于统一管理一个「人 + 多个 Agent」组合的全部 **Skill** 与 **记忆文件**。
所有 Agent 通过本仓库实现：

- **Skill 的统一存放、统一更新与统一分发**
- **各 Agent 独立记忆的私有化存放与版本管理**
- **多 Agent 并行协作而不互相冲突**

原则：**私有优先、权限隔离、仅以 Git 为唯一同步机制、杜绝密钥泄露。**

**非目标**：本仓库不是应用、不是服务、不是插件。它不提供 API，不提供运行时，也不试图接管 Agent 自己的原生能力。

---

## 2. 仓库结构与命名规范

```text
MindMesh/
├── AGENTS.md / CLAUDE.md     本协议
├── SKILL.md                  技能主入口
├── README.md                 人类可读说明（英文）
├── README.zh.md              人类可读说明（中文）
├── 00StartHere.md            上手流程
├── 01Environment.md          本机环境
├── 02Identity.md             人格与语气
├── 03Capabilities.md         能力总表
├── 04RemoteAccess.md         远端 / SSH / 服务器
├── 05Secrets.example.md      凭据字段清单（占位符）
├── 06World.md                设备 / 网络 / 人
├── Index.md                  关键词路由表
├── SkillsList.md             技能总清单
├── docs/                     设计文档
├── Prompts/                  给 Agent 的提示词
├── Skills/                   本组合的专属技能
│   └── <Name>/SKILL.md
├── Memory/                   各 Agent 的私有记忆区
│   └── <AgentName>/
├── Scripts/                  可直接执行的治理脚本
├── Dashboard/                只读活动看板
├── Credentials/              🚫 已 gitignore，永不入库
└── .gitignore
```

**命名规范**：所有受管文件名与目录名一律 **PascalCase**（每个单词首字母大写、无空格、无连字符、无下划线）。

**必须保留原名的少数文件**（工具自动发现依赖这些固定名，改了就失效）：

| 文件名 | 原因 |
|---|---|
| `AGENTS.md` | Codex / Cursor 等自动读取 |
| `CLAUDE.md` | Claude Code 自动读取 |
| `SKILL.md` | Skill 规范要求 |
| `README.md` | 各平台通用约定 |
| `YYYY-MM-DD.md` | 日期文件，格式固定 |

---

## 3. 权限与操作基准

- 默认基准：**Agent 只对自己的 `Memory/<AgentName>/` 有写权限。**
- **只读**：`Skills/`、`docs/`、`Scripts/`、`Dashboard/`、顶层文档。
- **修改上述只读区域的唯一合法方式**：创建分支 + 发 Pull Request（见第 5、11 条）。
- **严禁**删除或改写任何其他 Agent 的文件。

---

## 4. Memory 目录使用规范

- 每个 Agent 在 `Memory/<AgentName>/` 下存放自己的全部记忆。
- 目录名必须与为该 Agent 分配的名字**完全一致**（PascalCase）。
- **允许**：在本目录内自由创建、修改、删除文件。
- **禁止**：写入其他 Agent 的目录。
- 建议在目录内维护自己的 `README.md` / 索引文件，并在其中记录长期结论。

**记忆的分层建议**（可按需采用）：

| 层 | 建议文件 | 用途 |
|---|---|---|
| 活跃 | `Memory.md` | 精简的当前状态，每次会话开始时读 |
| 日志 | `Daily/YYYY-MM-DD.md` | 当天发生的事、决策、踩过的坑 |
| 参考 | `Reference-*.md` | 某个领域的细节（邮件 / 网络 / 工具……） |
| 学习 | `Learnings.md` | 犯过的错 + 正确做法 |

> **写文件 > 心理笔记。**不写进文件的东西，会话一结束就不存在了。

---

## 5. Skills 目录使用规范

`Skills/` 放本组合的专属技能，**使用者对其无写权限**。

如需新增或修改技能：

1. 从最新 `main` 建分支 `skill/<名字>` 或 `add-skill/<名字>`；
2. 修改 `Skills/<SkillName>/SKILL.md`；
3. 推送分支；
4. 创建 **Pull Request**，指定审阅人；
5. 合并后本地切回 `main` 并 `git pull`。

**自主同步例外**：若某次变更**仅涉及自己的 Memory 目录**，可直接 push（见第 10 条）。

**技能写作规范**见 `docs/SkillAuthoring.md`，也可以直接让 Agent 按 `Prompts/AuthorSkill.md` 来写。

---

## 6. 上游 / 通用技能（可选）

如果你同时维护一个「通用技能库」（第三方 Skill 的本地集合），建议：

- 单独目录（例如 `Library/`），**禁止直接修改**；
- 由**维护者**定期从上游同步，并以**低频、整块**的提交方式更新
  （例如 `skill: sync upstream snapshot (YYYY-MM-DD)`），避免历史被零碎改动撑爆；
- 第三方技能各自遵循其原始许可，**保留其 LICENSE 与出处**。

> 更推荐的做法是 **不把第三方技能复制进仓库**，而是用脚本按名安装。
> 复制进仓库会带来体积、授权、更新三重麻烦。

---

## 7. 通用文件操作准则

- 新增文件默认放各自的 `Memory/<AgentName>/`。
- 临时文件一律放**仓库外**，或用 `.tmp` 后缀并在提交前清理。
- 批量操作时过滤系统隐藏文件（`.DS_Store`、`Thumbs.db`、`desktop.ini`）。
- **禁止**使用超长路径或含特殊字符的文件名。
- 单个文件建议 **< 5 MB**；大文件（数据集、模型、二进制）**不得入库**，走外部存储。

---

## 8. Git 操作基本准则

- 默认分支 `main`。
- **任何操作的第一件事都是 `git pull --rebase`**——包括你只是想去**读**记忆。
- 遇到冲突：解决后在 `Memory/<AgentName>/` 写一条记录（谁、什么时候、为什么、怎么解决），然后继续。
- 提交到 `main` 前**必须**先 pull，并保证可线性快进。
- 提交前先检查 `git status`，确认没有把临时文件、密钥、大文件带进去。

---

## 9. Commit Message 规范

```text
<AgentName>: <一句话说明>

<可选：详细说明>

Agent: <AgentName>
```

- 首行**必须以你的 Agent 名开头**，后接冒号 + 空格。
- **末尾必须单独一行**写 `Agent: <AgentName>`。
- 示例：

```text
ClaudeCode: 记录今日课程笔记与作业进度

- 新增 2026-01-01.md
- 更新课表索引

Agent: ClaudeCode
```

> 这个 trailer 不是形式主义：活动看板、活跃度审计、责任追溯都依赖它。

---

## 10. Push 权限与保护分支

**允许直接 push `main` 的唯一场景**：

- 变更范围**仅限** `Memory/<自己的名字>/` 目录内。

**其余情况一律走 PR。**

`main` 建议开启分支保护：**禁止 force push**、禁止删除、必须 PR。

---

## 11. 分支使用规范

| 用途 | 分支名 |
|---|---|
| 个人记忆（直接推 main，不必建分支） | — |
| 修改技能 | `skill/<名字>` |
| 新增技能 | `add-skill/<名字>` |
| 顶层文档 / 设计文档 | `docs/<名字>` |
| 治理脚本 / 看板 | `tooling/<名字>` |

---

## 12. 网络与超时设置

- 若你的 Git 远端走隧道 / 反代 / 家宽上行，**首次 clone 可能很慢**，不要中断。
- 建议的 git 全局配置：

```bash
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999
```

- **对不可靠的链路，务必显式设置超时**（例如 SSH 的 `ConnectTimeout=120`、`ServerAliveInterval=20`），
  否则你会得到一堆「看起来是认证失败、其实是超时」的假错误。

详见 `04RemoteAccess.md`。

---

## 13. Agent 身份与署名

### 13.1 名单由你定义

本仓库**不预设任何 Agent 名单**。请在你自己的 fork 里，把下面这张表填成你真实使用的 Agent：

| 标准名（一字不差） | 记忆目录 | 说明 |
|---|---|---|
| `<AgentName>` | `Memory/<AgentName>/` | 例如 `ClaudeCode` |
| `<AgentName>` | `Memory/<AgentName>/` | 例如 `Codex` |

**约束**：

- 名字必须 **PascalCase**，无空格、无连字符；
- **commit 署名、`Agent:` trailer、记忆目录名，三者必须完全一致**；
- 新增一个 Agent = 新增一个目录 + 一个署名，**不需要修改协议本身**。

### 13.2 凭据

- 每个 Agent 使用**独立凭据**，**绝不共用**。
- 凭据保存在仓库**之外**，通过系统的凭据管理器或环境变量注入。
- **绝不写入仓库**（见第 17 条）。

---

## 14. 禁止事项

1. ❌ 写入任何密钥（token / 密码 / API Key / 私钥）。
2. ❌ 删除、修改其他 Agent 的 `Memory/` 目录。
3. ❌ 直接 push 到 `main` 修改 `Skills/`、`docs/` 或顶层文档。
4. ❌ force push、删除分支、改写公共历史。
5. ❌ 入库大文件或二进制产物。
6. ❌ 在 commit message / issue / PR 里粘贴密钥。
7. ❌ 把「一份记忆」同时放进两个 Agent 的目录（那是复制，不是共享——共享的正确做法是提取成 `Skills/` 或顶层文档）。

---

## 15. 冲突处理与容错机制

- 冲突时**优先保留双方内容**，不要粗暴覆盖。
- 解决后必须在自己的 Memory 里记录。
- **硬性要求**：任何时候都不允许以「解决冲突」为名丢弃别人的数据。
- 记忆类文件的冲突通常意味着**两个 Agent 都做了值得保留的补充**，合并的逻辑比重写更常正确。

---

## 16. 特殊场景处理

| 场景 | 做法 |
|---|---|
| 需要改顶层文档 | 走 `docs/<名字>` 分支 + PR |
| 发现上游技能有更新 | 提请维护者统一同步，不要自己改上游目录 |
| 想新增技能 | `add-skill/<名字>` + PR |
| 想给某个记忆换位置 | 走 PR，并在 PR 描述里说明迁移原因 |
| 仓库变慢 / 变大 | 见第 7、19 条；用审计脚本定位（`Scripts/audit.sh`） |
| 误提交了密钥 | **立即**吊销并更换，然后清理历史——只 `git rm` 是不够的 |

---

## 17. 密钥与安全

**任何密钥、token、密码、私钥都严禁进入仓库。这是本协议最硬的一条。**

- 凭据清单（只列字段名）见 `05Secrets.example.md`。
- 真实值由本人保管；需要时当面/私聊索取，拿到后放在**仓库之外**。
- 一旦误提交：立即吊销 → 更换 → 清理历史（`git filter-repo` 或直接重建仓库）。**吊销永远排在清理前面**。
- 公开仓库里，`Memory/` 就是公开的。**请按「假设它会被人看到」来写。**

---

## 18. 动态调整机制

本协议可以演进，但：

- 任何 Agent **不得单方面修改本文件**；
- 变更必须走 PR，并由**人类**确认后合并；
- 重大变更请在提交信息里说明动机与影响范围。

---

## 19. 自动化维护机制（维护者可替换）

仓库维护者（Orchestrator）负责：

1. **Memory Review**：定期检查各 Agent 的记忆目录是否符合规范。
2. **Skill Review**：审阅 `Skills/` 的 PR。
3. **Consistency Check**：校验命名规范、`Agent:` trailer、密钥泄露。
4. **Git Audit**：检查分支保护、异常推送、仓库体积。
5. **Upstream Sync**：如维护通用技能库，定期同步快照。

**关键约束**：维护者是一个**可替换的角色**，不是某个特定 Agent。

它可以由任何具备「执行命令 + 定时任务 + 操作 Git」能力的 Agent 担任，
也可以由 **CI（例如 GitHub Actions）** 直接担任——本仓库的 `Scripts/` 与
`.github/workflows/` 就是为此准备的。

详见 `docs/Orchestrator.md`。

---

## 20. 启动检查清单（每个 Agent 首次接入时执行）

- [ ] clone 本仓库到本地固定路径
- [ ] `git pull --rebase` 成功
- [ ] 确认自己的标准名，`Memory/<AgentName>/` 存在（不存在则创建）
- [ ] 设置该机器的 commit 身份（`user.name` / `user.email`）
- [ ] 配置该 Agent 的**专属**凭据（存在仓库外）
- [ ] 读一遍 `00StartHere.md`
- [ ] 知道 `Index.md` / `SkillsList.md` 在哪，以及**按需加载**的纪律
- [ ] 知道密钥不入库、真实值放在哪里
- [ ] 完成第一次提交，格式正确（首行署名 + `Agent:` trailer）

---

## 📞 遇到问题

先查 `Index.md` 与相关 `SKILL.md`；查不到，再问仓库的所有者（人类）。

**不要猜。**在一个多 Agent 仓库里，一次基于猜测的写入，代价可能是别人的一整天。

---

_本协议由仓库所有者制定。MindMesh 提供架构与措辞，具体名单、路径、远端由你填写。_
