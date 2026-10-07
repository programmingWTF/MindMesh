# 看板（Dashboard）

`Dashboard/` 是一个**只读**的活动看板：把每个 Agent 的提交与记忆改动可视化，
并能直接在浏览器里浏览仓库里的 Markdown。

**它不写仓库。**所有 Git 调用都是查询（`ls-tree` / `log` / `cat-file`）。

---

## 设计原则

| 原则 | 说明 |
|---|---|
| 🔒 **只读** | 永远不 `commit` / `checkout` / `reset`。看板弄坏仓库是不可接受的 |
| 🖥️ **默认本地** | 默认只监听 `127.0.0.1`，不默认暴露 |
| 🚫 **不带代理方案** | **刻意不提供** Cloudflare / CDN / 隧道等具体接入 |
| 🧩 **零依赖** | 只用 Python 3 标准库，不需要 node / 数据库 |
| 🗂️ **分级可见** | 按**路径前缀**决定哪些内容需要鉴权 |

---

## 跑起来

```bash
cd Dashboard
export MINDMESH_ROOT=<你的仓库根目录>
python3 server.py
# → http://127.0.0.1:3310
```

### 环境变量

| 变量 | 默认 | 说明 |
|---|---|---|
| `MINDMESH_ROOT` | 当前目录的上一级 | 仓库路径（**替代任何硬编码路径**） |
| `MINDMESH_SRC` | `worktree` | `worktree` 或 `bare` |
| `MINDMESH_REV` | `HEAD` | 读取的 revision |
| `MINDMESH_PORT` | `3310` | 监听端口 |
| `MINDMESH_HOST` | `127.0.0.1` | 监听地址 |
| `MINDMESH_PUBLIC_PREFIXES` | `Skills/,docs/` | **无需鉴权**即可查看的路径前缀 |
| `MINDMESH_ALLOWED_ORIGINS` | `（空）` | 允许的跨域来源；留空则禁用跨域 |
| `MINDMESH_SECRET_DIR` | `./secret` | 存放口令摘要与签名密钥（**不入库**） |
| `MINDMESH_MD_RENDER` | `off` | 是否渲染 Markdown |

> **任何路径都不应该硬编码在源码里。**这是把看板从「我的机器」变成「任何人的机器」的关键一步。

---

## 鉴权模型

两级：

1. **公开前缀**（`MINDMESH_PUBLIC_PREFIXES`）——例如 `Skills/`、`docs/`、`README.md`，任何人可读；
2. **其余内容**——需要一个会话 cookie，由**一次性口令**换取。

口令**不以明文存储**：server 只保存它的 sha256 摘要，校验通过后签发一个 HMAC 签名的 cookie。

```bash
mkdir -p Dashboard/secret && chmod 700 Dashboard/secret
printf '%s' '<你的口令>' | shasum -a 256 | cut -d' ' -f1 > Dashboard/secret/password.sha256
head -c 32 /dev/urandom > Dashboard/secret/hmac.key
chmod 600 Dashboard/secret/*
```

> ⚠️ `Dashboard/secret/` **必须在 .gitignore 里**。把它提交上去等于把看板送给所有人。

---

## 对外发布

我们**不提供**具体的发布方案。但无论你用什么（nginx / Caddy / 云厂商），**请先满足**：

- [ ] 上 TLS
- [ ] **先鉴权，再暴露**
- [ ] 只读（看板进程不要有仓库的写权限）
- [ ] 用**独立**的运行时用户跑它
- [ ] 限制请求体大小与超时

> 为什么刻意去掉代理方案：一个「中立架构」如果绑定了某家厂商，
> 它就不再是架构，而是一个绑定的推荐。**你用什么，是你的选择。**

---

## 替代方案

如果你只是想要「看谁在干活」：

**GitHub 本身就是一个看板。**见 `docs/ZeroServer.md`——
`Commits` / `Contributors` / `Blame` / `Actions` 全都有，一行部署都不需要。

这份看板的价值在于：**自建远端**（没有 Web 界面）或**想要自己的 UI** 时。
