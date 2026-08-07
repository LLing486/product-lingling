# Product LingLing 性能优化 + 前端归档 需求说明

> 提交人：Joi ｜ 日期：2026-08-05
> 目标：解决页面加载卡顿（当前全量拉取 130 张卡 + 1052 条 RSS 一次进 DOM），并统一前端入口为 index.html

---

## 一、性能优化（后端）

### 1. `/api/cards` 分页 + 精简字段（backend/main.py + backend/services/opportunity_store.py）

**main.py 修改：**
```python
@app.get("/api/cards")
def list_cards(
    keyword: str = Query(""),
    direction: str = Query(""),
    date: str = Query(""),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    cards, total = get_all_cards(keyword=..., direction=..., date_filter=..., page=page, page_size=page_size)
    return {"cards": cards, "total": total, "page": page, "page_size": page_size}
```

**opportunity_store.py 修改：**
- `get_all_cards()` 增加 `page`、`page_size` 参数，SQL 加 `LIMIT ? OFFSET ?`，返回 `(cards, total)` 元组
- 新增精简序列化函数 `_card_light(row)`：列表接口只返回 `id, title, direction, card_type, score, created_at, source_title`（去掉 `user_persona, pain_point, ai_solution, mvp_plan, risks, next_step, source_titles, source_urls, kickoff, kickoff_prompt` 等大文本字段）
- 分页排序保持 `ORDER BY created_at DESC, id DESC`

### 2. `/api/sources` 加 limit 参数（backend/main.py + backend/services/rss_fetcher.py）

**rss_fetcher.py：**
- `get_all_rss_items(limit: int = 50)` 增加 limit 参数，SQL 加 `LIMIT ?`，保持 `ORDER BY fetched_at DESC`

**main.py：**
- `/api/sources` 加 `limit: int = Query(50, ge=1, le=500)` 参数，透传给 `get_all_rss_items`

---

## 二、性能优化（前端 frontend/v3.html）

### 3. 首屏只拉必要数据

`loadData()` 改为：
- `/api/cards/today` — 全量（今日卡本来就不多）
- `/api/cards?page=1&page_size=20` — 只拉第一页（20张）做卡片库初始展示
- `/api/sources?limit=50` — 只拉最近50条信号

### 4. 卡片库滚动懒加载

- 维护一个 `page` 状态变量，初始 1
- 监听滚动/容器滚动，接近底部时 `page += 1` 请求下一页 `/api/cards?page=N&page_size=20`
- 追加渲染到卡片库容器，不重建已有 DOM
- 搜索/筛选时重置 `page = 1` 并清空重载
- 数据接口兼容：今日卡渲染逻辑不动，只改卡片库（library）的加载方式
- 若分页返回 `page * page_size >= total` 停止继续加载（显示"已加载全部"）

---

## 三、前端归档（frontend/）

### 5. 统一入口 index.html

- 将 `v3.html` 的**完整内容**复制到 `index.html`（保持 v3 全部功能与视觉不变）
- 删除 index.html 中的跳转逻辑（不再需要 `location.replace('/v3.html')`）

### 6. 旧版本移入 archive/

- 新建 `frontend/archive/` 目录
- `v3.html`、`v2.html`、`prototype.html` 全部移入 `frontend/archive/`
- 检查 index.html 内是否有指向 v2/v3 的链接，有则更新或删除

---

## 四、验收标准

1. `node`/本地起服后：访问 `/` 直接是 v3 完整界面，无跳转
2. 首屏请求：`/api/cards/today` + `/api/cards?page=1` + `/api/sources?limit=50`，无全量请求
3. 卡片库滚动到底自动加载下一页，加载完显示结束提示
4. 搜索/筛选功能正常（重置分页）
5. 旧版本在 archive/ 下可访问（`/archive/v3.html` 等）
6. 不改变现有视觉设计、今日卡交互、评分展示

## 五、约束

- 不引入新依赖、不改数据库 schema
- 保持单文件前端风格（v3.html 原本就是单文件）
- 修改完成后本地跑一遍验证，再交付
