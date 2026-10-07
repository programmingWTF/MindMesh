# 维护者（Orchestrator）

> 仓库需要一个「定期照看它」的角色。**但不需要是某个特定的 Agent。**

---

## 维护者做什么

| 职责 | 对应 |
|---|---|
| 记忆规范检查 | `Scripts/audit.sh` |
| 密钥泄漏扫描 | `Scripts/leakscan.sh` |
| 技能 PR 审阅 | `gh pr review` |
| 命名 / `Agent:` trailer 一致性 | `Scripts/audit.sh` |
| 仓库体积与分支保护 | `gh api` / 仓库设置 |
| 上游技能同步（如有） | 低频整块提交 |

输出应当是一份**报告**，而不是一堆静默的改动。

---

## 谁可以当维护者

**唯一的要求是三个能力：**

1. 能**执行 shell 命令**（跑 `Scripts/` 里的脚本）；
2. 能做**定时 / 周期任务**；
3. 能**操作 Git**（提交、开 PR、合并、读 API）。

满足这三条的候选，按「越省事越好」排序：

| 候选 | 定时能力 | 说明 |
|---|---|---|
| **CI（GitHub Actions）** | `schedule` | **最省事**。不需要 Agent，不需要机器，零成本 |
| 你已有的任何 Agent | 平台自带心跳 / cron | 只要它能定时醒来自查一次 |
| 自建脚本 + crontab | 原生 | 完全可控 |
| 一个专门的小 Agent | 平台心跳 | 想要自然语言报告时 |

> ⚠️ **不要默认「必须是某个最贵的 Agent」来当维护者。**
> 维护工作是**规则明确的例行检查**，它适合交给最便宜、最稳定的执行者。
> 把贵的 token 花在判断上，不要花在「跑脚本然后读输出」上。

---

## 参考实现：GitHub Actions

```yaml
# .github/workflows/audit.yml
name: audit

on:
  schedule: [{ cron: "0 1 * * 1" }]
  workflow_dispatch:

permissions:
  contents: read
  issues: write

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - run: bash Scripts/audit.sh > /tmp/audit.md || true
      - run: cat /tmp/audit.md >> $GITHUB_STEP_SUMMARY
```

> `fetch-depth: 0` 是必要的——审计要读提交历史。默认的浅克隆会让「活跃度统计」全部变成 0。

---

## 参考实现：cron

```bash
0 9 * * 1 cd /path/to/repo && git pull --rebase -q && bash Scripts/audit.sh >> logs/audit.log 2>&1
```

---

## 拆分职责：不要让一个 Agent 既当运动员又当裁判

| 角色 | 权限 |
|---|---|
| 普通 Agent | 只写自己的 `Memory/` |
| 维护者 | 审 PR、合并、跑审计、改 `Scripts/` |
| **人类** | 改 `AGENTS.md`、改权限、决定谁能当维护者 |

**`AGENTS.md` 只能由人类改**（协议第 18 条）。
维护者可以让协议**被更好地执行**，但不能**自己改写规则**。

> 如果只有一个 Agent 可用，它也可以兼任维护者——
> 但要接受这个事实：**它审的是自己。**此时审计脚本的自动化程度就是你的安全边际。

---

## 换维护者时要交接什么

- [ ] 远端地址与凭据（用**新的**独立凭据，不要复制旧的）
- [ ] 定时任务的位置（cron / Actions / 平台心跳）
- [ ] 通知通道
- [ ] 当前已知问题列表（写在 `Memory/<旧维护者>/` 里，**不要靠口头交接**）
