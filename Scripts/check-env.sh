#!/usr/bin/env bash
# check-env.sh — 本机体检：已装什么、版本多少、缺什么
#
# 用法: bash Scripts/check-env.sh
# 输出会被 Agent 写进 01Environment.md（只写事实，不要猜）
set -uo pipefail

printf '# 本机环境体检 %s\n\n' "$(date '+%Y-%m-%d %H:%M')"

printf '## 系统\n\n'
printf '| 项 | 值 |\n|---|---|\n'
printf '| 主机名 | %s |\n' "$(hostname 2>/dev/null || echo '?')"
printf '| 系统 | %s |\n' "$(uname -s 2>/dev/null || echo '?')"
printf '| 内核 | %s |\n' "$(uname -r 2>/dev/null || echo '?')"
printf '| 架构 | %s |\n' "$(uname -m 2>/dev/null || echo '?')"
printf '| Shell | %s |\n' "${SHELL:-?}"
printf '\n'

printf '## 工具\n\n'
printf '| 工具 | 状态 | 版本 |\n|---|---|---|\n'
check() {
  local name="$1" cmd="$2" ver="$3"
  if command -v "$cmd" >/dev/null 2>&1; then
    local v
    v="$(eval "$ver" 2>/dev/null | head -1)"
    printf '| %s | ✅ | %s |\n' "$name" "$v"
  else
    printf '| %s | ❌ | — |\n' "$name"
  fi
}

check git       git      'git --version'
check node      node     'node --version'
check npm       npm      'npm --version'
check python3   python3  'python3 --version'
check pip3      pip3     'pip3 --version'
check docker    docker   'docker --version'
check gh        gh       'gh --version'
check jq        jq       'jq --version'
check rg        rg       'rg --version'
check curl      curl     'curl --version'
check ssh       ssh      'ssh -V'
check tmux      tmux     'tmux -V'
check ffmpeg    ffmpeg   'ffmpeg -version'
printf '\n'

printf '## 磁盘\n\n'
printf '```text\n'
df -h . 2>/dev/null | tail -2 || echo '(不可用)'
printf '```\n\n'

printf '## 结论\n\n'
printf '> 请把上表中标 ❌ 且**确实需要**的项，单独列在这里，并写明用途。\n'
printf '> 其余的空着——**不要为了完整而安装。**\n'
