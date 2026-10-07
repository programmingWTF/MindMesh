#!/usr/bin/env bash
# leakscan.sh — 提交前的密钥兜底扫描
#
# 用法:
#   bash Scripts/leakscan.sh          # 扫工作区
#   bash Scripts/leakscan.sh --staged # 只扫 staged（适合放进 pre-commit）
#
# 退出码: 0 = 干净, 1 = 发现可疑内容
#
# ⚠️ 它只能抓「长得像密钥」的东西。写进普通文本的密码它抓不到。
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT" || exit 1

PATTERNS='gh[porsu]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|re_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|xox[baprs]-[0-9A-Za-z-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}'

if [ "${1:-}" = "--staged" ]; then
  # 只检查暂存区里新增/修改的行
  FOUND="$(git diff --cached -U0 | grep -E '^\+' | grep -vE '^\+\+\+' | grep -InE "$PATTERNS" | head -20)"
  SCOPE="暂存区"
else
  FOUND="$(grep -rInE --binary-files=without-match \
    --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=secret \
    --exclude='leakscan.sh' \
    "$PATTERNS" . 2>/dev/null | head -20)"
  SCOPE="工作区"
fi

if [ -n "$FOUND" ]; then
  echo "🔴 $SCOPE 中发现可疑密钥："
  echo
  printf '%s\n' "$FOUND" | sed -E 's/([A-Za-z0-9_-]{6})[A-Za-z0-9_-]{10,}/\1…<redacted>/g'
  echo
  echo "处理顺序（不能颠倒）："
  echo "  1. 先吊销 / 更换这个密钥（此刻起旧值就是废的）"
  echo "  2. 再清理仓库历史（git filter-repo，或重建仓库）"
  echo "  3. 通知所有使用者"
  echo
  exit 1
fi

echo "✅ $SCOPE 未发现可疑密钥模式"
exit 0
