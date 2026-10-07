---
name: mindmesh-github
description: 用 gh CLI 操作 GitHub：issue、PR、评审、合并、分支保护、仓库设置。当需要开 PR、审 PR、合并、看 issue、批量操作仓库时使用。
---

# GitHub 协作

## 前置

```bash
gh auth status          # 确认登录的身份
gh auth switch          # 切换账号
```

> ⚠️ **确认当前身份**。多账号时，用错身份会产生「明明有权限却 403」这类假故障。

## 常用

```bash
# 仓库
gh repo view --json name,visibility,defaultBranchRef
gh repo clone <owner>/<repo>

# Issue
gh issue list --state open --limit 20
gh issue create --title "..." --body-file body.md

# PR
gh pr create --fill --base main --head <branch>
gh pr list --state open
gh pr view <n>
gh pr diff <n>
gh pr review <n> --comment --body "..."
gh pr checks <n>
```

## 改文件的标准流程（**不要直接推 main**）

```bash
git pull --rebase
git checkout -b docs/<名字>
# ...改文件...
git add <文件>
git commit -m "docs: <说明>

Agent: <我的名字>"
git push -u origin docs/<名字>
gh pr create --fill
```

## 合并

```bash
gh pr merge <n> --squash --delete-branch
```

**失败路径：**

| 症状 | 真实原因 | 做法 |
|---|---|---|
| `405 Method Not Allowed` | 常见于**受保护分支**，未必是你没权限 | 改用 `gh api` 的 GraphQL `mergePullRequest`，或让维护者合并 |
| `Pull request is not mergeable` | 有冲突 / 检查未过 | `gh pr checks` + 本地 `git pull --rebase` 解决 |
| 不能 approve 自己的 PR | 平台限制：作者不能自审 | 换另一个有权限的身份审，或走维护者 |
| `403` 但账号有权限 | 是**当前激活的账号**不对 | `gh auth switch` |

## 合并前检查清单

- [ ] PR 只改了它声称要改的东西（`gh pr diff`）
- [ ] 没有密钥、没有大文件
- [ ] 命名符合规范（PascalCase）
- [ ] 涉及 `AGENTS.md` 的改动**必须由人类确认**

## 验证

```bash
gh pr view <n> --json state,mergedAt,mergeCommit
```
