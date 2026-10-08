# MindMesh Dashboard

一个**只读**的活动看板：把每个 Agent 的提交与记忆改动可视化，并能在浏览器里浏览仓库文件。
纯 Python 标准库，零依赖，单文件部署。

---

## 功能

- **概览**：Agent 卡片（commits / files / 近 30 天 sparkline）、30 天活动堆叠柱图（按 Agent / 按目录）、热门文件
- **文件浏览**：懒加载目录树、Markdown 渲染 / 源码双模式、二进制预览、**递归文件搜索**、打开文件时目录树自动展开定位 + 高亮标记
- **提交改动**：逐提交 diff 视图（分页加载），从概览任意文件名 / hash 一键跳转
- **hash 路由**：`#/`（概览）、`#/files`、`#/commits`，浏览器前进 / 后退可用，URL 即状态
- **私密区**：`MINDMESH_PUBLIC_PREFIXES` / `MINDMESH_PUBLIC_FILES` 之外的内容需要口令解锁（session cookie，180 天可选）
- **健康面板**：workspace 文件与仓库副本的同步状态、最新维护报告（可选，配 `MINDMESH_WS` 启用）

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

全部通过环境变量，源码里没有任何硬编码路径 / 域名：

| 环境变量 | 默认 | 说明 |
|---|---|---|
| `MINDMESH_ROOT` | 上级目录 | 仓库工作副本路径 |
| `MINDMESH_BARE` | （空） | 裸仓库路径（存在则优先，零延迟） |
| `MINDMESH_REV` | `origin/main` | 工作副本读取的 revision |
| `MINDMESH_BARE_REV` | `refs/heads/main` | 裸仓库读取的 revision |
| `MINDMESH_HOST` | `127.0.0.1` | 监听地址 |
| `MINDMESH_PORT` | `3310` | 监听端口 |
| `MINDMESH_PUBLIC_PREFIXES` | `Skills/,docs/` | 无需登录即可查看的目录前缀 |
| `MINDMESH_PUBLIC_FILES` | `README.md,…` | 无需登录即可查看的根文件 |
| `MINDMESH_ALLOWED_ORIGINS` | （空） | 允许的跨域来源；空 = 禁用（同源部署不需要） |
| `MINDMESH_SECRET_DIR` | `./secret` | 口令摘要与签名密钥目录 |
| `MINDMESH_SESSION_DAYS` | `30` | 会话有效期 |
| `MINDMESH_COOKIE` | `mindmesh_session` | 会话 cookie 名 |
| `MINDMESH_EXTRA_PWD` | （空） | 可选的第二份口令摘要文件路径 |
| `MINDMESH_AGENTS` | （空） | 概览预置的 Agent 名单；空 = 从提交历史自动发现 |
| `MINDMESH_AUTHOR_AGENT` | （空） | git 作者名兜底归因，格式 `作者名=AgentName,...` |
| `MINDMESH_WS` | （空） | workspace 目录（启用健康面板） |
| `MINDMESH_LINKS` | （空） | 健康面板检查的文件名列表（需配 `MINDMESH_WS`） |
| `MINDMESH_LINKS_REPO_DIR` | （空） | 这些文件在仓库内的对应目录 |
| `MINDMESH_MAINT_DIR` | （空） | 维护报告目录（相对仓库根） |

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

**没有配置口令时**：只有 `MINDMESH_PUBLIC_PREFIXES` / `MINDMESH_PUBLIC_FILES` 里的内容可读，其余一律 403。这是一个安全的默认值。

---

## 部署形态

- **最简**：`python3 server.py`，浏览器直接访问，或用 nginx / caddy 反代
- **前后端分离**：静态文件走 CDN / nginx，API 域名通过 index.html 里的 `<meta name="mindmesh-api" content="https://api.example.com">` 指定（不配则默认同源），服务端配 `MINDMESH_ALLOWED_ORIGINS` 允许跨域
- **systemd**：参考

```ini
[Service]
WorkingDirectory=/opt/mindmesh/Dashboard
Environment=MINDMESH_ROOT=/srv/mindmesh
Environment=MINDMESH_HOST=0.0.0.0
ExecStart=/usr/bin/python3 /opt/mindmesh/Dashboard/server.py
Restart=always
```

---

## 只读保证

本服务**只**调用这些 git 子命令：

```text
git ls-tree    git log    git cat-file    git rev-parse    git fetch
```

没有任何 `commit` / `checkout` / `reset` / `clean`。`fetch` 仅用于让工作副本的 `origin/main` 保持新鲜（裸仓库模式不 fetch）。

---

## 字体

`static/` 内的 Monaspace Radon 字体基于 [SIL Open Font License 1.1](https://openfontlicense.org/) 授权，见 [FONT-LICENSE.md](./static/FONT-LICENSE.md)。

## License

Apache-2.0，与 MindMesh 主仓库一致。
