# 灵灵 · 「期」增量契约（episode-contract）

> 2026-09-22 定稿 ｜ 第 1 步：把「期」从页面里抽出来，变成数据 + 一个共享 shell
> **验收标准（一句话）：新增第 04 期 = 写一个 `exp/p4.html` + 在 `exp/episodes.js` 加一条；其余文件零改动。**

---

## 0 · 为什么要做这件事

期数现在硬编码在 4 个文件里（`index.html` 的 CTA 与三张期卡片、`p1/p2/p3.html` 各两份期号切换条）。
第 04 期开始就要手改 4 个文件的 6–9 处——一定会漏。做完本契约后，期数是数据，页面只是视图。

---

## 1 · 已定稿的数据文件：`frontend/exp/episodes.js`

已写好，**不要修改它的字段名**。结构：

```js
window.LING_EPISODES = {
  updated: "2026-09-22",
  episodes: [ { no, date, file, tag, title, short, motif, card:{id,title}, signal, sourceTitle, sourceUrl, judgmentCurrent, reviewPrev } ]
};
```

- **为什么是 `.js` 不是 `.json`**：JSON 要 `fetch`，而 `file://` 下 fetch 被浏览器拦。本站硬约束是「双击就能打开」。经典 script 挂全局变量，`file://` 和 `http` 都能跑，零构建。
- 数组**按 no 升序**（01 → 02 → 03 → …）。
- `short` 可能为空字符串 → 用 `title` 兜底。
- `judgmentCurrent` / `reviewPrev` 目前全为空（01–03 早于周更机制）→ 见 §3.2。

---

## 2 · 新建共享脚本：`frontend/exp-shell.js`

**形态**：经典 script（**不是 ES module**——`type="module"` 在 `file://` 下同样被拦），挂 `window.LING_SHELL`，`DOMContentLoaded` 时自动扫描并挂载。

**硬约束**
1. **零外部请求、零依赖、零构建**：不 fetch、不 import、不引 CDN、不写死任何网络地址。
2. **不注入任何 CSS**：复用各页已有的 class（`.pnav*`、`.psrc*`、`.cta*`、`.ilist` / `.icard*`）。
3. `file://` 与 `http://` 两种打开方式都要正常。
4. 脚本本身不抛异常；任一占位缺失就跳过，不影响页面其余部分。
5. 不改任何原型页的业务逻辑与文案。

### 2.1 占位与渲染规则

shell 扫描 `[data-shell]`，按下表渲染。**渲染出的 DOM 结构必须与下面逐字一致**（各页 CSS 依赖这些 class）。

#### ① `data-shell="pnav"` —— 期号切换条
各页把原有的切换条整块换成：
```html
<div class="pnav" data-shell="pnav" data-no="1" data-base="p" data-pos="top"></div>
```
属性：`data-no` 当前期号（数字）｜`data-base` 链接前缀（`exp/p1.html` 用 `p`，根目录 `index.html` 用 `exp/p`）｜`data-pos` 仅 `top` / `bottom`。

shell 填 `innerHTML` 为（首期时 `← 上一期` 渲染成 `span`；末期时 `下一期 →` 渲染成 `span`；中间时渲染 `a`）：
```html
<a class="pnav-prev" href="{base}{prevFile}">← 上一期</a>
<span class="pnav-list"><a href="{base}p1.html">01</a><a href="{base}p2.html" aria-current="page">02</a>…</span>
<a class="pnav-next" href="{base}{nextFile}">下一期 →</a>
```
- 不可点时用：`<span class="pnav-prev is-off" aria-disabled="true">← 上一期</span>`（next 同理）。
- 期号**两位数零填充**（`01`、`02`…）。
- 当前期那个 `<a>` 加 `aria-current="page"`，**只有它有**。
- 容器自身的 class / role / aria-label（`role="navigation" aria-label="期号切换"`）**不要动**，只填里面。
  （各页原有的 `<div class="pnav" role="navigation" aria-label="期号切换">` 保留这些属性。）

#### ② `data-shell="judgment"` —— 本期判断 / 上期回看
各页在**来源区 `</section>` 之后**插入：
```html
<section class="psrc" data-shell="judgment" data-no="1"></section>
```
渲染（复用 `.psrc` 系列 class，**因此不需要任何新 CSS**）：
```html
<h2 class="psrc-h">本期判断</h2>
<p class="psrc-line">{judgmentCurrent}</p>
<h2 class="psrc-h">上期回看</h2>
<p class="psrc-line">{reviewPrev}</p>
```
- **两个字段都为空 → 整个元素从 DOM 里移除**（不留空白、不留空标题）。01–03 现在就是这种情况。
- 只有其中一个空 → 只渲染有内容的那个小节。

