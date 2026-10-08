'use strict';
/* LobsterContext dashboard · extensions (files browser, commit diffs, auth).
   Builds on the original dark dashboard; reuses esc/color/iconOf/rel from it. */
(function () {
  var E = window;
  function esc(s) { return (E.esc ? E.esc(s) : String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]; })); }
  function iconOf(n) { return E.iconOf ? E.iconOf(n) : null; }
  function isSvg(p) { return E.isSvg ? E.isSvg(p) : (p && p.indexOf('.svg') > 0); }
  function color(n) { return E.color ? E.color(n) : '#8b93a1'; }
  function relOf(iso) { return E.rel ? E.rel(iso) : (iso || ''); }
  function hexA(h, a) { return E.hexA ? E.hexA(h, a) : h; }

  var ST = { authed: false, view: 'overview', tree: {}, sel: '' };

  var API_BASE = E.MINDMESH_API || '';
  function api(path, opts) {
    return fetch(API_BASE + path, Object.assign({ credentials: 'include', headers: { 'Accept': 'application/json' } }, opts || {}))
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { status: r.status, ok: r.ok, data: j }; }); });
  }
  function badge(agent, col) { return E.badgeHTML ? E.badgeHTML(agent, col) : '<span class="badge" style="background:' + color(agent) + '">' + esc(agent) + '</span>'; }

  /* ---------------- modal + auth ---------------- */
  function modal(html, narrow) {
    var m = document.createElement('div'); m.className = 'mask2';
    m.innerHTML = '<div class="modal2' + (narrow ? ' narrow' : '') + '" style="position:relative"><span class="mx">&times;</span>' + html + '</div>';
    document.body.appendChild(m);
    function close() { m.remove(); }
    m.addEventListener('click', function (e) { if (e.target === m) close(); });
    m.querySelector('.mx').onclick = close;
    return { node: m, close: close };
  }
  function loginModal(msg) {
    return new Promise(function (resolve) {
      var M = modal('<h3>🔒 需要密码</h3><p class="msub">' + esc(msg || '该内容在受保护的记忆区。请输入管理密码（NAS sudo 密码）解锁，本浏览器会记住登录状态。') + '</p>' +
        '<input type="password" autocomplete="current-password" placeholder="密码"><div class="merr"></div>' +
        '<div class="mrow"><a class="fbtn" id="lc">取消</a><a class="fbtn primary" id="lo">解锁</a></div>', true);
      var inp = M.node.querySelector('input'), err = M.node.querySelector('.merr');
      inp.focus();
      function done(v) { M.close(); resolve(v); }
      M.node.querySelector('#lc').onclick = function () { done(false); };
      function submit() {
        if (!inp.value) return; err.textContent = '验证中…';
        api('/api/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ password: inp.value }) })
          .then(function (r) { if (r.ok) { ST.authed = true; done(true); } else if (r.status === 429) err.textContent = '尝试过多，请 10 分钟后再试。'; else { err.textContent = '密码不正确。'; inp.select(); } });
      }
      M.node.querySelector('#lo').onclick = submit;
      inp.onkeydown = function (e) { if (e.key === 'Enter') submit(); };
    });
  }
  function ensureAuth(msg) { if (ST.authed) return Promise.resolve(true); return loginModal(msg).then(function (ok) { refreshAuthUI(); return ok; }); }
  function refreshAuthUI() {
    var b = document.getElementById('authbtn'); if (!b) return;
    b.textContent = ST.authed ? '🔓 已解锁 · 点此退出' : '🔒 解锁记忆';
    b.classList.toggle('on', ST.authed);
  }

  /* ---------------- views ---------------- */
  function setView(v) {
    ST.view = v; document.body.setAttribute('data-view', v);
    ['overview', 'files', 'commits'].forEach(function (x) {
      var s = document.getElementById('view-' + x);
      if (s) s.classList.toggle('hidden', x !== v);
      var n = document.querySelector('.nv[data-view="' + x + '"]');
      if (n) n.classList.toggle('on', x === v);
    });
    if (v === 'files' && !document.getElementById('ftree').dataset.ready) { renderTree(); document.getElementById('ftree').dataset.ready = '1'; }
    if (v === 'files') emptyViewer();
    if (v === 'commits') renderCommits();
  }

  /* ---------------- files ---------------- */
  function humanSize(n) { if (n == null) return ''; var u = ['B', 'KB', 'MB', 'GB'], i = 0, v = n; while (v >= 1024 && i < u.length - 1) { v /= 1024; i++; } return (i ? v.toFixed(1) : v) + ' ' + u[i]; }
  function nodeEl(name, type, priv, path) {
    var n = document.createElement('div');
    n.className = 'fnode' + (path === ST.sel ? ' cur' : '');
    n.setAttribute('data-path', path);
    n.innerHTML = '<span class="fi">' + (type === 'dir' ? '📁' : '📄') + '</span><span class="fn">' + esc(name) + '</span>';
    if (type === 'dir') {
      n.onclick = function (ev) {
        ev.stopPropagation();
        var sib = n.nextElementSibling;
        if (sib && sib.classList.contains('fkids')) { sib.classList.toggle('hidden'); return; }
        api('/api/tree?path=' + encodeURIComponent(path)).then(function (r) {
          if (r.status === 403) { ensureAuth('该目录在记忆区，需要密码。').then(function (ok) { if (ok) n.onclick(ev); }); return; }
          var box = document.createElement('div'); box.className = 'fkids';
          n.after(box);
          fillDir(path, box);
        });
      };
    } else { n.onclick = function () { openFile(path); }; }
    return n;
  }
  function renderTree() {
    var box = document.getElementById('ftree'); if (!box) return;
    /* 2026-10-08: 树主体收进 #ftreebody，搜索框/结果框常驻不被重绘吞掉 */
    var body = box.querySelector('#ftreebody');
    if (!body) { body = document.createElement('div'); body.id = 'ftreebody'; box.appendChild(body); }
    body.innerHTML = '';
    var root = document.createElement('div'); root.className = 'fnode';
    root.innerHTML = '<span class="fi">🏠</span><span class="fn">仓库根目录</span>';
    root.onclick = function () { collapseTree(); };
    body.appendChild(root);
    var holder = document.createElement('div'); holder.className = 'frootkids';
    body.appendChild(holder);
    fillDir('', holder);
  }
  /* 2026-10-08: 根目录点击改为「全部收起」，不再重建整棵树（原实现会弄丢展开状态） */
  function collapseTree() {
    var kids = document.querySelectorAll('#ftreebody .fkids');
    Array.prototype.forEach.call(kids, function (k) { k.classList.add('hidden'); });
  }
  function fillDir(path, holder, cb) {
    holder.innerHTML = '<div class="fnode" style="opacity:.55"><span class="fi">…</span><span class="fn">加载中</span></div>';
    api('/api/tree?path=' + encodeURIComponent(path)).then(function (r) {
      if (r.status === 403) { holder.innerHTML = '<div class="fnode"><span class="fi">📁</span><span class="fn">需要密码</span></div>'; return; }
      holder.innerHTML = '';
      (r.data.entries || []).forEach(function (e) { holder.appendChild(nodeEl(e.name, e.type, e.private, path + e.name)); });
      if (cb) cb();
    });
  }

  /* 2026-10-08: 打开文件时左侧树自动展开到该文件并高亮（.cur） */
  function cssSel(p) { return (window.CSS && CSS.escape) ? CSS.escape(p) : p.replace(/"/g, '\\"'); }
  function markCur(path) {
    var n = document.querySelector('.fnode[data-path="' + cssSel(path) + '"]');
    if (n) { n.classList.add('cur'); try { n.scrollIntoView({ block: 'nearest' }); } catch (e) {} }
  }
  function revealPath(path) {
    var box = document.getElementById('ftree'); if (!box) return;
    var body = box.querySelector('#ftreebody');
    if (!body) { renderTree(); body = box.querySelector('#ftreebody'); }
    if (!body) return;
    /* 搜索态先退出，回到目录树 */
    var res = document.getElementById('fresults');
    if (res && !res.classList.contains('hidden')) { var fs = document.getElementById('fsearch'); if (fs) fs.value = ''; showResults(null, ''); }
    var segs = path.split('/');
    var holder = body.querySelector('.frootkids');
    if (!holder) return;
    var prefix = '', i = 0;
    markCur(path);
    function step() {
      if (i >= segs.length - 1) { markCur(path); return; } /* 最后一段是文件本身 */
      prefix += segs[i] + '/';
      var dirNode = null;
      Array.prototype.forEach.call(holder.children, function (n) { if (n.getAttribute('data-path') === prefix) dirNode = n; });
      if (!dirNode) { markCur(path); return; } /* 树未加载到那层，尽力而为 */
      var sib = dirNode.nextElementSibling;
      var kidbox;
      if (sib && sib.classList.contains('fkids')) {
        kidbox = sib; sib.classList.remove('hidden');
        if (kidbox.children.length) { holder = kidbox; i++; step(); return; }
      } else { kidbox = document.createElement('div'); kidbox.className = 'fkids'; dirNode.after(kidbox); }
      fillDir(prefix, kidbox, function () { holder = kidbox; i++; step(); });
    }
    step();
  }
  function openFile(path) {
    ST.sel = path;
    Array.prototype.forEach.call(document.querySelectorAll('.fnode.cur'), function (n) { n.classList.remove('cur'); });
    markCur(path);
    revealPath(path);
    var view = document.getElementById('fview');
    view.innerHTML = '<div class="fbar"><span class="fcrumb">' + esc(path) + '</span></div><div class="fbody"><div class="lockbox">加载中…</div></div>';
    api('/api/file?path=' + encodeURIComponent(path)).then(function (r) {
      if (r.status === 403 || (r.data && r.data.private && !r.data.authed)) {
        ensureAuth('该文件在受保护的记忆区，需要密码。').then(function (ok) { if (ok) openFile(path); });
        return;
      }
      if (!r.ok) { view.querySelector('.fbody').innerHTML = '<div class="lockbox">读取失败：' + esc(r.data.error || r.status) + '</div>'; return; }
      var d = r.data;
      var crumbs = '<span class="fcrumb">' + path.split('/').map(function (s, i, a) {
        var sub = a.slice(0, i + 1).join('/');
        return '<a data-p="' + esc(sub) + '">' + esc(s) + '</a>';
      }).join(' / ') + '</span>';
      var bar = '<div class="fbar"><button class="fbtn menubtn" id="ftoggle">☰ 目录</button>' + crumbs +
        '<span class="mono" style="color:var(--dim2);font-size:11.5px">' + humanSize(d.size) + '</span>' +
        (d.binary ? '' : '<span class="tgl2" id="tg2"><button data-m="render"' + (d.html ? ' class="on"' : '') + '>渲染</button><button data-m="source"' + (d.html ? '' : ' class="on"') + '>源码</button></span>') +
        '<a class="fbtn" target="_blank" href="' + API_BASE + '/api/raw?path=' + encodeURIComponent(path) + '">下载</a></div>';
      view.innerHTML = bar + '<div class="fbody" id="fb2"></div>';
      wireToggle(); toggleDrawer(false);
      view.querySelectorAll('.fcrumb a').forEach(function (a) { a.onclick = function () { openFile(a.getAttribute('data-p')); }; });
      var body = view.querySelector('#fb2');
      function paint(mode) {
        if (d.binary) {
          body.innerHTML = '<div class="lockbox">二进制文件 · <a class="fbtn" target="_blank" href="' + API_BASE + '/api/raw?path=' + encodeURIComponent(path) + '">下载</a>' +
            (['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'ico'].indexOf(d.ext) >= 0 ? '<br><br><img style="max-width:100%;border-radius:10px" src="' + API_BASE + '/api/raw?path=' + encodeURIComponent(path) + '">' : '') + '</div>';
          return;
        }
        if (mode === 'render' && d.html) { body.innerHTML = '<article class="md">' + d.html + '</article>'; return; }
        var lines = (d.raw || '').split('\n'), shown = lines.slice(0, 5000), h = '<div class="srcline">';
        for (var i = 0; i < shown.length; i++) h += '<span class="lno">' + (i + 1) + '</span>' + esc(shown[i]) + '\n';
        h += '</div>';
        body.innerHTML = '<pre class="src">' + h + '</pre>' + (lines.length > shown.length ? '<p class="msub">已截断，仅显示前 5000 行。</p>' : '');
      }
      paint(d.html ? 'render' : 'source');
      var tg = view.querySelector('#tg2');
      if (tg) tg.onclick = function (e) { var b = e.target.closest('button'); if (!b) return; Array.prototype.forEach.call(tg.children, function (x) { x.classList.toggle('on', x === b); }); paint(b.getAttribute('data-m')); };
    });
  }

  /* ---------------- commits + diff ---------------- */
  function getData() { if (E.DATA) return Promise.resolve(E.DATA); return api('/api/summary').then(function (r) { E.DATA = r.data; return r.data; }); }
  function renderCommits() {
    var box = document.getElementById('vcommits'); if (!box) return;
    box.innerHTML = '<div class="lockbox">加载中…</div>';
    getData().then(function (d) {
      var list = (d && d.commits) || [];
      /* 2026-10-08: 分页渲染，避免仓库变大后一次性宣染全部提交 */
      var PAGE = 50, page = ST.commitPage || 1;
      var shown = list.slice(0, page * PAGE);
      var h = '<div class="clist">';
      shown.forEach(function (c) {
        h += '<div class="crow" data-h="' + c.hash + '">' + badge(c.agent) +
          '<span class="cmsg">' + esc(c.subject || '(no message)') + '</span>' +
          '<span class="chip">' + c.nfiles + ' 文件</span>' +
          '<span class="ct">' + esc(relOf(c.date)) + ' · <span class="mono">' + esc(c.short) + '</span></span></div>';
      });
      if (list.length > shown.length) {
        h += '<div class="lockbox" style="cursor:pointer"><span id="cmore" class="fbtn primary">加载更多（还有 ' + (list.length - shown.length) + ' 条）</span></div>';
      }
      box.innerHTML = h + '</div>';
      var more = box.querySelector('#cmore');
      if (more) more.onclick = function (e) { e.stopPropagation(); ST.commitPage = page + 1; renderCommits(); };
      box.querySelectorAll('.crow').forEach(function (row) { row.onclick = function () { openDiff(row.getAttribute('data-h')); }; });
    });
  }
  function openDiff(sha) {
    var M = modal('<h3>提交改动</h3><p class="msub mono">' + esc(sha) + '</p><div id="difbody"><div class="lockbox">加载中…</div></div>');
    api('/api/commit?sha=' + encodeURIComponent(sha)).then(function (r) {
      var b = M.node.querySelector('#difbody');
      if (!r.ok) { b.innerHTML = '<div class="lockbox">读取失败</div>'; return; }
      var d = r.data;
      var head = '<div class="msg" style="font-size:14.5px;font-weight:650">' + esc(d.subject || '') + '</div>' +
        '<div class="det"><span>' + esc(d.agent) + '</span><span>' + esc(d.author) + '</span><span>' + esc(relOf(d.date)) + '</span><span class="mono">' + esc(d.short) + '</span></div>';
      if (d.private && !d.authed) {
        b.innerHTML = head + '<div class="lockbox"><div class="big">🔒</div>该提交涉及记忆区。<br><br><a class="fbtn primary" id="unl">解锁查看改动</a></div>';
        b.querySelector('#unl').onclick = function () { ensureAuth('该提交涉及记忆区，需要密码。').then(function (ok) { if (ok) { M.close(); openDiff(sha); } }); };
        return;
      }
      var files = '<table class="files2">' + (d.files || []).map(function (f) {
        return '<tr><td class="p"><a data-p="' + esc(f.path) + '">' + esc(f.path) + '</a></td><td class="a">' + esc(f.add) + '</td><td class="d">' + esc(f.del) + '</td></tr>';
      }).join('') + '</table>';
      var patches = (d.files || []).map(function (f) {
        return '<details' + (d.files.length === 1 ? ' open' : '') + '><summary style="cursor:pointer;color:var(--dim);font-size:12.5px;padding:4px 0"><span class="openp" data-p="' + esc(f.path) + '" title="打开文件">↗</span> ' + esc(f.path) + '</summary><div class="patch">' + diffHTML(f.patch || '(无文本差异)') + '</div></details>';
      }).join('');
      b.innerHTML = head + '<h4 style="margin:14px 0 4px;font-size:13px;color:var(--dim)">改动文件 ' + (d.files || []).length + ' <span style="color:var(--dim2);font-weight:400">（点路径可跳转）</span></h4>' + files + patches;
      Array.prototype.forEach.call(b.querySelectorAll('[data-p]'), function (a) {
        a.addEventListener('click', function (ev) { ev.preventDefault(); ev.stopPropagation(); M.close(); jumpToFile(a.getAttribute('data-p')); });
      });
    });
  }
  function diffHTML(t) {
    return String(t).split('\n').map(function (l) {
      var c = '';
      if (l.indexOf('@@') === 0) c = 'h';
      else if (l.indexOf('+++') === 0 || l.indexOf('---') === 0) c = 'm';
      else if (l.charAt(0) === '+') c = 'a';
      else if (l.charAt(0) === '-') c = 'd';
      return '<i' + (c ? ' class="' + c + '"' : '') + '>' + esc(l) + '</i>';
    }).join('');
  }

  function handleHash() {
    var h = (location.hash || '').replace(/^#\/?/, '');
    var parts = h.split('/'), head = parts[0], rest = parts.slice(1).join('/');
    if (head === 'files') { setView('files'); if (rest) openFile(decodeURI(rest)); }
    else if (head === 'commits') { setView('commits'); if (rest) openDiff(rest); }
    else { setView('overview'); }
  }

  /* ---------------- navigation (hash = single source of truth) ----------------
     2026-10-08: 顶部导航改为写 hash，由 hashchange 统一驱动视图切换。
     修复：先看文件再点概览、再点同名文件时 hash 不变导致不跳转的问题。 */
  function navHash(v) { return v === 'overview' ? '#/' : '#/' + v; }
  function goView(v) {
    var t = navHash(v);
    if (location.hash === t || (v === 'overview' && (location.hash === '' || location.hash === '#'))) { handleHash(); return; }
    location.hash = t;
  }
  function jumpToFile(path) {
    var t = '#/files/' + encodeURI(path);
    var cur = (location.hash || '').replace(/^#\/files\//, '');
    if (location.hash === t || decodeURI(cur) === path) { handleHash(); return; }
    location.hash = t;
  }
  function decorateCommits() {
    var box = document.getElementById('commits'); if (!box) return;
    Array.prototype.forEach.call(box.querySelectorAll('.f'), function (el) {
      if (el.getAttribute('data-done')) return;
      el.setAttribute('data-done', '1');
      var parts = (el.textContent || '').split(' · ');
      el.innerHTML = parts.map(function (p) {
        var s = p.trim();
        if (/^\+\d+$/.test(s)) return '<span style="opacity:.55">' + s + '</span>';
        return '<span data-p="' + s.replace(/"/g, '&quot;') + '" style="cursor:pointer">' + s + '</span>';
      }).join('<span style="opacity:.4"> · </span>');
    });
    Array.prototype.forEach.call(box.querySelectorAll('.fil div'), function (el) { el.style.cursor = 'pointer'; });
  }
  function wireJumps() {
    var box = document.getElementById('commits');
    if (box && window.MutationObserver) {
      new MutationObserver(decorateCommits).observe(box, { childList: true });
      decorateCommits();
    }
    document.addEventListener('click', function (e) {
      var t = e.target; if (!t || !t.closest) return;
      var hit = null;
      if ((hit = t.closest('#commits .fil > div'))) { e.preventDefault(); e.stopPropagation(); jumpToFile(hit.textContent.trim()); return; }
      if ((hit = t.closest('#commits .f span[data-p]'))) { e.preventDefault(); e.stopPropagation(); jumpToFile(hit.getAttribute('data-p')); return; }
      if ((hit = t.closest('#commits .cmt .det .mono'))) { e.preventDefault(); e.stopPropagation(); openDiff(hit.textContent.trim()); return; }
      if ((hit = t.closest('#hot .hm'))) { e.preventDefault(); e.stopPropagation(); var n = hit.querySelector('.n'); if (n) jumpToFile((n.textContent || '').trim()); return; }
    }, true);
  }

  /* ---------------- mobile drawer ---------------- */
  function ensureDrawer() {
    if (document.getElementById('drawerMask')) return;
    var m = document.createElement('div'); m.id = 'drawerMask';
    m.onclick = function () { toggleDrawer(false); };
    document.body.appendChild(m);
  }
  function toggleDrawer(force) {
    var t = document.getElementById('ftree'); if (!t) return;
    var open = (typeof force === 'boolean') ? force : !t.classList.contains('open');
    t.classList.toggle('open', open);
    var m = document.getElementById('drawerMask'); if (m) m.classList.toggle('show', open);
  }
  function wireToggle() {
    var b = document.getElementById('ftoggle'); if (!b) return;
    b.onclick = function (e) { e.stopPropagation(); toggleDrawer(); };
  }
  function emptyViewer() {
    var v = document.getElementById('fview'); if (!v || v.querySelector('.fbar')) return;
    v.innerHTML = '<div class="fbar"><button class="fbtn menubtn" id="ftoggle">☰ 目录</button>' +
      '<span class="fcrumb">选择一个文件查看</span></div>' +
      '<div class="fbody"><div class="lockbox">点左上角「☰ 目录」打开文件树</div></div>';
    wireToggle();
  }

  /* ---------------- file search (2026-10-08) ---------------- */
  function wireFSearch() {
    var fs = document.getElementById('fsearch');
    if (!fs) return;
    var t = null;
    fs.oninput = function () {
      var qv = fs.value.trim();
      clearTimeout(t);
      if (!qv) { showResults(null, ''); return; }
      t = setTimeout(function () {
        api('/api/fsearch?q=' + encodeURIComponent(qv)).then(function (r) {
          if (fs.value.trim() !== qv) return; /* 输入已变，丢弃过期结果 */
          showResults(r.ok ? (r.data.results || []) : [], qv);
        });
      }, 220);
    };
  }
  function showResults(list, qv) {
    var res = document.getElementById('fresults');
    var body = document.getElementById('ftreebody');
    if (!res) return;
    if (!qv || !list) {
      res.classList.add('hidden'); res.innerHTML = '';
      if (body) body.classList.remove('hidden');
      return;
    }
    if (body) body.classList.add('hidden');
    res.classList.remove('hidden');
    if (!list.length) { res.innerHTML = '<div class="fsrch-empty">没有匹配的文件</div>'; return; }
    var h = '';
    list.forEach(function (it) {
      if (it.truncated) { h += '<div class="fsrch-empty">匹配过多，仅显示前 120 条…</div>'; return; }
      var name = it.path.split('/').pop();
      h += '<div class="fnode" data-p="' + esc(it.path) + '" title="' + esc(it.path) + '"><span class="fi">📄</span><span class="fn">' + esc(name) + '</span>' + (it.private ? '<span class="frp">🔒</span>' : '') + '</div>';
    });
    res.innerHTML = h;
    Array.prototype.forEach.call(res.querySelectorAll('.fnode'), function (n) {
      n.onclick = function () { openFile(n.getAttribute('data-p')); };
    });
  }

  /* ---------------- boot ---------------- */
  function boot() {
    api('/api/me').then(function (r) { ST.authed = !!(r.data && r.data.authed); refreshAuthUI(); });
    var nav = document.getElementById('nav');
    if (nav) {
      nav.querySelectorAll('.nv').forEach(function (n) { n.onclick = function () { goView(n.getAttribute('data-view')); }; });
      var ab = document.getElementById('authbtn');
      ab.onclick = function () {
        if (ST.authed) { api('/api/logout', { method: 'POST' }).then(function () { ST.authed = false; refreshAuthUI(); if (ST.view === 'files') renderTree(); }); }
        else { ensureAuth('解锁后可查看记忆区文件与提交改动。'); }
      };
    }
    setView('overview');
    ensureDrawer();
    wireJumps();
    wireFSearch();
    window.addEventListener('hashchange', handleHash);
    window.__ll = { openFile: openFile, handleHash: handleHash, setView: setView, api: api, ST: ST };
    handleHash();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
