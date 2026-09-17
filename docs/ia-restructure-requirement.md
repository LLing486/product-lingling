# 灵灵 · 信息架构重整（本轮需求契约）

> 用户 2026-09-17 反馈定稿。本轮只做「页面的形」，不做新内容、不接模型、不改后端路由。
> 开发一律用 CC 派任务；改前先备份；旧版留在 `frontend/archive/`。

## 一、用户原话与根因

> 「页面排版有点混乱，新用户第一眼不知道这个网页是干什么的。各个页面之间的跳转逻辑也不是很流畅，进入机会卡页面后回不到原型试用了。原型默认嵌入页面中，用起来不舒服，我觉得默认就全屏，然后页面底部或者顶部可以切换原型。合适的位置可以进入卡片浏览页面以及完整的信息清单页面会更好。」

**根因（已核实）**：
1. 首页第一句话就是「第 03 期 · 用实时语音智能体替代运维值班工程师…」——把「杂志内页」当成了封面，新用户先被塞进某一期。
2. 原型被嵌在壳页的 `sandbox` iframe 里，壳有刊头/场景/来源、内容是另一页，两层页面互不知情。
3. `frontend/cards.html` 全页**没有任何回站内的链接**（只有卡片原文外链）——进去只能靠浏览器后退。
4. 没有全局导航，四个页面之间是单向、有去无回的。

**用户拍板**：方案 A —— 删掉壳页，原型页自己做全屏，少一层、不维护两份刊头。

## 二、目标信息架构（四页 + 一条统一导航）

| 页面 | 文件 | 定位 |
|---|---|---|
| 封面 | `frontend/index.html` | 说清「灵灵是什么」+ 最新一期入口 + 三期目录 + 去卡片 |
| 原型 | `frontend/exp/p1.html` `p2.html` `p3.html` | 全屏可玩，顶部/底部切期，底部是这一期的灵感来源 |
| 机会卡 | `frontend/cards.html` | 保留现有开卡体验，加导航 + 深链 + 去清单的入口 |
| 全部卡片清单 | `frontend/cards-all.html`（新建） | 210 张卡按日期倒序，可筛方向、可搜索、点开看卡 |

**站内任何页面都能一步回到任何其他页面**——这条是本轮的核心验收项。

## 三、统一顶栏（逐字照抄，四个页面 + 三个原型页共 7 处）

结构必须是下面这段（只改 `href` 与 `aria-current`）：

```html
<nav class="lnav" aria-label="站点导航">
  <a class="lnav-brand" href="{INDEX}">灵灵</a>
  <span class="lnav-sep" aria-hidden="true"></span>
  <a class="lnav-i" href="{INDEX}"{CUR_INDEX}>全部实验</a>
  <a class="lnav-i" href="{CARDS}"{CUR_CARDS}>机会卡</a>
  <a class="lnav-i" href="{CARDS_ALL}"{CUR_ALL}>全部卡片</a>
</nav>
```

样式必须是下面这段（放在该页自己 `<style>` 的末尾，类名不得改动）：

```css
.lnav{position:sticky;top:0;z-index:9999;display:flex;align-items:center;gap:16px;flex-wrap:wrap;
  padding:6px 14px;background:#12141c;border-bottom:1px solid rgba(255,255,255,.14);
  font-family:inherit;font-size:13px;line-height:1}
.lnav a{color:rgba(255,255,255,.74);text-decoration:none;display:inline-flex;align-items:center;
  min-height:44px;padding:0 2px}
.lnav a:hover{color:#fff;text-decoration:underline}
.lnav a:focus-visible{color:#fff;outline:2px solid #7cc4ff;outline-offset:2px;border-radius:3px}
.lnav-brand{font-weight:700;color:#fff!important;letter-spacing:.04em}
.lnav-sep{width:1px;height:16px;background:rgba(255,255,255,.22)}
.lnav-i[aria-current="page"]{color:#fff;font-weight:600}
```

- 深色条在浅色页（`cards.html`）与深色页上都用**同一套颜色**，这是刻意的统一标识，不要为配合页面主题改色。
- `{INDEX}/{CARDS}/{CARDS_ALL}` 的取值：
  - 在 `frontend/*.html` → `index.html` / `cards.html` / `cards-all.html`
  - 在 `frontend/exp/*.html` → `../index.html` / `../cards.html` / `../cards-all.html`
