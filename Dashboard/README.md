# Dashboard

一个**只读**的活动看板：把每个 Agent 的提交与记忆改动可视化，并能在浏览器里浏览仓库文件。

---

## 快速开始

```bash
cd Dashboard
export MINDMESH_ROOT="$(cd .. && pwd)"     # 仓库根目录
python3 server.py
# → http://127.0.0.1:3310
```

**零依赖**：只用 Python 3 标准库。

---

## 配置

| 环境变量 | 默认 | 说明 |
|---|---|---|
| `MINDMESH_ROOT` | 上级目录 | 仓库路径（**不要在源码里硬编码**） |
| `MINDMESH_REV` | `HEAD` | 读取的 revision |
| `MINDMESH_HOST` | `127.0.0.1` | 监听地址 |
| `MINDMESH_PORT` | `3310` | 监听端口 |
| `MINDMESH_PUBLIC_PREFIXES` | `Skills/,docs/` | 无需登录即可查看的前缀 |
| `MINDMESH_ALLOWED_ORIGINS` | （空） | 允许的跨域来源；空 = 禁用 |
| `MINDMESH_SECRET_DIR` | `./secret` | 口令摘要与签名密钥 |
| `MINDMESH_SESSION_DAYS` | `30` | 会话有效期 |

---

## 设置访问口令

口令**不以明文存储**——只存它的 sha256 摘要：

```bash
mkdir -p secret && chmod 700 secret
printf '%s' '<你的口令>' | shasum -a 256 | cut -d' ' -f1 > secret/password.sha256
head -c 32 /dev/urandom > secret/hmac.key
chmod 600 secret/*
```

> ⚠️ `Dashboard/secret/` **必须**在 `.gitignore` 里（本仓库已配好）。提交它等于把看板送给所有人。

**没有配置口令时**：只有 `MINDMESH_PUBLIC_PREFIXES` 里的内容可读，其余一律 403。这是一个安全的默认值。

---

## 只读保证

本服务**只**调用这些 git 子命令：

```text
git ls-tree    git log    git cat-file    git rev-parse
```

没有任何 `commit` / `checkout` / `reset` / `clean`。
**看板弄坏仓库是不可接受的**，所以这条约束是硬性的。

---

## 对外发布

本仓库**刻意不提供**任何 CDN / 隧道 / 代理厂商的接入方案——那是各家自己的绑定，不该混进中立方案。

无论你用什么方式暴露它，请先满足：

- [ ] TLS
- [ ] **先鉴权，再暴露**
- [ ] 看板进程**没有**仓库的写权限
- [ ] 用独立的、低权限的运行用户
- [ ] 限制请求体大小与超时
- [ ] `MINDMESH_ALLOWED_ORIGINS` 只填你真正的来源，不要用 `*`

---

## 你可能根本不需要它

如果你用 GitHub 当远端，**GitHub 本身就是一个看板**：

| 你想要的 | GitHub 自带 |
|---|---|
| 谁改了什么 | Commits |
| 某个 Agent 的活跃度 | Insights → Contributors |
| 按目录浏览 | 文件树（天然按 `Memory/<Agent>/` 分区） |
| 追一个决定 | Blame |
| 评审改动 | Pull Request |
| 定时任务 | Actions |

见 `docs/ZeroServer.md`。这个自托管看板的价值在于：**私有远端没有 Web 界面**，或者**你想自己控制 UI**。
