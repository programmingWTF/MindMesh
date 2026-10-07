#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MindMesh Dashboard — 只读活动看板 + 仓库浏览器。

设计约束（请勿破坏）:
  * 只读。所有 git 调用都是查询（ls-tree / log / cat-file / rev-parse）。
    本进程永远不会写仓库。
  * 路径全部来自环境变量。源码里不出现任何硬编码路径。
  * 默认只监听 127.0.0.1。
  * 不带任何代理 / CDN / 隧道方案——那是使用者自己的决定，且必须先配好鉴权。

环境变量:
  MINDMESH_ROOT              仓库路径（默认：本文件所在目录的上一级）
  MINDMESH_REV               读取的 revision（默认 HEAD）
  MINDMESH_HOST              监听地址（默认 127.0.0.1）
  MINDMESH_PORT              监听端口（默认 3310）
  MINDMESH_PUBLIC_PREFIXES   无需鉴权的前缀，逗号分隔（默认 Skills/,docs/）
  MINDMESH_ALLOWED_ORIGINS   允许的跨域来源，逗号分隔（默认空 = 禁用跨域）
  MINDMESH_SECRET_DIR        存放口令摘要与签名密钥（默认 ./secret）
  MINDMESH_SESSION_DAYS      会话有效期天数（默认 30）
