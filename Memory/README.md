# Memory/

这里存放**每个 Agent 的私有记忆**。

```text
Memory/
├── README.md         本文件
├── <AgentName>/      ← 只有这个 Agent 能写
└── <OtherAgent>/     ← 只有那个 Agent 能写
```

## 规则（协议第 4 条）

- **目录名 = Agent 的名字**，一字不差，PascalCase。
- **你只能写自己的目录。**别人的目录**只读**。
- 修改别人的目录**必须**走 PR，并由人类或维护者确认。

## 为什么这样划

**单写者分区**是整套设计里最关键的一条：它把「多个写入者改同一份数据」这个经典问题，
变成了物理上不可能发生的事。

代价是：**跨 Agent 共享的内容必须显式提取**到 `Skills/` 或顶层文档。
这不是缺点——它迫使你思考「这条信息到底该属于谁」。

## 新建一个 Agent

```bash
mkdir -p Memory/<AgentName>
touch Memory/<AgentName>/.gitkeep
```

然后在 `AGENTS.md` 第 13 条登记它（**走 PR**）。

## 建议的组织方式

```text
Memory/<AgentName>/
├── README.md                 我是谁、我在哪、我的记忆怎么组织
├── Memory.md                 当前活跃状态（会话开始时读这个）
├── Learnings.md              犯过的错 + 正确做法
├── Daily/
│   └── YYYY-MM-DD.md         当天发生的事
└── Reference-<领域>.md       某个领域的细节
```

## ⚠️ 这里的隐私

**如果是公开仓库，`Memory/` 就是公开的。**

- 不要放密钥（协议第 17 条）；
- 不要放你不希望任何人看到的内容；
- 涉及他人的信息要克制——**你无权替别人决定他们的信息该存在哪里**。

需要私密记忆 → 用 private 仓库，或把敏感内容拆到仓库外。
