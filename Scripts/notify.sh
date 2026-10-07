#!/usr/bin/env bash
# notify.sh — 把一份报告送到你的眼前
#
# 用法:
#   bash Scripts/notify.sh <文件或"-">                    # stdout（默认）
#   bash Scripts/notify.sh <文件> --webhook <URL>         # POST 到 webhook
#   bash Scripts/notify.sh <文件> --smtp <收件人>          # 发邮件
#   bash Scripts/notify.sh <文件> --issue <owner/repo>    # 开一个 GitHub Issue
#
# 凭据一律从环境变量读，绝不写进本文件。
set -uo pipefail

INPUT="${1:-"-"}"
MODE="stdout"
TARGET=""
[ "${2:-}" = "--webhook" ] && MODE="webhook" && TARGET="${3:-}"
[ "${2:-}" = "--smtp" ]    && MODE="smtp"    && TARGET="${3:-}"
[ "${2:-}" = "--issue" ]   && MODE="issue"   && TARGET="${3:-}"

if [ "$INPUT" = "-" ]; then BODY="$(cat)"; else BODY="$(cat "$INPUT")"; fi
SUBJECT="[MindMesh] 维护报告 $(date '+%Y-%m-%d')"

case "$MODE" in
  stdout)
    printf '%s\n' "$SUBJECT"
    printf '%s\n' "$BODY"
    ;;

  webhook)
    [ -z "$TARGET" ] && { echo "缺少 webhook URL" >&2; exit 2; }
    # 兼容 Slack / Discord / 飞书 的常见字段
    curl -sS -m 30 -X POST "$TARGET" \
      -H 'Content-Type: application/json' \
      --data-binary "$(printf '%s' "$BODY" | python3 -c 'import json,sys; print(json.dumps({"text": sys.stdin.read()}))')" \
      && echo "✅ webhook 已发送"
    ;;

  smtp)
    [ -z "$TARGET" ] && { echo "缺少收件人" >&2; exit 2; }
    # 推荐用 msmtp / swaks / 平台自带发信工具，凭据放 ~/.msmtprc (chmod 600)
    if command -v msmtp >/dev/null 2>&1; then
      printf 'To: %s\nSubject: %s\nContent-Type: text/plain; charset=utf-8\n\n' "$TARGET" "$SUBJECT" \
        | cat - <(printf '%s\n' "$BODY") | msmtp "$TARGET" && echo "✅ 邮件已发送"
    else
      echo "未安装 msmtp；请自行换成你的发信方式（见 Skills/Email/SKILL.md）" >&2
      exit 3
    fi
    ;;

  issue)
    [ -z "$TARGET" ] && { echo "缺少 owner/repo" >&2; exit 2; }
    if command -v gh >/dev/null 2>&1; then
      TMP="$(mktemp)"; printf '%s\n' "$BODY" > "$TMP"
      gh issue create --repo "$TARGET" --title "$SUBJECT" --body-file "$TMP" && echo "✅ Issue 已创建"
      rm -f "$TMP"
    else
      echo "未安装 gh" >&2; exit 3
    fi
    ;;

  *)
    echo "未知模式: $MODE" >&2
    echo "用法: notify.sh <文件或-> [--webhook URL | --smtp 收件人 | --issue owner/repo]" >&2
    exit 2
    ;;
esac