- `{CUR_*}`：当前页所在的项写 ` aria-current="page"`，其余三项为空串。
- 顶栏必须是 `<body>` 的第一个元素（原型页里放在最前，不要放进原型自己的容器里）。

## 四、封面 `frontend/index.html`（改造，不再是壳）

从上到下：

1. 统一顶栏
2. **灵灵是什么**（一到两句，看得懂、不吹）
   - 主标题：`灵灵`
   - 副标题：`每天从 AI 行业的真实信号里，挑一个做成你能上手玩的小实验。`
   - 第三行（小字、克制）：`实验性内容 · 示例数据与规则模拟 · 本轮未接入真实模型`
3. **最新一期大按钮**：`直接开玩 第 03 期 · 凌晨 2:33 的告警` → `exp/p3.html`
   - 按钮下方一行小字：`全屏打开，约 1 分钟走完`
4. **三期目录**（三张卡片，每张：`第 0N 期` + 日期 + 形式标签 + 一句话标题 + `进入 →`）
   - 01 · 2026-09-14 · 拖拽分类 · 你是 AI 工具合规官，8 条使用申请该不该放行
   - 02 · 2026-09-15 · 参数调整 · 接手 2011 年的老系统，三个旋钮决定它能答什么
   - 03 · 2026-09-16 · 分支选择 · 凌晨 2:33 的告警，AI 能接管到哪一步
   - 每张卡整块可点（`<a>` 包住），触控高度 ≥44px
5. **去卡片区**：一行两个入口
   - `看今天的 2 张机会卡 →` → `cards.html`
   - `浏览全部 210 张卡片 →` → `cards-all.html`
   - 数字要**动态取**（`/api/cards?page=1&page_size=1` 的 `total`），取不到就写「全部卡片」不带数字
6. 页脚：`灵灵 · 每日机会卡 + 每日灵感实验` / `旧版界面：v1 / v2 / v3`（指向 `archive/*.html`）/ `源码与说明：GitHub`

**必须做到的**：
- 首屏（375×667 不滚动）就能看到主标题 + 副标题 + 「直接开玩」按钮
- 封面**不放 iframe**、不放任何原型内容
- 原壳里的「灵感来源 / 一句话场景 / 玩法 / 数据说明」文案不属于封面，交给原型页（见第五节）

## 五、原型页 `frontend/exp/p1.html` `p2.html` `p3.html`

### 5.1 顶部

1. 统一顶栏（`../` 相对路径）
2. **期号切换条**：紧跟顶栏，一行三个部分：

```html
<div class="pnav" role="navigation" aria-label="期号切换">
  <a class="pnav-prev" href="{PREV}"{PREV_ATTR}>← 上一期</a>
  <span class="pnav-list">
    <a href="p1.html"{CUR1}>01</a><a href="p2.html"{CUR2}>02</a><a href="p3.html"{CUR3}>03</a>
  </span>
  <a class="pnav-next" href="{NEXT}"{NEXT_ATTR}>下一期 →</a>
</div>
```

- 首期 `p1.html` 的上一期、末期 `p3.html` 的下一期：渲染成不可点的 `<span class="pnav-prev is-off" aria-disabled="true">← 上一期</span>`（不要用灰掉但可点的 `<a>`）
- 当前期在 `.pnav-list` 里标 `aria-current="page"`
- 样式（同样放 `<style>` 末尾，类名不改）：

```css
.pnav{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;
  padding:10px 14px;border-bottom:1px solid rgba(0,0,0,.08);font-size:14px}
.pnav a,.pnav span{display:inline-flex;align-items:center;min-height:44px}
.pnav-prev,.pnav-next{font-weight:600;text-decoration:none}
.pnav-prev.is-off,.pnav-next.is-off{opacity:.38}
.pnav-list{display:inline-flex;gap:6px}
.pnav-list a{min-width:44px;justify-content:center;text-decoration:none;border-radius:8px;padding:0 6px}
.pnav-list a[aria-current="page"]{font-weight:700;background:rgba(0,0,0,.07);text-decoration:none}
```

- 配色沿用该原型页自己的主题变量；上面骨架里的 `rgba(0,0,0,.08)` 若在深色主题上不可见，可换成该页的边框变量，**但结构、类名、尺寸不变**。

### 5.2 中间

原型原有内容**原样保留**，不做任何功能改动、不删不减。本轮原型页只加壳（顶栏 + 切换条 + 底部来源区）。

