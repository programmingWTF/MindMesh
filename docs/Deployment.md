# 部署

> 有三种形态，**从你实际有什么出发，不要一步到位。**

---

## 形态 ①：单人（一个 GitHub 仓库）

**你需要**：一个 GitHub 账号。

```bash
# 1. 在 GitHub 上创建仓库（建议先设 private）
# 2. 克隆
git clone git@github.com:<you>/<repo>.git
cd <repo>

# 3. 给第一个 Agent 建记忆目录
mkdir -p Memory/ClaudeCode && touch Memory/ClaudeCode/.gitkeep

# 4. 配置提交身份
git config user.name "ClaudeCode"
git config user.email "<你的邮箱>"

# 5. 第一次提交
git add -A && git commit -m "ClaudeCode: 初始化

Agent: ClaudeCode"
git push
```

**完成。**没有服务器、没有域名、没有 Docker。

---

## 形态 ②：多 Agent 共用

在上面的基础上：

1. **每个 Agent 一个目录**：`Memory/ClaudeCode/`、`Memory/Codex/`、`Memory/Cursor/`……
2. **每个 Agent 一份独立凭据**（不要共用同一个 token——出问题时无法单独吊销）。
3. **在 `AGENTS.md` 第 13 条登记名单**，让所有 Agent 知道彼此的名字。
4. **打开分支保护**：`main` 禁止 force push、要求 PR。
5. **把入口贴给每个 Agent**：仓库根 `AGENTS.md` + `00StartHere.md`，
   或直接用 `Prompts/Bootstrap.md`。

### 让 Agent 自己完成接入

把 `Prompts/Bootstrap.md` 整段丢给它，它会自己 clone、建目录、配身份、读协议、做第一次提交。

---

## 形态 ③：自建（有常驻机器）

**你多得到的是**：私有远端、看板、定时自检、离线可用。

### 3.1 私有 Git 远端

任何支持 HTTP(S) 或 SSH 的 Git 服务都可以（Gitea / Forgejo / GitLab / 甚至裸仓库 + SSH）。

> **建议直连，不要绕公网代理**——代理会给你的 `git push` 加上一层不透明的超时与限速。
> 如果你的机器只有家宽上行，第一次 clone 会很慢，**不要中断**。

推荐配置：

```bash
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999
```

### 3.2 定时自检

把 `Scripts/audit.sh` 挂到 cron / systemd timer：

```bash
# 每周一 09:00
0 9 * * 1 cd /path/to/repo && bash Scripts/audit.sh >> /path/to/logs/audit.log 2>&1
```

**没有常驻机器？** 用 GitHub Actions 替代，效果一样，且免费：

```yaml
# .github/workflows/audit.yml
name: audit
on:
  schedule: [{ cron: "0 1 * * 1" }]
  workflow_dispatch:
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: bash Scripts/audit.sh
```

### 3.3 看板

见 `docs/Dashboard.md`。

### 3.4 通知

`Scripts/notify.sh` 支持三种输出：**stdout / webhook / SMTP**。
选一个，把它挂到审计脚本后面。

---

## 多机 / 多用户

| 场景 | 做法 |
|---|---|
| 同一台机器、多个 Agent | 各自 `Memory/<Name>/`，各自 commit 身份 |
| 多台机器 | 各自 clone，靠 pull/push 同步；**冲突靠单写者分区避免** |
| 多人协作 | 每人一组 Agent；**不要共用凭据**；PR 审阅人写清楚 |
| 需要离线 | 私有远端 + 本地 clone；定期 push |

---

## 迁移与备份

- **备份**：任何 clone 都 是完整备份（`git clone --mirror` 是更稳的镜像）。
- **迁移远端**：`git remote set-url origin <新地址>`，然后 `git push --mirror`。
- **重建仓库**（历史里混进了密钥时）：新开一个仓库，把**当前状态**提交为第一个 commit。

> **吊销密钥永远排在清理历史之前。**
