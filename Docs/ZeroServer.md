# 零服务器方案

> **你只需要一个 Git 远端。GitHub 就够了。**
> 没有服务器、没有域名、没有 Docker、没有任何要维护的东西。

---

## 为什么这很重要

大多数「多 Agent 共享上下文」的方案，第一步就要求你：

部署一个服务 → 配一个数据库 → 建一个索引 → 开一个端口 → 搞一个域名……

**在你还只有两个 Agent 的时候，这就是劝退。**

MindMesh 的第一个形态刻意做成**零服务**：
远端用 GitHub，前端用 GitHub 自带的页面，定时任务用 GitHub Actions。

---

## 组成对照

| 自建方案里的东西 | 零服务器替代 |
|---|---|
| 私有 Git 服务 | **GitHub 仓库** |
| 前端网站 / 看板 | **GitHub 仓库页面本身** |
| 定时任务（cron / systemd） | **GitHub Actions** |
| 通知（邮件 / webhook） | **Actions 的输出 / Issue / 通知** |
| 域名 + 反代 + 鉴权 | **不需要**（GitHub 自带权限） |

---

## 一、远端：GitHub

```bash
git init -b main
git remote add origin git@github.com:<you>/<repo>.git
git push -u origin main
```

- **private**：个人记忆放这里。`Memory/` 只有你能看。
- **public**：只放你想公开的（技能、模板、文档）。**不要把私密记忆放进来。**

> ⚠️ GitHub 有自己的限制（仓库大小、LFS 配额、Actions 分钟数）。
> 记忆是文本，通常远远够用。**不要把二进制大文件塞进来。**

---

## 二、前端：GitHub 页面本身

你**不需要**自己写看板。GitHub 已经是：

| 你想要的 | GitHub 给的 |
|---|---|
| 看谁改了什么 | `Commits` |
| 看某个 Agent 的活跃度 | `Insights → Contributors` |
| 按目录浏览记忆 | 仓库文件树（天然按 `Memory/<Agent>/` 分区） |
| 读 Markdown | 自动渲染（表格、代码块、折叠都能看） |
| 追一个决定 | `Blame` / `History` |
| 让别人提改动 | `Pull Request`（自带评审与讨论） |
| 自动化 | `Actions` |

**换句话说：GitHub 就是一个已经建好的看板。**
`Dashboard/` 里那份自托管看板，是给「想自己控制 UI」或「私有远端没有 Web 界面」的人用的。

---

## 三、定时任务：GitHub Actions

```yaml
# .github/workflows/audit.yml
name: audit

on:
  schedule:
    - cron: "0 1 * * 1"   # 每周一 01:00 UTC
  workflow_dispatch:

permissions:
  contents: read
  issues: write

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run audit
        run: bash Scripts/audit.sh | tee audit.md
      - name: Report
        run: |
          echo "## Audit $(date -u +%F)" >> $GITHUB_STEP_SUMMARY
          cat audit.md >> $GITHUB_STEP_SUMMARY
```

- `GITHUB_STEP_SUMMARY` 会把报告渲染在 Actions 页面上；
- 想让「维护者 Agent」也参与，见 `Docs/Orchestrator.md`。

### 密钥怎么办

用 `Repository secrets`（`Settings → Secrets and variables → Actions`），
在 workflow 里以环境变量注入。**永远不要写进仓库。**

---

## 四、通知

没有邮件服务器也没关系，按可得性排序：

| 方式 | 做法 |
|---|---|
| 无 | Actions 的 step summary（零配置） |
| Issue | 用 `gh issue create` 把报告变成一条待办（**天然有历史、有归档**） |
| Webhook | `Scripts/notify.sh <url>` 打到你的 IM / 机器人 |
| 邮件 | `Scripts/notify.sh --smtp`（需要 SMTP 凭据，放 secrets） |

> **Issue 是最被低估的一种通知**：它自动获得了「已读/未读、谁在处理、什么时候关的」这些状态。

---

## 五、什么时候你才真的需要一个服务器

出现下面任意一条，再考虑升级：

- 记忆里有很多**大文件**（超过托管服务的限额）；
- 你需要在**没有公网**的环境里同步；
- 你要把看板**发布给不特定的人**（需要自己的鉴权）；
- 你需要的定时任务**频率/时长**超过免费额度；
- 你想统一管理 **多个仓库**的上下文。

**在那之前，GitHub 就够了。**
