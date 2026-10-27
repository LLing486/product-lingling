/* 灵灵 · 每周实验 —— 共享壳（exp-shell.js）
 *
 * 一句话：把「期」从页面里抽出来。页面只留空占位（[data-shell]），
 * 期号切换条 / 本期判断 / 首页最新一期按钮 / 首页期卡片，全由这里按
 * exp/episodes.js 渲染。新增一期 = 写一个 exp/pN.html + 在 episodes.js
 * 里加一条，其余文件零改动。
 *
 * 为什么是经典 script、不是 ES module：
 *   type="module" 在 file:// 下会被 CORS 拦，本站硬约束是「双击就能打开」。
 *   经典 script 挂全局变量，file:// 和 http:// 都能跑，也不需要构建。
 *
 * 硬约束（见 docs/episode-contract.md §2）：
 *   - 零外部请求 / 零依赖 / 零构建：不 fetch、不 import、不引 CDN、不写死网络地址
 *   - 不注入任何 CSS：只复用各页已有的 .pnav* / .psrc* / .cta* / .ilist / .icard*
 *   - 任一占位缺失、任一条数据异常，都只跳过那一处；本脚本不抛异常
 *   - 只填占位元素的内部，不动页面其余部分（容器自身的 class 与 aria 一律保留）
 */
