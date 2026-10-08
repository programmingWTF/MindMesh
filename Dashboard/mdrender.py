#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markdown -> HTML renderer for the LobsterContext activity dashboard.

Security model:
  * raw HTML in the source is DISABLED (markdown_it html=False), so document
    content cannot inject markup - the output HTML is ours plus what
    markdown-it/Pygments escape.
  * link/image schemes are validated by markdown-it (javascript: etc blocked).
  * code fences are highlighted server-side with Pygments (which escapes).

GitHub-flavoured extras: tables, strikethrough, task lists and admonition
alerts ([!NOTE] / [!TIP] / [!IMPORTANT] / [!WARNING] / [!CAUTION]).
"""
import re
import html as _html
from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from pygments import highlight as _pyg_highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound

_ALERT_RE = re.compile(
    r'<blockquote>\s*<p>\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*(?:<br\s*/?>)?[ \t\r\n]*',
    re.I)
_ALERT_TITLES = {"note": "Note", "tip": "Tip", "important": "Important",
                 "warning": "Warning", "caution": "Caution"}
_TASK_RE = re.compile(r'<li>\[([ xX])\]\s*')
_FORMATTER = HtmlFormatter(nowrap=True)


def render_code(code, lang=""):
    """Highlight a code string with Pygments (escapes content)."""
    lexer = None
    if lang:
        try:
            lexer = get_lexer_by_name(lang, stripnl=False)
        except ClassNotFound:
            try:
                lexer = guess_lexer(code)
            except Exception:
                lexer = None
    if lexer is None:
        body = _html.escape(code)
    else:
        try:
            body = _pyg_highlight(code, lexer, _FORMATTER)
        except Exception:
            body = _html.escape(code)
    cls = "md-code"
    if lang:
        cls += " language-" + _html.escape(lang, quote=True)
    return '<div class="md-codeblock"><pre class="%s"><code>%s</code></pre></div>' % (cls, body)


class DashRenderer(RendererHTML):
    def fence(self, tokens, idx, options, env):
        token = tokens[idx]
        info = (token.info or "").strip().split()
        lang = info[0] if info else ""
        return render_code(token.content, lang) + "\n"

    def link_open(self, tokens, idx, options, env):
        t = tokens[idx]
        t.attrSet("target", "_blank")
        t.attrSet("rel", "noopener noreferrer")
        return self.renderToken(tokens, idx, options, env)


def _slug(s):
    s = re.sub(r'[^\w\u4e00-\u9fff\- ]+', '', s or '')
    s = re.sub(r'\s+', '-', s.strip()).lower()
    return s[:80] or "section"


def _build():
    md = MarkdownIt("gfm-like", renderer_cls=DashRenderer)
    md.options["html"] = False
    try:
        import linkify_it  # noqa: F401
        md.options["linkify"] = True
    except Exception:
        md.options["linkify"] = False

    def heading_ids(state):
        toks = state.tokens
        for i, t in enumerate(toks):
            if t.type == "heading_open":
                title = ""
                if i + 1 < len(toks) and toks[i + 1].type == "inline":
                    title = toks[i + 1].content or ""
                try:
                    t.attrSet("id", _slug(title))
                except Exception:
                    pass
    md.core.ruler.push("heading_ids", heading_ids)
    return md


_MD = _build()


def _alert_repl(m):
    kind = m.group(1).lower()
    return ('<blockquote class="md-alert md-alert-%s">\n'
            '<p class="md-alert-title">%s</p>\n<p>' % (kind, _ALERT_TITLES[kind]))


def _task_repl(m):
    done = m.group(1).lower() == "x"
    return '<li class="md-task%s"><input type="checkbox" disabled%s> ' % (
        " md-task-done" if done else "", " checked" if done else "")


def render(text):
    """Return rendered HTML for a markdown string."""
    out = _MD.render(text or "")
    out = _ALERT_RE.sub(_alert_repl, out)
    out = _TASK_RE.sub(_task_repl, out)
    return out


if __name__ == "__main__":
    import sys
    print(render(sys.stdin.read()))
