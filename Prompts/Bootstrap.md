# Prompts / Bootstrap.md — 让一个全新 Agent 接入

> **用法**：把下面分隔线之间的内容整段复制给一个全新的 Agent。
> 把 `<尖括号>` 里的值替换成你的实际信息。

---

你是这个仓库的新成员。请严格按顺序完成接入，**不要跳步，不要一次读多个文件**。

## 环境

- 仓库地址：`<git@github.com:you/repo.git>`
- 本地路径：`<~/repo 或 D:\\path\\repo>`
- **你的名字**：`<AgentName>`（PascalCase，一字不差）
- 你的提交署名：`<同上>`

## 步骤

1. **同步**——这是第一件事，哪怕你只是要读文件：
   ```bash
   cd <本地路径>
   git pull --rebase
   ```

2. **读协议**：完整读仓库根的 `AGENTS.md`。它是唯一权威。
   同时读 `00StartHere.md`。

3. **认领你的记忆目录**：
   ```bash
   mkdir -p Memory/<AgentName> && touch Memory/<AgentName>/.gitkeep
   ```
   确认 `AGENTS.md` 第 13 条里已经有你的名字；没有就告诉我，我来加。

4. **配置提交身份**（仅本仓库）：
   ```bash
   git config user.name "<AgentName>"
   git config user.email "<你的邮箱>"
   ```

5. **体检本机**：
   ```bash
   bash Scripts/check-env.sh
   ```
   把结论写进 `01Environment.md`（**只写事实**，没有的写「未安装」，不要猜）。

6. **建索引**：在 `Memory/<AgentName>/README.md` 里写下：
   - 你是谁、你在哪台机器上运行、你的主要用途；
   - 你的记忆文件组织方式。

7. **第一次提交**：
   ```bash
   git add -A Memory/<AgentName> 01Environment.md
   git commit -m "<AgentName>: 初始化接入

Agent: <AgentName>"
   git push
   ```

## 约束（违反这些就停下来问我）

- 你**只能写** `Memory/<AgentName>/` 和 `01Environment.md`（后者走 PR 更稳妥）；其余全部只读。
- **绝对不要**把任何密钥、token、密码写进仓库。
- **不要** force push，**不要**改写历史，**不要**删除别人的文件。
- **不要** `ls -R`，**不要**一次 `cat` 多个文件。

## 完成后回报

用三句话告诉我：你读懂了什么、你做了什么改动、你有什么不确定的地方。
