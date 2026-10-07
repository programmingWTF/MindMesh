---
name: mindmesh-remote
description: 访问远端机器（SSH）。当需要连服务器、NAS、VPS、另一台电脑、在远端执行命令、传文件时使用。
---

# 远端访问

## 第 0 条：先设超时

**慢链路会把「超时」伪装成「认证失败」。**这是最浪费时间的一类假故障。

```bash
ssh -o ConnectTimeout=120 -o ServerAliveInterval=20 -o ServerAliveCountMax=6 <别名> "命令"
```

写进 ``` ~/.ssh/config ``` 一次，之后就不用每次带了。

## 先验证，再干活

```bash
ssh -o ConnectTimeout=120 <别名> "echo OK && uname -a && uptime"
```

看到 `OK` 才继续。**不要**在一个可能超时的连接上直接跑一条会改状态的命令。

## 别名约定

把别名写进 `04RemoteAccess.md`，不要每次拼地址：

| 别名 | 场景 | 特点 |
|---|---|---|
| `<填>` | 局域网 | 快 |
| `<填>` | 远程（隧道） | **慢，等 30~120 秒，别中断** |

## 常用

```bash
# 单条命令
ssh <别名> "systemctl --user status <服务>"

# 传文件
scp <本地> <别名>:<远端路径>
rsync -av --progress <本地>/ <别名>:<远端>/

# 长任务：放后台，别占着会话
ssh <别名> "nohup <命令> > /tmp/out.log 2>&1 &"

# 需要交互时用 tmux
ssh <别名> -t "tmux new -A -s work"
```

## 纪律

- **先看再动**：在别人（包括你自己的）机器上，改配置前先读现状。
- **改前备份**：`cp <文件> <文件>.bak`。
- **改动记进记忆**：`Memory/<我的名字>/` 里写「在哪台机器、改了什么、为什么」。
- **不要留下密钥**：用完清理临时凭据。

## 失败路径

| 症状 | 真实原因 | 做法 |
|---|---|---|
| `Permission denied` 但密钥没问题 | **超时** | 加大 `ConnectTimeout`，重试，不要反复重配密钥 |
| 连上就断 | `ServerAliveInterval` 未设 | 按上面的配置 |
| `Host key verification failed` | 机器重装过 | 核对指纹后更新 `known_hosts` |
| 外网连不上，内网正常 | 无公网入口 | 见 `04RemoteAccess.md`（隧道 / 或干脆不用 SSH） |

## 验证

- `echo OK` 返回；
- 改动前有备份、改动后有可复现的命令记录在 `Memory/<我的名字>/` 里。
