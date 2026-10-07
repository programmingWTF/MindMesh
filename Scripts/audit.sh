#!/usr/bin/env bash
# audit.sh — MindMesh 治理审计
#
# 用法:
#   bash Scripts/audit.sh              # 打印到 stdout
#   bash Scripts/audit.sh > report.md  # 存成报告
#
# 只读：本脚本不修改仓库、不提交、不推送。
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT" || exit 1

AGENT_NAMES_FILE="AGENTS.md"
OUT=""

say() { OUT="$OUT$1
"; }

say "# 维护报告 $(date '+%Y-%m-%d %H:%M')"
say ""
say "仓库: $(git config --get remote.origin.url 2>/dev/null | sed -E 's#//[^@/]+@#//#' || echo '(无远端)')"
say "分支: $(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
say ""

# ── 1. 密钥泄漏扫描 ────────────────────────────────────────────
say "## 1. 密钥泄漏扫描"
LEAKS="$(grep -rInE --include='*.md' --include='*.sh' --include='*.py' --include='*.json' --include='*.yml' --include='*.yaml' \
  'gh[porsu]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|re_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----' . 2>/dev/null \
  | grep -v '^./Scripts/leakscan.sh:' | grep -v '\*\*\*' | head -20)"
if [ -n "$LEAKS" ]; then
  say "  🔴 **发现可疑密钥，请立即处理：**"
  say "```text"
  say "$LEAKS"
  say "```"
else
  say "  ✅ 未发现明显密钥模式"
fi
say ""

# ── 2. 命名规范（受管区域应为 PascalCase） ─────────────────────
say "## 2. 命名规范检查"
BAD="$(git ls-files \
  | grep -vE '^Dashboard/static/' \
  | grep -E '\.(md|sh|py|json|ya?ml)$' \
  | grep -vE '(^|/)(AGENTS|CLAUDE|SKILL|README|LICENSE|NOTICE)\.md$' \
  | grep -vE '/?[0-9]{4}-[0-9]{2}-[0-9]{2}' \
  | grep -E '[a-z]-[a-z]|_' | head -20)"
if [ -n "$BAD" ]; then
  say "  以下文件不符合 PascalCase（若是有意为之可忽略）："
  say "```text"
  say "$BAD"
  say "```"
else
  say "  ✅ 全部符合"
fi
say ""

# ── 3. 提交规范 ────────────────────────────────────────────────
say "## 3. 提交规范（Agent: trailer）"
TOTAL="$(git log -50 --format='%H' 2>/dev/null | wc -l | tr -d ' ')"
WITH="$(git log -50 --format='%B%x00' 2>/dev/null | tr '\0' '\n' | grep -c '^Agent: ' || true)"
say "  最近 50 条提交中，含 \`Agent: \` trailer 的：$WITH / $TOTAL"
if [ "$TOTAL" -gt 0 ] && [ "$WITH" -lt "$TOTAL" ]; then
  say "  ⚠️ 有条目缺少 trailer——活动看板与责任追溯会漏掉它们"
fi
say ""
say "### 最近 10 条提交"
say "```text"
say "$(git log -10 --format='  %h %ad %s' --date=short 2>/dev/null)"
say "```"
say ""

# ── 4. 仓库体积 ────────────────────────────────────────────────
say "## 4. 仓库体积"
say "```text"
say "  工作区: $(du -sh . 2>/dev/null | cut -f1)"
say "  .git  : $(du -sh .git 2>/dev/null | cut -f1)"
say "  受管文件数: $(git ls-files | wc -l | tr -d ' ')"
say "```"
BIG="$(git ls-files -z | xargs -0 du -h 2>/dev/null | sort -rh | head -5)"
say "  最大的 5 个受管文件："
say "```text"
say "$BIG"
say "```"
say ""

# ── 5. 各 Agent 活跃度 ─────────────────────────────────────────
say "## 5. 各 Agent 记忆活跃度"
say ""
say "| Agent | 提交数 | 目录体积 | 最近提交 |"
say "|---|---|---|---|"
if [ -d Memory ]; then
  for d in Memory/*/; do
    [ -d "$d" ] || continue
    n="$(basename "$d")"
    c="$(git log --oneline -- "$d" 2>/dev/null | wc -l | tr -d ' ')"
    sz="$(du -sh "$d" 2>/dev/null | cut -f1)"
    last="$(git log -1 --format='%ad' --date=short -- "$d" 2>/dev/null)"
    say "| $n | $c | $sz | $last |"
  done
else
  say "| （无 Memory 目录） | | | |"
fi
say ""

# ── 6. 待办提示 ────────────────────────────────────────────────
say "## 6. 需要人类决定的事"
say ""
say "- [ ] 检查是否有待审的技能 PR"
say "- [ ] 确认 main 分支保护仍然开启（禁止 force push）"
say "- [ ] 确认没有人的凭据需要轮换"
say ""

printf '%s' "$OUT"