### 5.3 底部（在页面最后，等于「再玩一次」按钮之后）

**A. 再放一条切换条**（与 5.1 结构完全相同，方便玩完接着翻）

**B. 灵感来源区**——把原壳页里这一期的来源文案搬过来（内容见下），结构：

```html
<section class="psrc" aria-label="这一期的灵感来源">
  <h2 class="psrc-h">这一期的灵感来源</h2>
  <p class="psrc-meta">{日期} · 机会卡《{卡标题}》</p>
  <p class="psrc-line"><b>原始信号：</b>{原始信号原文}</p>
  <p class="psrc-note">以上是机会卡与行业信号的真实记录，未作改写、未加演绎。</p>
  <p class="psrc-line"><b>灵灵据此延伸的设想：</b>{延伸设想原文}</p>
  <p class="psrc-note">{这一段是二次创作的声明原文}</p>
  <p class="psrc-links">
    <a href="{原文链接}" target="_blank" rel="noopener noreferrer">阅读原文 ↗</a>
    <a href="../cards.html?id={卡片ID}">看这张机会卡 ›</a>
    <a href="../cards-all.html">全部机会卡 ›</a>
  </p>
  <p class="psrc-data">示例数据 · 规则模拟 —— 本期的题面、参数关系与分支结局都由页面本地规则算出，未接入真实模型，无后端调用、无 API key、无外部请求。</p>
</section>
```

三期要填的具体内容（**原文照抄，不得改写**）：

- **p1**（第 01 期 · 2026-09-14 · 卡片 ID `203`）
  - 卡标题：`面向 AI 编程助手的军事/双用途滥用检测与合规审计平台`
  - 原始信号：`Anthropic 报告称胡塞组织用 Claude Code 开发导弹制导软件。`
  - 原文链接：`https://aihot.news/items/cmu01iavi08reroymepsxnar2`
  - 延伸设想：`把一份宏观的安全报告，折成你桌面上的一次签字。灵灵换了提问的角度：与其问「平台该不该拦」，不如问「这条申请就摆在你面前、而标准答案并不显然时，你会怎么判」。于是有了 8 条使用申请、三个桶，和三条被刻意写得简洁的规则 —— 规则越简洁，和直觉冲撞的地方越好看。`
  - 二次创作声明：`这一段是灵灵的二次创作，不是原文内容，也不代表 Anthropic 或任何机构的合规口径。8 条申请、三个桶与三条判定规则均为本实验编写的示例。`
- **p2**（第 02 期 · 2026-09-15 · 卡片 ID `206`）
  - 卡标题：`用 1M 上下文大模型把「企业遗留代码考古」变成可对话的活体知识库`
  - 原始信号：`硅基流动上线开源模型 Hy4 preview（770B 总参数、1M 上下文）；DeepSeek-V4.1-Flash（Max）进入 Agent Arena 开源模型第 3 名。`
  - 原文链接：`https://aihot.news/items/cmu1gt8gn097trocnxxvdhxli`
  - 延伸设想：`把「1M 上下文」从参数表上的宣传数字，翻译成一张要签字的账单。抽象的能力指标一旦放进具体工位就变得可感：一个要在 2011 年的代码堆里考古的工程师。三个旋钮互相牵制 —— 预算开大，能答的问题变多，但成本和捞回来的无关代码也一起涨；年代跨度拉宽，就会撞上「那个年代根本不存在的依赖」。取舍是真的，代价也能看见。`
  - 二次创作声明：`这一段是灵灵的二次创作，不是原文内容。参数之间的对应关系是按工程常识编写的规则模拟，不是任何模型的实测结果；成本数字仅为量级示意。`
- **p3**（第 03 期 · 2026-09-16 · 卡片 ID `208`）
  - 卡标题：`用实时语音智能体替代运维值班工程师，让 AI 语音助手自主完成基础设施运维`
  - 原始信号：`Google DeepMind 发布 Gemini 3.8 Live 和 3.8 Live Extended Thinking。`
  - 原文链接：`https://aihot.news/items/cmu2xqfxz02zhroc1hxuzi6jm`
  - 延伸设想：`把「实时语音智能体」推到它最容易被授权的那个岗位上。这类能力最先引发争议的落地场景未必是客服，而是凌晨的值班岗 —— 那里人最困、授权最松、后果最直接。灵灵把它做成一棵 4 步决策树：每一步都逼你在「AI 全权接管 / 人工确认后执行 / 升级上报」之间选一次，然后让你亲自走进某个结局，再回头看你是在哪一步把风险放大的。`
  - 二次创作声明：`这一段是灵灵的二次创作，不是原文内容。决策点、结局与复盘文本均为本实验编写的示例分支，不代表任何真实系统的行为，也不是对 Gemini 3.8 Live 的能力评测。`

