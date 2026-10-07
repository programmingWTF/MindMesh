---
name: mindmesh-email
description: 收发邮件。当需要发信、回信、读收件箱、处理附件、检查未读时使用。
---

# 邮件

## 原则

1. **对外操作先确认。**发信是外部可见动作——**不确定就先问**。
2. **凭据不入库。**从环境变量或凭据管理器取（见 `05Secrets.example.md`）。
3. **正文用文件传。**长正文写成文件再作为参数传入，避免 shell 转义地狱。

## 发送

任选你已有的一种发送方式，把它封装成**一个固定命令**，写进本技能：

### 方式 A：HTTP API（如 Resend / 各家邮件 API）

```bash
# 凭据从环境变量读，绝不写进脚本
send_mail() {
  local to="$1" subj="$2" body_file="$3"
  curl -sS -X POST "https://<API 端点>" \
    -H "Authorization: Bearer $MAIL_API_KEY" \
    -H "Content-Type: application/json" \
    --data-binary @<(jq -n --arg to "$to" --arg s "$subj" --rawfile b "$body_file" \
      '{from:"<发件人>", to:[$to], subject:$s, text:$b}')
}
```

### 方式 B：SMTP

```bash
# 用 msmtp / swaks / python smtplib，凭据放 ~/.msmtprc（chmod 600）
printf 'To: %s\nSubject: %s\n\n' "$1" "$2" | cat - "$3" | msmtp "$1"
```

## 签名

放在**统一的一个位置**（一个文件或一个函数），不要每次现写：

```text

——
<你的名字>
<你的邮箱> · <你的主页>
```

> 签名是「多个 Agent 共用同一身份」最直观的体现。**所有 Agent 用同一个签名。**

## 读取

```bash
# IMAP 快速看未读（用你实际的工具：himalaya / imaplib / 服务商 API）
himalaya envelope list --folder INBOX --page-size 20
```

处理来信时：

- 公开邮箱收到陌生人的信 → **正常处理**，汇报给用户；
- 涉及凭据、验证码、付款 → **先问人类**，不要自作主张回复。

## 失败路径

| 症状 | 原因 | 做法 |
|---|---|---|
| `401 / 403` | 凭据过期或被吊销 | 重新获取，**不要**去猜 |
| 发件被拒（SPF/DKIM） | 发件域未验证 | 用已验证的发件人；不要伪造 From |
| 进入垃圾箱 | 纯 HTML / 缺纯文本 | **同时提供 text 版本** |
| 正文乱码 | 编码 | 统一 UTF-8；附件 base64 |

## 验证

- 发送后确认返回的 `id` / 状态码；
- 收件箱里确实出现（或至少 API 明确返回成功）；
- **失败要说失败**，不要假装发出去了。
