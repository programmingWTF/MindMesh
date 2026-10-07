#!/usr/bin/env bash
# sync.sh — 记忆同步：提交本地 → 拉取远端 → 推送
#
# 用法: bash Scripts/sync.sh <AgentName>
#
# 设计要点（吃过亏的地方）:
#   即使本地没有改动，也必须 pull —— 否则永远拿不到别人推的提交。
set -uo pipefail

AGENT="${1:-}"
if [ -z "$AGENT" ]; then
  echo "用法: bash Scripts/sync.sh <AgentName>" >&2
  exit 2
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT" || exit 1

DIR="Memory/$AGENT"
if [ ! -d "$DIR" ]; then
  echo "🔴 目录不存在: $DIR" >&2
  echo "   你是这个仓库的成员吗？名字是否正确（PascalCase）？" >&2
  exit 3
fi

# 1) 提交本地改动（只提交自己的目录）
git add -A "$DIR" >/dev/null 2>&1
if ! git diff --cached --quiet; then
  STAMP="$(date '+%Y-%m-%d %H:%M')"
  git commit -q -m "$AGENT: 记忆自动同步 $STAMP

Agent: $AGENT" && echo "✅ 已提交 $STAMP"
else
  echo "· 本地无改动"
fi

# 2) 关键：无论有没有改动都拉取
if git pull --rebase --autostash -q origin main 2>/dev/null; then
  echo "✅ 已拉取远端"
else
  echo "⚠️ 拉取失败——可能有冲突。请手动处理，**不要**丢弃别人的内容。" >&2
fi

# 3) 有领先则推送
AHEAD="$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)"
if [ "$AHEAD" -gt 0 ]; then
  if git push -q origin main 2>/dev/null; then
    echo "✅ 已推送 $AHEAD 条提交"
  else
    echo "⚠️ 推送失败" >&2
    exit 4
  fi
fi
exit 0
