# 需求：详情面板评分展示改为六维雷达图

## 背景
Product-Lingling 前端 `frontend/index.html` 的机会卡详情面板（`#d-dims`）目前用**条形图**（`.dim-bar` / `.dim-fill`）展示六维评分，用户希望改成**正六边形六维雷达图**。

## 现有实现（需替换的部分）

**数据**：`full.scores` 对象，6 个维度，每维 0-5 分：
- `pain_real` 痛点真实性
- `ai_fit` AI 适配度
- `market_size` 市场规模
- `competition` 竞争强度
- `tech_feasibility` 技术可行性
- `monetization` 商业化潜力

值结构：`{ value: 4, reason: '...' }`（reason 是可选的评分理由）。

**当前渲染代码**（约 933-941 行，`openDetail()` 内）：
```js
$('d-dims').innerHTML = DIMS.map(d => {
  const raw = (full.scores || {})[d.key];
  const v = raw && typeof raw === 'object' ? (raw.value || 0) : (Number(raw) || 0);
  const reason = raw && typeof raw === 'object' ? (raw.reason || '') : '';
  return `<div class="dim">
    <span class="dim-n" title="${esc(reason)}">${d.name}</span>
    <span class="dim-bar"><span class="dim-fill" style="width:0" data-w="${v / 5 * 100}%"></span></span>
    <span class="dim-v">${v}/5</span></div>`;
}).join('');
```
动画逻辑（952 行）：`requestAnimationFrame(() => requestAnimationFrame(() => { document.querySelectorAll('#d-dims .dim-fill').forEach(el => { el.style.width = el.dataset.w; }); }));`

**DIMS 定义**（428-432 行）：6 个维度 key + 中文名。

**详情面板颜色约定**：`cross`（跨界卡）用 `var(--terra)`，普通卡用 `var(--amber)`（见 921-922 行 `d-score` 的取色逻辑）。

**现有 CSS**（216-221 行）：
```css
.dims { margin: 6px 0 4px; }
.dim { display: grid; grid-template-columns: 74px 1fr 38px; gap: 10px; align-items: center; padding: 5px 0; }
.dim-n { font-size: 12px; color: var(--ink-2); }
.dim-bar { height: 6px; border-radius: 3px; background: var(--paper-2); overflow: hidden; }
.dim-fill { height: 100%; border-radius: 3px; background: var(--amber); transition: width .7s ease-out; }
.dim-v { font-size: 12px; color: var(--ink-3); text-align: right; font-variant-numeric: tabular-nums; }
```

## 目标效果
把条形图替换为 **SVG 正六边形雷达图**：

1. **形状**：正六边形网格，6 个顶点按顺时针/逆时针均匀分布，每个顶点对应一个维度。
2. **网格**：0/1/2/3/4/5 六层同心六边形网格线 + 从中心到顶点的 6 条对角线（细线、低透明度），构成雷达图底网。
3. **数据多边形**：按各维度值（0-5）计算顶点位置，绘制填充多边形，颜色 `var(--amber)`（普通卡）/ `var(--terra)`（跨界卡），带半透明填充（如 fill-opacity 0.25）和实线描边。
4. **维度标签**：每个顶点外侧标注维度中文名（字号约 10-11px，颜色 var(--ink-2)），保持可读性；标签位置需根据角度计算避免遮挡（六边形外侧放射状摆放）。
5. **数值**：每个顶点处标注该维度的分值（0-5，保留 1 位小数，如 4/5 显示 4.0 或 4）。
6. **评分理由**：保留 reason 信息——可放在维度标签的 `<title>` 悬浮提示（SVG `<title>` 元素）中。
7. **动画**：打开详情时雷达图从中心向外展开（多边形 + 网格线用 transform scale 或 stroke-dashoffset 过渡，约 0.7s ease-out），与原有条形图动画风格一致。注意保留 `prefers-reduced-motion` 兼容（现有 281 行有 `transition: none !important` 的降级规则）。
8. **尺寸与布局**：雷达图约 200×200 或自适应容器宽度（居中），上方保留大分数 `d-score` 不动，雷达图作为六维评分的可视化主体。
9. **降级**：如果 `full.scores` 缺失或全为 0，显示占位文本（如"暂无六维评分"），不报错。
10. **不改变**：`d-score` 大分数、维度含义、数据来源、其他面板布局均不动。只替换 `#d-dims` 内的条形图。

## 技术约束
- 单文件修改 `frontend/index.html`，纯前端原生 JS + SVG，不引入任何外部库（无 ECharts/D3）。
- 遵循现有代码风格（原生函数、模板字符串、`$()` helper、`esc()` 转义）。
- 保持暗色玻璃主题一致（用现有 CSS 变量：--paper/--ink-2/--ink-3/--amber/--terra 等）。
- 雷达图值域固定 0-5，多边形顶点坐标：`angle = -90° + i * 60°`（从正上方开始，顺时针），`r = v/5 * R`（R 为最大半径）。
- 修改完成后本地验证：node 语法检查或直接起服务看页面渲染，确保无 JS 报错、雷达图正常显示、动画正常。

## 完成后
1. 本地验证（起服务或静态检查），确认无报错。
2. 报告修改摘要（改了哪些函数/CSS，雷达图实现方式）。
3. 不要 commit。