#### ③ `data-shell="cta"`（仅 `index.html`）—— 最新一期按钮
```html
<a class="cta" data-shell="cta" data-base="exp/p"></a>
```
shell 设置 `href` 与 `innerHTML`：
```html
<span class="cta-k">直接开玩 →</span><span class="cta-v">第 03 期 · 凌晨 2:33 的告警</span>
```
- 取**期号最大**的一期；`{short || title}`；期号两位数零填充。

#### ④ `data-shell="ilist"`（仅 `index.html`）—— 期卡片列表
```html
<ul class="ilist" data-shell="ilist" data-base="exp/p"></ul>
```
按 **no 升序**填充：
```html
<li><a class="icard" href="{base}{file}">
  <span class="icard-top"><b class="icard-no">第 01 期</b><span class="icard-date">2026-09-14</span></span>
  <span class="icard-tag">拖拽分类</span>
  <span class="icard-title">你是 AI 工具合规官，8 条使用申请该不该放行</span>
  <span class="icard-go">进入 →</span>
</a></li>
```
- `第 01 期` 里的期号同样两位零填充。
- `aria-current` 不要加（这里不是当前页）。

### 2.2 期号零填充与「第 N 期」
统一规则：`String(no).padStart(2, "0")`；显示成 `第 03 期`。

---

## 3 · 各页要改的地方（这就是全部改动）

| 文件 | 要做的改动 |
|---|---|
| `frontend/exp-shell.js` | **新建**（§2 全部） |
| `frontend/index.html` | CTA 块换成 §2.1③ 占位；三期 `<li>` 整段换成 §2.1④ 占位；目录区标题「三期实验」改成「**往期实验**」；`</body>` 前加 `<script src="exp/episodes.js"></script>` 和 `<script src="exp-shell.js"></script>`；**其余一字不动** |
| `frontend/exp/p1.html` | 两份期号切换条各换成 §2.1① 占位（`data-no="1" data-base="p"`，一份 `data-pos="top"`、一份 `data-pos="bottom"`）；来源区 `</section>` 后插 §2.1② 占位；`</body>` 前加 `<script src="episodes.js"></script>` 和 `<script src="../exp-shell.js"></script>`；**原型本体、来源区文案、CSS 全部不动** |
| `frontend/exp/p2.html` | 同 p1，`data-no="2"` |
| `frontend/exp/p3.html` | 同 p1，`data-no="3"` |

### 3.1 不要做的事（越界即返工）
- ❌ 不改任何原型页的交互逻辑、文案、示例数据、样式表
- ❌ 不引入任何框架、构建步骤、外部资源
- ❌ 不删 `archive/` 里的历史版本
- ❌ 不动 `frontend/data/`（卡片快照）
- ❌ **不改「每日 / 每周」相关文案**——口径改动是单独一次决定，本轮不做
- ❌ 不新增 CSS 文件；`exp-shell.js` 不注入 CSS

### 3.2 关于 01–03 没有「本期判断 / 上期回看」
正常。这两块从第 04 期开始才有内容，现在渲染结果就是该元素不存在。

---

## 4 · 验收清单（我会逐条真跑，不是看自报）

1. **零外部请求**：CDP 网络审计，非 `file://` 请求数 = **0**（用 `file://` 与 `http://` 各跑一遍）
2. **期号切换条**：`p1` 显示 `01` 高亮 + `下一期 →`，且 `← 上一期` 是不可点 `span`；`p3` 反之；`p2` 两头都可点
3. **四页互相可达**：`index` ⇄ `p1/p2/p3`，每页顶底两条切换条都能走
4. **首页 CTA** 指向 `p3.html`，文案 `第 03 期 · 凌晨 2:33 的告警`
5. **首页列表** 三期齐全、升序、`icard` 结构完整
6. **judgment 占位在 01–03 上不产生任何可见节点**
7. **375px / 768px / 1280px 三档零横向溢出**（`scrollWidth ≤ innerWidth`）
8. **零 JS 报错**；`file://` 下也零报错
9. **尺寸回归**：切换条 `.pnav-prev` / `.pnav-next` / `.pnav-list a` 触控高度 ≥44px
10. **增量验证（最关键）**：临时加一期 `p4.html` + `episodes.js` 加一条，确认 **`index.html`、`p1-p3.html`、`exp-shell.js` 零改动** 就能出现第 04 期；验证完删掉临时文件