(function () {
  'use strict';

  /* ══════════════════════════════════════════════════════
     1. 小工具
     ══════════════════════════════════════════════════════ */

  /* 契约 §2.2：期号统一两位零填充 */
  function pad(n) {
    return String(n).padStart(2, '0');
  }

  /* 期号显示：3 →「第 03 期」 */
  function issueLabel(n) {
    return '第 ' + pad(n) + ' 期';
  }

  /* 数据虽然是本地常量，仍然转义：正文里的 < > & 不该把页面结构撑坏 */
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  /* 判断「字段是否为空」：null / undefined / 纯空白都算空（契约 §2.1②） */
  function text(v) {
    return v == null ? '' : String(v).trim();
  }

  /* 期号 → 数字；取不到合法数字时返回 NaN */
  function noOf(ep) {
    return Number(ep && ep.no);
  }

  /* ══════════════════════════════════════════════════════
     2. 数据：读 window.LING_EPISODES
     ══════════════════════════════════════════════════════ */

  /* 返回按 no 升序排好的期列表。
     数据没加载 / 结构不对 / 一条都不合法 → 返回 null（＝整体跳过，不碰 DOM）。 */
  function episodes() {
    var raw = window.LING_EPISODES && window.LING_EPISODES.episodes;
    if (!raw || typeof raw.length !== 'number') return null;
    var out = [];
    for (var i = 0; i < raw.length; i++) {
      if (raw[i] && isFinite(noOf(raw[i]))) out.push(raw[i]);
    }
    if (!out.length) return null;
    out.sort(function (a, b) { return noOf(a) - noOf(b); });
    return out;
  }

  /* 按期号取一期；取不到返回 null */
  function pick(list, no) {
    for (var i = 0; i < list.length; i++) {
      if (noOf(list[i]) === no) return list[i];
    }
    return null;
  }

  /* ══════════════════════════════════════════════════════
     3. 链接拼接
     ══════════════════════════════════════════════════════ */

  /* data-base（契约 §2.1①，页面自带）：
         exp/pN.html  →  "p"       （同目录，链接就写 p2.html）
         index.html   →  "exp/p"   （指向 exp/p2.html）
     data 里的 file 是完整文件名（"p2.html"）。
     这两个 data-base 取值本身已经含了文件名首字母 p，再直接接 file 会拼出
     pp2.html，所以这里做一次归一：前缀以 p 结尾、文件名以 p 开头时，去重一次。
     （写成 data-base="" 或 "exp/" 的页面不受影响，照旧直接相接。） */
  function linkTo(base, file) {
    var b = base == null ? '' : String(base);
    var f = file == null ? '' : String(file);
    if (b.charAt(b.length - 1) === 'p' && f.charAt(0) === 'p') f = f.slice(1);
    return b + f;
  }

  /* ══════════════════════════════════════════════════════
     4. ① 期号切换条 data-shell="pnav"（契约 §2.1①）
     ══════════════════════════════════════════════════════ */

  /* 首期没有上一期 → 不可点的 span（next 同理） */
  function navEnd(cls, label, ep, base) {
    if (!ep) {
      return '<span class="' + cls + ' is-off" aria-disabled="true">' + label + '</span>';
    }
    return '<a class="' + cls + '" href="' + esc(linkTo(base, ep.file)) + '">' + label + '</a>';
  }

  function renderPnav(el, list) {
    var no = Number(el.getAttribute('data-no'));
    if (!isFinite(no)) return;
    var base = el.getAttribute('data-base') || '';

    var idx = -1, i;
    for (i = 0; i < list.length; i++) {
      if (noOf(list[i]) === no) { idx = i; break; }
    }

    var prev = null, next = null;
    if (idx >= 0) {
      prev = idx > 0 ? list[idx - 1] : null;
      next = idx < list.length - 1 ? list[idx + 1] : null;
    } else {
      /* 当前期号不在数据里（页面比数据新 / 数据被改）：按 no 就近取，别让切换条整体空掉 */
      for (i = 0; i < list.length; i++) {
        if (noOf(list[i]) < no) prev = list[i];
        if (noOf(list[i]) > no && !next) next = list[i];
      }
    }

    var items = list.map(function (ep) {
      return '<a href="' + esc(linkTo(base, ep.file)) + '"' +
        (noOf(ep) === no ? ' aria-current="page"' : '') +
        '>' + pad(noOf(ep)) + '</a>';
    }).join('');

    el.innerHTML =
      navEnd('pnav-prev', '← 上一期', prev, base) + '\n  ' +
      '<span class="pnav-list">\n    ' + items + '\n  </span>\n  ' +
      navEnd('pnav-next', '下一期 →', next, base);
  }

  /* ══════════════════════════════════════════════════════
     5. ② 本期判断 / 上期回看 data-shell="judgment"（契约 §2.1②）
        复用 .psrc 系列 class，所以不需要任何新 CSS。
     ══════════════════════════════════════════════════════ */

  function renderJudgment(el, list) {
    var no = Number(el.getAttribute('data-no'));
    if (!isFinite(no)) return;
    var ep = pick(list, no);
    var current = ep ? text(ep.judgmentCurrent) : '';
    var review = ep ? text(ep.reviewPrev) : '';

    /* 两个字段都为空（含「数据里查不到这一期」）→ 整个元素从 DOM 移除，
       不留空白、不留空标题，也不留 .psrc 的上下内边距 */
    if (!current && !review) {
      if (el.parentNode) el.parentNode.removeChild(el);
      return;
    }

    var html = '';
    if (current) {
      html += '<h2 class="psrc-h">本期判断</h2>\n  <p class="psrc-line">' + esc(current) + '</p>';
    }
    if (review) {
      if (html) html += '\n  ';
      html += '<h2 class="psrc-h">上期回看</h2>\n  <p class="psrc-line">' + esc(review) + '</p>';
    }
    el.innerHTML = html;
  }

  /* ══════════════════════════════════════════════════════
     6. ③ 首页最新一期按钮 data-shell="cta"（契约 §2.1③）
     ══════════════════════════════════════════════════════ */

  function renderCta(el, list) {
    var base = el.getAttribute('data-base') || '';
    var latest = list[list.length - 1];        /* 列表已按 no 升序，末条即期号最大 */
    el.setAttribute('href', linkTo(base, latest.file));
    var t = text(latest.short) || text(latest.title);
    el.innerHTML =
      '<span class="cta-id">' +
        '<span class="cta-k">最新一期</span>' +
        '<span class="cta-no">' + pad(noOf(latest)) + '</span>' +
      '</span>' +
      '<span class="cta-main">' +
        '<span class="cta-issue">' + esc(issueLabel(noOf(latest))) + '</span>' +
        '<span class="cta-title">' + esc(t) + '</span>' +
      '</span>' +
      '<span class="cta-go">直接开玩 →</span>';
  }

  /* ══════════════════════════════════════════════════════
     7. ④ 首页期卡片列表 data-shell="ilist"（契约 §2.1④）
     ══════════════════════════════════════════════════════ */

  function renderIlist(el, list) {
    var base = el.getAttribute('data-base') || '';
    el.innerHTML = list.map(function (ep) {
      var th = ep.theme || {};
      var vars = ' style="' +
        '--c-accent:' + esc(th.accent || '#8A6508') + ';' +
        '--c-accent-ink:' + esc(th.accentInk || '#8A6508') + '"';
      return '<li class="irow"><a class="irow-link" href="' + esc(linkTo(base, ep.file)) + '"' + vars + '>\n' +
        '  <span class="irow-bar" aria-hidden="true"></span>\n' +
        '  <span class="irow-no">' + pad(noOf(ep)) + '</span>\n' +
        '  <span class="irow-body">\n' +
        '    <span class="irow-title">' + esc(ep.title) + '</span>\n' +
        '    <span class="irow-meta">' + esc(ep.date) + ' · ' + esc(ep.motif) + '</span>\n' +
        '  </span>\n' +
        '  <span class="irow-side">\n' +
        '    <span class="irow-tag">' + esc(ep.tag) + '</span>\n' +
        '    <span class="irow-go">进入 →</span>\n' +
        '  </span>\n' +
        '</a></li>';
    }).join('\n');
  }

  /* ══════════════════════════════════════════════════════
     8. 扫描并挂载
     ══════════════════════════════════════════════════════ */

  var RENDERERS = {
    pnav: renderPnav,
    judgment: renderJudgment,
    cta: renderCta,
    ilist: renderIlist
  };

  function mount(scope) {
    try {
      var list = episodes();
      if (!list) return false;                       /* 没数据：一个占位都不碰 */
      var root = scope || document;
      var nodes = root.querySelectorAll ? root.querySelectorAll('[data-shell]') : [];
      for (var i = 0; i < nodes.length; i++) {
        var el = nodes[i];
        var fn = RENDERERS[el.getAttribute('data-shell')];
        if (!fn) continue;                           /* 未知占位：跳过 */
        try {
          fn(el, list);
        } catch (e) {
          /* 单处渲染失败不牵连其余占位，更不牵连页面 */
        }
      }
      return true;
    } catch (e) {
      return false;
    }
  }

  function boot() {
    mount(document);
  }

  /* 正常是页面里同步加载：此时 readyState 还是 loading，挂到 DOMContentLoaded。
     若脚本被动态插入（readyState 已不是 loading），立刻补挂一次，免得漏掉。 */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  /* 暴露给自检脚本（无副作用，不改变上面的行为） */
  window.LING_SHELL = {
    mount: mount,
    episodes: episodes,
    linkTo: linkTo,
    pad: pad,
    issueLabel: issueLabel
  };
})();
