#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MindMesh Dashboard - read-only dashboard + repo browser for agent memory repos.

Read-only: every git call is a query (ls-tree / log / cat-file / fetch). The
repository is never written to.

Data source: a bare repo (MINDMESH_BARE) when available, else a worktree
(MINDMESH_ROOT, default: the parent directory). Private areas (everything
outside MINDMESH_PUBLIC_PREFIXES / MINDMESH_PUBLIC_FILES) require a session
cookie obtained by posting the admin password (only its sha256 digest is
stored; the plaintext is never needed here).

All configuration is done through MINDMESH_* environment variables - see
README.md. No paths, domains or identities are hard-coded.
"""
import os
import re
import json
import time
import hmac
import hashlib
import gzip
import filecmp
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

import mdrender

APP = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("MINDMESH_ROOT") or os.path.dirname(APP)   # worktree
BARE = os.environ.get("MINDMESH_BARE", "")                       # optional bare repo (faster)
WS = os.environ.get("MINDMESH_WS", "")                           # optional workspace dir (health panel)
PORT = int(os.environ.get("MINDMESH_PORT", "3310"))
HOST = os.environ.get("MINDMESH_HOST", "127.0.0.1")
TTL = 15
LIMIT = 800
STATIC_DIR = os.path.join(APP, "static")
ICON_DIR = os.path.join(APP, "icons")

SECRET_DIR = os.environ.get("MINDMESH_SECRET_DIR") or os.path.join(APP, "secret")
PWD_FILE = os.path.join(SECRET_DIR, "password.sha256")
KEY_FILE = os.path.join(SECRET_DIR, "hmac.key")
EXTRA_PWD = os.environ.get("MINDMESH_EXTRA_PWD", "")  # optional second digest file
COOKIE = os.environ.get("MINDMESH_COOKIE", "mindmesh_session")
SESSION_DAYS = int(os.environ.get("MINDMESH_SESSION_DAYS", "30"))
MAX_INLINE = 2_000_000
MAX_RAW = 8_000_000


def _split_env(name, default):
    raw = os.environ.get(name)
    if raw is None:
        return tuple(default)
    return tuple(x.strip() for x in raw.split(",") if x.strip())


ALLOWED_ORIGINS = _split_env("MINDMESH_ALLOWED_ORIGINS", ())
PUBLIC_PREFIXES = _split_env("MINDMESH_PUBLIC_PREFIXES", ("Skills/", "docs/"))
# Root docs that carry no credential values: safe to read without the password.
PUBLIC_FILES = _split_env("MINDMESH_PUBLIC_FILES",
                          ("README.md", "SKILL.md", "Index.md", "CHANGELOG.md", "LICENSE"))
HARD_DENY = (".git/", "secret/", "Credentials/", "node_modules/")

SRC = REPO
REV = os.environ.get("MINDMESH_REV", "origin/main")
BARE_REV = os.environ.get("MINDMESH_BARE_REV", "refs/heads/main")
SRCKIND = "worktree"
_last_fetch = 0.0
CACHE = {"t": 0.0, "data": None, "tree_t": 0.0, "tree": None}
LOCK = threading.Lock()
TRIES = {}
US = "\x1f"
RS = "\x1e"
_JS = "application/json; charset=utf-8"

AGENTS = _split_env("MINDMESH_AGENTS", ())  # agents to pre-seed in the overview grid
LINKS = _split_env("MINDMESH_LINKS", ())    # workspace files to health-check (needs MINDMESH_WS)

LANG_EXT = {
    "py": "python", "js": "javascript", "mjs": "javascript", "cjs": "javascript",
    "ts": "typescript", "tsx": "tsx", "jsx": "jsx", "json": "json", "sh": "bash",
    "bash": "bash", "zsh": "bash", "md": "markdown", "yml": "yaml", "yaml": "yaml",
    "toml": "toml", "ini": "ini", "cfg": "ini", "html": "html", "htm": "html",
    "css": "css", "scss": "scss", "sql": "sql", "go": "go", "rs": "rust", "java": "java",
    "c": "c", "h": "c", "cpp": "cpp", "hpp": "cpp", "rb": "ruby", "php": "php",
    "xml": "xml", "dockerfile": "docker", "ps1": "powershell", "bat": "batch",
    "csv": "text", "txt": "text", "log": "text", "env": "bash", "conf": "ini",
}
BINARY_EXT = {"png", "jpg", "jpeg", "gif", "webp", "ico", "bmp", "svg", "pdf", "zip",
              "gz", "tar", "tgz", "woff", "woff2", "ttf", "otf", "mp4", "mp3", "wav",
              "xlsx", "xls", "docx", "doc", "pptx", "jar", "so", "bin", "exe", "dll",
              "pyc", "sqlite", "db"}


# --------------------------------------------------------------------------- git
def pick_source():
    global SRC, REV, SRCKIND
    try:
        if os.path.isdir(BARE) and os.access(os.path.join(BARE, "HEAD"), os.R_OK):
            SRC, REV, SRCKIND = BARE, BARE_REV, "bare"
            return
    except Exception:
        pass
    SRC, SRCKIND = REPO, "worktree"


def _gitargs(a):
    return ["git", "--no-pager", "-c", "core.quotePath=false", "-C", SRC] + list(a)


def git(*a, timeout=60):
    try:
        p = subprocess.run(_gitargs(a), capture_output=True, text=True, timeout=timeout)
        return p.stdout
    except Exception:
        return ""


def gitb(*a, timeout=60):
    try:
        p = subprocess.run(_gitargs(a), capture_output=True, timeout=timeout)
        return p.stdout
    except Exception:
        return b""


def tree():
    """path -> {"sha","size"} for every tracked blob, cached."""
    now = time.time()
    with LOCK:
        if CACHE["tree"] is not None and now - CACHE["tree_t"] < TTL:
            return CACHE["tree"]
    out = git("ls-tree", "-r", "-l", REV)
    t = {}
    for line in out.splitlines():
        if "\t" not in line:
            continue
        meta, path = line.split("\t", 1)
        parts = meta.split()
        if len(parts) < 4 or parts[1] != "blob":
            continue
        try:
            size = int(parts[3])
        except Exception:
            size = 0
        t[path] = {"sha": parts[2], "size": size}
    with LOCK:
        CACHE["tree"] = t
        CACHE["tree_t"] = now
    return t


# --------------------------------------------------------------------------- perms
def is_private(p):
    if p.startswith(HARD_DENY):
        return True
    if p in PUBLIC_FILES:
        return False
    q = p.rstrip("/")
    for pre in PUBLIC_PREFIXES:
        if q == pre.rstrip("/") or p.startswith(pre):
            return False
    return True


def deny(p):
    return p.startswith(HARD_DENY) or ".." in p.split("/") or p.startswith("/")


# --------------------------------------------------------------------------- auth
_key_cache = None


def key():
    global _key_cache
    if _key_cache:
        return _key_cache
    try:
        os.makedirs(SECRET_DIR, mode=0o700, exist_ok=True)
    except Exception:
        pass
    try:
        with open(KEY_FILE, "r") as f:
            _key_cache = bytes.fromhex(f.read().strip())
    except Exception:
        _key_cache = os.urandom(32)
        try:
            fd = os.open(KEY_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w") as f:
                f.write(_key_cache.hex())
        except Exception:
            pass
    return _key_cache


def password_hash():
    for p in (PWD_FILE, EXTRA_PWD):
        try:
            with open(p) as f:
                h = f.read().strip().lower()
            if re.fullmatch(r"[0-9a-f]{64}", h):
                return h
        except Exception:
            continue
    return ""


def issue_token():
    exp = int(time.time()) + SESSION_DAYS * 86400
    sig = hmac.new(key(), str(exp).encode(), hashlib.sha256).hexdigest()
    return "%d.%s" % (exp, sig)


def verify_token(tok):
    try:
        exp_s, sig = tok.split(".", 1)
        exp = int(exp_s)
    except Exception:
        return 0
    if exp < time.time():
        return 0
    good = hmac.new(key(), str(exp).encode(), hashlib.sha256).hexdigest()
    return exp if hmac.compare_digest(good, sig) else 0


def rate_ok(ip):
    now = time.time()
    rec = TRIES.get(ip)
    if not rec or now - rec[0] > 600:
        TRIES[ip] = [now, 1]
        return True
    rec[1] += 1
    return rec[1] <= 5


# --------------------------------------------------------------------------- summary
def trailer_agent(body):
    m = re.search(r"^Agent:\s*([A-Za-z0-9_.-]+)\s*$", body or "", re.M)
    return m.group(1) if m else None


# 2026-10-08: 作者名兜底归因（防止漏写 Agent trailer 时 GitHub 身份被当成独立 agent）
AUTHOR_AGENT = {}
for _kv in (os.environ.get("MINDMESH_AUTHOR_AGENT") or "").split(","):
    if "=" in _kv:
        _k, _v = _kv.split("=", 1)
        AUTHOR_AGENT[_k.strip()] = _v.strip()


def commit_agent(body, author):
    return trailer_agent(body) or AUTHOR_AGENT.get(author) or author or "Unknown"


CATS = ["记忆", "技能库", "脚本", "文档", "其他"]


def cat_of(f):
    if f.startswith("Memory/"):
        return "记忆"
    if f.startswith("Skills/") or f.startswith("Library/"):
        return "技能库"
    if f.startswith("Scripts/"):
        return "脚本"
    if "/" not in f:
        return "文档"
    return "其他"


def human(n):
    for u, s in ((1 << 30, "GB"), (1 << 20, "MB"), (1 << 10, "KB")):
        if n >= u:
            return "%.1f %s" % (n / float(u), s)
    return "%d B" % n


def build():
    global _last_fetch
    pick_source()
    if SRCKIND == "worktree" and time.time() - _last_fetch > 60:
        git("fetch", "--all", "--prune", timeout=45)
        _last_fetch = time.time()

    total = 0
    try:
        total = int(git("rev-list", "--count", REV).strip() or 0)
    except Exception:
        pass
    branch = (REV.split("/")[-1] if SRCKIND == "worktree" else "main")
    tracked = len(tree())

    try:
        gsize = sum(os.path.getsize(os.path.join(dp, f))
                    for dp, _, fs in os.walk(os.path.join(SRC, "objects")) for f in fs)
        if SRCKIND == "worktree":
            gsize = sum(os.path.getsize(os.path.join(dp, f))
                        for dp, _, fs in os.walk(os.path.join(REPO, ".git")) for f in fs)
    except Exception:
        gsize = 0

    raw = git("log", REV, "-n", str(LIMIT), "--name-only", "--date=iso-strict",
              "--pretty=format:" + RS + "%H" + US + "%aI" + US + "%an" + US + "%s" + US + "%b" + US)
    commits = []
    for ch in raw.split(RS):
        ch = ch.strip("\n")
        if not ch:
            continue
        p = ch.split(US)
        if len(p) < 6:
            continue
        files = [x.strip() for x in p[5].splitlines() if x.strip()]
        cnt = {}
        for f in files:
            k = cat_of(f)
            cnt[k] = cnt.get(k, 0) + 1
        dom = max(cnt, key=lambda k: cnt[k]) if cnt else "其他"
        commits.append({"hash": p[0], "short": p[0][:8], "date": p[1], "author": p[2],
                        "agent": commit_agent(p[4], p[2]),
                        "subject": p[3], "files": files, "nfiles": len(files), "cat": dom,
                        "private": any(is_private(f) for f in files)})

    per = {}
    for a in AGENTS:
        per[a] = {"commits": 0, "files": set(), "last": None, "days": {}, "touched": 0}
    for c in commits:
        d = per.setdefault(c["agent"], {"commits": 0, "files": set(), "last": None, "days": {}, "touched": 0})
        d["commits"] += 1
        d["touched"] += len(c["files"])
        for f in c["files"]:
            d["files"].add(f)
        day = (c["date"] or "")[:10]
        if day:
            d["days"][day] = d["days"].get(day, 0) + 1
        if not d["last"] or c["date"] > d["last"]:
            d["last"] = c["date"]

    today = time.strftime("%Y-%m-%d")
    t0 = time.mktime(time.strptime(today, "%Y-%m-%d"))
    days = [time.strftime("%Y-%m-%d", time.localtime(t0 - i * 86400)) for i in range(29, -1, -1)]
    daily = []
    for dd in days:
        row = {"date": dd, "total": 0, "by": {}, "bycat": {}}
        for a, d in per.items():
            n = d["days"].get(dd, 0)
            if n:
                row["by"][a] = n
                row["total"] += n
        for c in commits:
            if (c["date"] or "")[:10] == dd:
                k = c.get("cat", "其他")
                row["bycat"][k] = row["bycat"].get(k, 0) + 1
        daily.append(row)

    agents = []
    for a, d in per.items():
        agents.append({"name": a, "commits": d["commits"], "files_touched": d["touched"],
                       "unique_files": len(d["files"]), "last": d["last"],
                       "spark": [d["days"].get(x, 0) for x in days]})
    agents.sort(key=lambda x: (-x["commits"], x["name"]))

    fcount = {}
    for c in commits:
        for f in c["files"]:
            fcount[f] = fcount.get(f, 0) + 1
    hot = sorted(fcount.items(), key=lambda kv: -kv[1])[:40]

    links = []
    links_dir = os.environ.get("MINDMESH_LINKS_REPO_DIR", "")  # repo-side twin of the workspace files
    for f in LINKS:
        p = os.path.join(WS, f)
        repo_p = os.path.join(REPO, links_dir, f) if links_dir else os.path.join(REPO, f)
        is_link = os.path.islink(p)
        exists = os.path.isfile(p)
        ok = bool(exists and not is_link)
        in_sync = False
        if ok and os.path.isfile(repo_p):
            try:
                in_sync = filecmp.cmp(p, repo_p, shallow=False)
            except Exception:
                in_sync = False
        links.append({"file": f, "ok": ok, "in_sync": in_sync, "is_link": is_link,
                      "target": os.readlink(p) if is_link else None})
    maint = ""
    try:
        md = os.environ.get("MINDMESH_MAINT_DIR", "")
        fs = sorted(os.listdir(os.path.join(REPO, md))) if md and os.path.isdir(os.path.join(REPO, md)) else []
        maint = fs[-1] if fs else ""
    except Exception:
        pass

    return {"generated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": {"kind": SRCKIND, "path": SRC, "rev": REV},
            "repo": {"path": REPO, "branch": branch, "commits": total, "tracked_files": tracked,
                     "git_size": human(gsize), "git_bytes": gsize,
                     "last_commit": commits[0]["date"] if commits else None},
            "agents": agents, "commits": commits, "daily": daily, "cats": CATS,
            "hot_files": [{"file": k, "count": v} for k, v in hot],
            "days": days,
            "health": {"links_ok": sum(1 for x in links if x["ok"]), "links_total": len(LINKS),
                       "links": links, "maintenance": maint}}


def cached():
    with LOCK:
        if CACHE["data"] is not None and (time.time() - CACHE["t"]) < TTL:
            return CACHE["data"]
    d = build()
    with LOCK:
        CACHE["data"] = d
        CACHE["t"] = time.time()
    return d


# --------------------------------------------------------------------------- files
def list_dir(path):
    t = tree()
    if path and not path.endswith("/"):
        path += "/"
    dirs = {}
    files = []
    for p in t:
        if deny(p) or not p.startswith(path):
            continue
        rest = p[len(path):]
        if not rest:
            continue
        if "/" in rest:
            name = rest.split("/", 1)[0] + "/"
            dirs[name] = dirs.get(name, 0) + 1
        else:
            files.append({"name": rest, "size": t[p]["size"], "sha": t[p]["sha"]})
    entries = [{"name": d, "type": "dir", "count": c, "private": is_private(path + d)}
               for d, c in dirs.items()]
    entries += [{"name": f["name"], "type": "file", "size": f["size"], "sha": f["sha"],
                 "private": is_private(path + f["name"]),
                 "lang": LANG_EXT.get(f["name"].rsplit(".", 1)[-1].lower(), "") if "." in f["name"] else ""}
                for f in files]
    entries.sort(key=lambda e: (e["type"] != "dir", e["name"].lower()))
    return entries


def file_payload(path, authed, want_render=True):
    if deny(path):
        return None, 403, "forbidden"
    t = tree()
    e = t.get(path)
    if not e:
        return None, 404, "not found"
    priv = is_private(path)
    if priv and not authed:
        return {"path": path, "private": True, "authed": False}, 200, None
    size = e["size"]
    ext = path.rsplit(".", 1)[-1].lower() if "." in path.rsplit("/", 1)[-1] else ""
    payload = {"path": path, "size": size, "sha": e["sha"], "private": priv, "authed": True,
               "ext": ext, "lang": LANG_EXT.get(ext, ""), "binary": ext in BINARY_EXT,
               "too_big": size > MAX_INLINE}
    if payload["binary"]:
        return payload, 200, None
    data = gitb("cat-file", "blob", e["sha"], timeout=30)
    if b"\x00" in data[:8000]:
        payload["binary"] = True
        return payload, 200, None
    if size > MAX_RAW:
        payload["truncated"] = True
        data = data[:MAX_RAW]
    text = data.decode("utf-8", "replace")
    payload["raw"] = text
    if ext == "md" and want_render and size <= MAX_INLINE:
        try:
            payload["html"] = mdrender.render(text)
        except Exception as ex:
            payload["render_error"] = str(ex)
    elif not payload["binary"] and not payload["lang"] and ext not in ("txt",):
        payload["lang"] = "text"
    return payload, 200, None


def commit_payload(sha, authed):
    if not re.fullmatch(r"[0-9a-fA-F]{4,40}", sha or ""):
        return None
    meta = git("show", "-s", "--date=iso-strict", "--format=%H%x1f%aI%x1f%an%x1f%cn%x1f%s%x1f%b", sha)
    if not meta.strip():
        return None
    p = meta.split("\x1f")
    if len(p) < 6:
        return None
    files_raw = git("show", "--numstat", "--format=", sha)
    files = []
    for line in files_raw.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        a, d, f = parts[0], parts[1], "\t".join(parts[2:])
        files.append({"path": f, "add": a, "del": d, "private": is_private(f),
                      "binary": a == "-"})
    out = {"sha": p[0], "short": p[0][:8], "date": p[1], "author": p[2], "committer": p[3],
           "subject": p[4], "body": p[5], "agent": commit_agent(p[5], p[2]),
           "files": files, "authed": authed,
           "private": any(f["private"] for f in files)}
    if out["private"] and not authed:
        return out
    patch = git("show", "--format=", "--no-color", "-U3", sha, timeout=60)
    chunks = {}
    cur = None
    for line in patch.splitlines(True):
        m = re.match(r"^diff --git a/(.*?) b/(.*)$", line)
        if m:
            cur = m.group(2)
            chunks.setdefault(cur, [])
            continue
        if cur is not None and line.startswith("@@"):
            chunks.setdefault(cur, []).append(line)
        elif cur is not None and not line.startswith(("index ", "--- ", "+++ ", "new file", "deleted file", "similarity", "old mode", "new mode", "rename ")):
            chunks[cur].append(line)
    for f in files:
        body = "".join(chunks.get(f["path"], []))
        if len(body) > 200000:
            body = body[:200000] + "\n... (truncated)"
        f["patch"] = body
    return out


# --------------------------------------------------------------------------- http
class H(BaseHTTPRequestHandler):
    server_version = "MindMeshDash/2.0"

    def log_message(self, *a):
        pass

    def _headers(self, code, ct, extra=None, length=None, cache="no-store"):
        self.send_response(code)
        self.send_header("Content-Type", ct)
        self.send_header("Cache-Control", cache)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; img-src 'self' data: https:; "
                         "style-src 'self' 'unsafe-inline'; script-src 'self'; "
                         "font-src 'self'; connect-src 'self " + " ".join(ALLOWED_ORIGINS) + "; "
                         "base-uri 'none'; form-action 'none'")
        origin = self.headers.get("Origin")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Credentials", "true")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Vary", "Origin")
        if extra:
            for k, v in extra:
                self.send_header(k, v)
        if length is not None:
            self.send_header("Content-Length", str(length))
        self.end_headers()

    def _wants_gzip(self, ct, body):
        if len(body) < 700:
            return False
        if "gzip" not in (self.headers.get("Accept-Encoding") or "").lower():
            return False
        base = ct.split(";")[0].strip().lower()
        return base in ("application/json", "text/html", "text/css",
                        "application/javascript", "text/javascript",
                        "image/svg+xml", "text/plain", "application/xml")

    def _send(self, code, ct, body, extra=None, cache="no-store"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        hdrs = list(extra or [])
        if self._wants_gzip(ct, body):
            body = gzip.compress(body, 6)
            hdrs.append(("Content-Encoding", "gzip"))
            hdrs.append(("Vary", "Accept-Encoding"))
        self._headers(code, ct, hdrs, length=len(body), cache=cache)
        try:
            self.wfile.write(body)
        except Exception:
            pass

    def _json(self, code, obj, extra=None):
        self._send(code, _JS, json.dumps(obj, ensure_ascii=False))

    def authed(self):
        raw = self.headers.get("Cookie", "")
        for part in raw.split(";"):
            k, _, v = part.strip().partition("=")
            if k == COOKIE:
                return verify_token(v)
        return 0

    def do_OPTIONS(self):
        self.send_response(204)
        origin = self.headers.get("Origin")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Credentials", "true")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Max-Age", "86400")
            self.send_header("Vary", "Origin")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        p = urlparse(self.path).path
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else b""
        if p == "/api/login":
            ip = self.headers.get("X-Real-IP") or self.client_address[0]
            if not rate_ok(ip):
                return self._json(429, {"error": "too_many"})
            try:
                data = json.loads(body.decode("utf-8"))
            except Exception:
                data = {}
            pw = data.get("password") or ""
            want = password_hash()
            got = hashlib.sha256(pw.encode("utf-8")).hexdigest()
            if want and hmac.compare_digest(want, got):
                TRIES.pop(ip, None)
                tok = issue_token()
                host = self.headers.get("Host", "")
                secure = not re.match(r"^(127\.0\.0\.1|localhost)(:|$)", host)
                ck = "%s=%s; Path=/; Max-Age=%d; HttpOnly; SameSite=Lax%s" % (
                    COOKIE, tok, SESSION_DAYS * 86400, "; Secure" if secure else "")
                self._headers(200, _JS, [("Set-Cookie", ck)], length=len(b'{"ok":true}'))
                self.wfile.write(b'{"ok":true}')
            else:
                time.sleep(0.4)
                return self._json(401, {"error": "bad_password"})
            return
        if p == "/api/logout":
            self._headers(200, _JS, [("Set-Cookie", COOKIE + "=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax")],
                          length=len(b'{"ok":true}'))
            self.wfile.write(b'{"ok":true}')
            return
        self._send(404, "text/plain", "not found")

    def do_GET(self):
        u = urlparse(self.path)
        p = u.path
        q = parse_qs(u.query)
        authed = bool(self.authed())

        if p == "/api/me":
            return self._json(200, {"authed": authed})
        if p == "/api/summary":
            try:
                return self._json(200, cached())
            except Exception as e:
                return self._json(500, {"error": str(e)})
        if p == "/api/tree":
            path = (q.get("path", [""])[0]).lstrip("/")
            if deny(path):
                return self._json(403, {"error": "forbidden"})
            if path and is_private(path) and not authed:
                return self._json(403, {"error": "auth_required"})
            return self._json(200, {"path": path, "entries": list_dir(path)})
        if p == "/api/fsearch":
            # 2026-10-08: 文件树递归搜索（懒加载树搜不了全仓库）。
            # 未登录时隐藏私密路径，不报 403，保证搜索框始终可用。
            qs = (q.get("q", [""])[0]).strip().lower()
            if not qs:
                return self._json(200, {"results": []})
            out = []
            t = tree()
            for fp in t:
                if deny(fp) or qs not in fp.lower():
                    continue
                priv = is_private(fp)
                if priv and not authed:
                    continue
                if len(out) >= 120:
                    out.append({"path": "…", "truncated": True})
                    break
                out.append({"path": fp, "private": priv,
                            "size": t[fp]["size"]})
            return self._json(200, {"results": out})
        if p == "/api/file":
            path = (q.get("path", [""])[0]).lstrip("/")
            if not path:
                return self._json(400, {"error": "path required"})
            payload, code, err = file_payload(path, authed)
            if code != 200:
                return self._json(code, {"error": err})
            return self._json(200, payload)
        if p == "/api/raw":
            path = (q.get("path", [""])[0]).lstrip("/")
            if deny(path):
                return self._send(403, "text/plain", "forbidden")
            if is_private(path) and not authed:
                return self._send(403, "text/plain", "auth required")
            t = tree()
            e = t.get(path)
            if not e:
                return self._send(404, "text/plain", "not found")
            if e["size"] > MAX_RAW:
                return self._send(413, "text/plain", "file too large")
            data = gitb("cat-file", "blob", e["sha"])
            ext = path.rsplit(".", 1)[-1].lower() if "." in path.rsplit("/", 1)[-1] else "txt"
            ct = "text/plain; charset=utf-8"
            disp = "attachment"
            if ext in ("png", "jpg", "jpeg", "gif", "webp", "svg", "ico", "pdf"):
                ct = {"svg": "image/svg+xml"}.get(ext, "image/" + ("jpeg" if ext in ("jpg", "jpeg") else ext))
                disp = "inline"
            name = path.rsplit("/", 1)[-1]
            return self._send_headers_body(
                ct, data, [("Content-Disposition", '%s; filename="%s"' % (disp, name))])
        if p == "/api/commit":
            sha = q.get("sha", [""])[0]
            obj = commit_payload(sha, authed)
            if obj is None:
                return self._json(404, {"error": "not found"})
            return self._json(200, obj)
        if p == "/healthz":
            return self._send(200, "text/plain", "ok")
        if p == "/" or p == "/index.html":
            return self._static("index.html", "text/html; charset=utf-8")
        if p.startswith("/static/"):
            fn = os.path.basename(p)
            return self._static_path(os.path.join(STATIC_DIR, fn))
        if p.startswith("/icons/"):
            return self._static_path(os.path.join(ICON_DIR, os.path.basename(p)))
        return self._send(404, "text/plain", "not found")

    def _send_headers_body(self, ct, data, extra):
        self._headers(200, ct, extra, length=len(data))
        try:
            self.wfile.write(data)
        except Exception:
            pass

    def _static_path(self, fp):
        if not os.path.isfile(fp):
            return self._send(404, "text/plain", "not found")
        ext = fp.rsplit(".", 1)[-1].lower()
        ct = {"html": "text/html; charset=utf-8", "css": "text/css; charset=utf-8",
              "js": "application/javascript; charset=utf-8", "svg": "image/svg+xml",
              "png": "image/png", "ttf": "font/ttf", "woff2": "font/woff2",
              "json": "application/json; charset=utf-8"}.get(ext, "application/octet-stream")
        try:
            st = os.stat(fp)
            etag = '"%x-%x"' % (int(st.st_mtime), st.st_size)
        except Exception:
            etag = None
        long_cache = "public, max-age=604800, immutable" if ext in (
            "css", "js", "woff2", "ttf", "png", "svg", "ico", "jpg", "jpeg", "webp") else "public, max-age=3600"
        if etag and self.headers.get("If-None-Match") == etag:
            self._headers(304, ct, [("ETag", etag)], length=None, cache=long_cache)
            return
        with open(fp, "rb") as f:
            data = f.read()
        self._send(200, ct, data, extra=([("ETag", etag)] if etag else None), cache=long_cache)

    def _static(self, rel, ct):
        fp = os.path.join(APP, rel)
        if not os.path.isfile(fp):
            return self._send(404, "text/plain", "missing " + rel)
        with open(fp, "rb") as f:
            data = f.read()
        self._send(200, ct, data)


if __name__ == "__main__":
    try:
        os.makedirs(SECRET_DIR, mode=0o700, exist_ok=True)
    except Exception:
        pass
    key()
    srv = ThreadingHTTPServer((HOST, PORT), H)
    print("listening on :%d" % PORT, flush=True)
    srv.serve_forever()