"""
import os
import re
import json
import time
import hmac
import base64
import hashlib
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

APP = os.path.dirname(os.path.abspath(__file__))

ROOT = os.environ.get("MINDMESH_ROOT") or os.path.dirname(APP)
REV = os.environ.get("MINDMESH_REV", "HEAD")
HOST = os.environ.get("MINDMESH_HOST", "127.0.0.1")
PORT = int(os.environ.get("MINDMESH_PORT", "3310"))
SESSION_DAYS = int(os.environ.get("MINDMESH_SESSION_DAYS", "30"))
SECRET_DIR = os.environ.get("MINDMESH_SECRET_DIR", os.path.join(APP, "secret"))
MAX_INLINE = 2_000_000
MAX_LIST = 2000

COOKIE = "mindmesh_session"

def _split_env(name, default):
    raw = os.environ.get(name)
    if raw is None:
        return tuple(default)
    return tuple(p.strip() for p in raw.split(",") if p.strip())

PUBLIC_PREFIXES = _split_env("MINDMESH_PUBLIC_PREFIXES", ("Skills/", "docs/"))
ALLOWED_ORIGINS = _split_env("MINDMESH_ALLOWED_ORIGINS", ())

# 永远禁止访问的路径
HARD_DENY = (".git/", "secret/", "Credentials/", "node_modules/")


# ── git helpers（全部只读） ───────────────────────────────────────────
def git(*args, timeout=20):
    cmd = ["git", "-C", ROOT] + list(args)
    p = subprocess.run(cmd, capture_output=True, timeout=timeout)
    if p.returncode != 0:
        err = p.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(err or "git failed: " + " ".join(args[:3]))
    return p.stdout


def git_text(*args, **kw):
    return git(*args, **kw).decode("utf-8", "replace")


def list_tree(rev=REV):
    out = git("ls-tree", "-r", "-l", "--full-name", rev)
    files = []
    for line in out.decode("utf-8", "replace").splitlines():
        try:
            meta, path = line.split("\t", 1)
        except ValueError:
            continue
        parts = meta.split()
        if len(parts) < 4:
            continue
        size = parts[3]
        files.append({"path": path, "size": int(size) if size.isdigit() else None})
    return files


def commits(path=None, limit=50):
    fmt = "%H%x1f%an%x1f%ae%x1f%ad%x1f%s%x1f%b%x1e"
    args = ["log", "--date=short", "--max-count=" + str(limit), "--format=" + fmt]
    if path:
        args += ["--", path]
    raw = git_text(*args)
    out = []
    for chunk in raw.split("\x1e"):
        chunk = chunk.strip("\n")
        if not chunk:
            continue
        f = chunk.split("\x1f")
        if len(f) < 6:
            continue
        body = f[5]
        agent = ""
        m = re.search(r"^Agent:\s*(\S+)\s*$", body, re.M)
        if m:
            agent = m.group(1)
        out.append({"sha": f[0][:10], "name": f[1], "email": f[2],
                    "date": f[3], "subject": f[4], "agent": agent})
    return out


# ── 鉴权 ──────────────────────────────────────────────────────────────
def _read(path):
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except OSError:
        return None


def auth_ready():
    return _read(os.path.join(SECRET_DIR, "password.sha256")) and \
           _read(os.path.join(SECRET_DIR, "hmac.key"))


def check_password(pw):
    stored = _read(os.path.join(SECRET_DIR, "password.sha256"))
    if not stored:
        return False
    got = hashlib.sha256(pw.encode("utf-8")).hexdigest().encode()
    return hmac.compare_digest(stored.strip(), got)


def _mac():
    key = _read(os.path.join(SECRET_DIR, "hmac.key"))
    return key or b""


def issue_token():
    exp = int(time.time()) + SESSION_DAYS * 86400
    msg = str(exp).encode()
    sig = hmac.new(_mac(), msg, hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(msg).decode() + "." + sig


def verify_token(tok):
    try:
        b64, sig = tok.split(".", 1)
        msg = base64.urlsafe_b64decode(b64.encode())
        good = hmac.new(_mac(), msg, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(good, sig):
            return False
        return int(msg.decode()) > time.time()
    except Exception:
        return False


def is_public(path):
    return any(path.startswith(p) for p in PUBLIC_PREFIXES)


def is_denied(path):
    if path.startswith("/") or ".." in path.split("/"):
        return True
    return any(path.startswith(d) or ("/" + d) in path for d in HARD_DENY)


# ── HTTP ──────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    server_version = "MindMeshDashboard"

    def log_message(self, fmt, *args):
        pass

    # --- 工具 ---
    def _send(self, code, body, ctype="application/json; charset=utf-8", extra=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _cors(self):
        origin = self.headers.get("Origin")
        if origin and origin in ALLOWED_ORIGINS:
            return {"Access-Control-Allow-Origin": origin,
                    "Vary": "Origin"}
        return {}

    def _authed(self):
        raw = self.headers.get("Cookie", "")
        for part in raw.split(";"):
            if "=" in part:
                k, v = part.strip().split("=", 1)
                if k == COOKIE and verify_token(v):
                    return True
        return False

    # --- 路由 ---
    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        path = u.path
        try:
            if path in ("/", "/index.html"):
                return self._static("index.html", "text/html; charset=utf-8")
            if path == "/api/summary":
                return self._send(200, self._summary())
            if path == "/api/commits":
                return self._send(200, {"commits": commits(
                    q.get("path", [None])[0],
                    min(int(q.get("limit", ["50"])[0]), 500))})
            if path == "/api/tree":
                return self._send(200, self._tree())
            if path == "/api/file":
                return self._file(q)
            if path == "/api/me":
                return self._send(200, {"authed": self._authed(),
                                        "authRequired": bool(auth_ready()),
                                        "publicPrefixes": list(PUBLIC_PREFIXES)})
            return self._send(404, {"error": "not found"})
        except RuntimeError as e:
            return self._send(500, {"error": str(e)[:500]})
        except Exception as e:  # noqa
            return self._send(500, {"error": "internal: " + str(e)[:200]})

    do_HEAD = do_GET

    def do_POST(self):
        u = urlparse(self.path)
        if u.path == "/api/login":
            n = int(self.headers.get("Content-Length", "0") or 0)
            try:
                data = json.loads(self.rfile.read(n) or b"{}")
            except Exception:
                data = {}
            if not auth_ready():
                return self._send(503, {"error": "未配置口令（见 docs/Dashboard.md）"})
            if check_password(str(data.get("password", ""))):
                tok = issue_token()
                return self._send(200, {"ok": True}, extra={
                    "Set-Cookie": COOKIE + "=" + tok + "; Path=/; HttpOnly; "
                                  "SameSite=Lax; Max-Age=" + str(SESSION_DAYS * 86400)})
            time.sleep(0.5)  # 轻微限速
            return self._send(401, {"error": "口令不正确"})
        if u.path == "/api/logout":
            return self._send(200, {"ok": True}, extra={
                "Set-Cookie": COOKIE + "=; Path=/; HttpOnly; Max-Age=0"})
        return self._send(404, {"error": "not found"})

    # --- 视图 ---
    def _static(self, name, ctype):
        fp = os.path.join(APP, name)
        data = _read(fp)
        if data is None:
            return self._send(404, {"error": "missing " + name})
        return self._send(200, data, ctype)

    def _summary(self):
        files = list_tree()
        cm = commits(limit=200)
        agents = {}
        for f in files:
            m = re.match(r"^Memory/([^/]+)/", f["path"])
            if m:
                a = agents.setdefault(m.group(1), {"files": 0, "bytes": 0, "commits": 0, "last": None})
                a["files"] += 1
                a["bytes"] += f["size"] or 0
        for c in cm:
            if c["agent"] and c["agent"] in agents:
                agents[c["agent"]]["commits"] += 1
                if not agents[c["agent"]]["last"]:
                    agents[c["agent"]]["last"] = c["date"]
        return {
            "root": os.path.basename(ROOT.rstrip("/")),
            "rev": REV,
            "branch": git_text("rev-parse", "--abbrev-ref", REV).strip(),
            "head": git_text("rev-parse", "--short", REV).strip(),
            "fileCount": len(files),
            "totalBytes": sum(f["size"] or 0 for f in files),
            "agents": [dict(name=k, **v) for k, v in sorted(agents.items())],
            "recentCommits": cm[:30],
            "publicPrefixes": list(PUBLIC_PREFIXES),
        }

    def _tree(self):
        files = list_tree()
        vis = []
        for f in files:
            vis.append({
                "path": f["path"],
                "size": f["size"],
                "public": is_public(f["path"]),
            })
        return {"rev": REV, "files": vis[:MAX_LIST], "truncated": len(vis) > MAX_LIST}

    def _file(self, q):
        path = (q.get("path", [""])[0] or "").strip()
        if not path or is_denied(path):
            return self._send(400, {"error": "非法路径"})
        if not is_public(path) and not self._authed():
            return self._send(403, {"error": "需要登录"})
        try:
            size = int(git_text("cat-file", "-s", REV + ":" + path).strip())
        except Exception:
            return self._send(404, {"error": "文件不存在"})
        if size > MAX_INLINE:
            return self._send(413, {"error": "文件过大，请在本地查看",
                                    "size": size})
        text = git_text("cat-file", "blob", REV + ":" + path)
        return self._send(200, {"path": path, "size": size, "text": text})


def main():
    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("⚠️ MINDMESH_ROOT 看起来不是一个 git 仓库: " + ROOT)
    if not auth_ready():
        print("ℹ️ 未配置口令：仅公开前缀可读。见 docs/Dashboard.md")
    if HOST not in ("127.0.0.1", "localhost", "::1"):
        print("⚠️ 你正在监听非本地地址 " + HOST + " —— 请确认已经配好鉴权与 TLS。")
    print("MindMesh Dashboard → http://" + HOST + ":" + str(PORT) + "  (repo: " + ROOT + ")")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