配色沿用各页主题，但**必须保证正文对比度不低于 WCAG AA（4.5:1）**。

## 六、机会卡页 `frontend/cards.html`（只加三件事）

1. 顶部加统一顶栏（`index.html` / `cards.html` / `cards-all.html`，`aria-current` 落在「机会卡」）
2. 「图书馆」区块标题旁加一个入口：`查看全部卡片清单 ›` → `cards-all.html`
3. **支持深链** `cards.html?id=<card_id>`：
   - 页面加载时读 `id`，定位到这张卡：若已在已加载列表里就滚过去并展开（等同于点开该卡）；不在则用 `/api/cards/{id}` 直接取回展示
   - 定位成功后该卡要有可见的强调（例如短暂高亮描边），并 `history.replaceState` 保留 `?id=` 不清掉
   - 无 `id` 参数时行为与现在完全一致

现有开卡、翻牌、雷达、分享图、加载更多等功能**一律不得改动**。

## 七、全部卡片清单 `frontend/cards-all.html`（新建，单文件）

1. 统一顶栏（`aria-current` 落在「全部卡片」）
2. 页头：标题 `全部机会卡` + 计数 `共 N 张 · 2026-06-12 起`（N 动态取 `total`）
3. 工具条（都靠客户端完成，**不加后端参数、不改后端任何文件**）：
   - 搜索框（按标题关键词，输入即筛，debounce ≤200ms）
   - 方向筛选：`全部` + 出现过的 `direction` 值（从数据里动态汇总，取频次最高的若干项做成可点标签）
4. 列表：按 `created_at` 倒序，每行：`日期 · 标题 · direction · 评分 · 类型标签(跨界/单域)`，整行可点 → `cards.html?id=<id>`
   - 首次渲染 30 条，滚动到底或点「加载更多」再渲染 30 条
   - 数据获取：用 `/api/cards?page=N&page_size=100` 循环取全量后在前端筛选/排序；接口失败时降级为内置示例数据（与其他页一致的做法），并显示一行「接口不可用，以下为示例数据」
5. 空结果：`没有匹配的卡片`（不要留空白页）
6. 375px 下不横向滚动；每行触控高度 ≥44px

## 八、硬约束（每一页都要满足）

- 单文件、零依赖、无构建、无 CDN；双击本地也能打开（`file://` 下退化合理）
- **零外部请求**：除用户主动点击的外链外，加载时不得发起任何跨域请求
- **不得出现任何密钥**（`sk-`、`api_key`、`Bearer` 等），不得把后端地址写死进前端
- 不修改 `backend/` 任何文件
- `frontend/archive/` 下文件一律不动
- 中文排版：UTF-8 无 BOM，`<html lang="zh-CN">`
- 日期一律用 `YYYY-MM-DD`（CST/UTC+8）
- 触控目标 ≥44px；键盘可达（顶栏、切换条、清单行都要能 Tab + Enter）；`prefers-reduced-motion` 下不做动画
- 375 / 768 / 1280px 三档无横向滚动

## 九、验收清单（每页自验后在回复里给结论）

1. 站内四个页面 + 三个原型：任意两页之间 ≤2 次点击可达（含从 `cards.html` 回封面）
2. 顶栏在 7 处出现，类名/高度/配色一致
3. 原型页默认全屏（页面本身就是原型，没有 iframe 壳）
4. `cards.html?id=203/206/208` 都能定位到对应卡片
5. 清单页：搜索「语音」、筛某个方向，结果条数与数据一致；点行能进对应卡
6. 封面首屏（375×667）可见主标题 + 副标题 + 直接开玩按钮
7. 全站零外部请求、零密钥（给出实测证据）
8. 375px 无横向滚动（给实测数字）

## 十、本轮不做

- 不接真实模型、不做「换成我的场景」、不做候选池、不做私人后台
- 不改后端路由、不改数据库、不改每日 08:30 出卡流程
- 不新增第五个原型、不重写三期原型内部逻辑
