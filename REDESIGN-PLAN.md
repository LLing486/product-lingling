# Product LingLing 重构规划

## 一、现状分析

### 当前流程
```
RSS (50条) → 只存今日未分析 → DeepSeek 选4条 → 1条=1张卡片 → 存入DB
```

### 问题
1. **信息源浪费**：每天50条RSS，只用4条，其他全部丢弃
2. **卡片单一**：1条新闻→1张卡片，没有跨新闻的关联和创意
3. **无分类**：所有卡片混在一起，没有"关联型"vs"创意型"区分

---

## 二、目标设计

### 新流程
```
RSS (50条) → 全量增量存储（信息源池）
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
    关联型分析                 创意型分析
  聚类2-3条相关新闻         随机2-3条无关新闻
        ↓                       ↓
    3-5张卡片                3-5张卡片
        ↓                       ↓
        └───────────┬───────────┘
                    ↓
              每日6-10张卡片
```

### 三种卡片类型
| 类型 | card_type | 数据来源 | 逻辑 |
|------|-----------|----------|------|
| 关联型 | `related` | 2-3条主题相近的新闻 | 从同一趋势中发现产品机会 |
| 创意型 | `creative` | 2-3条主题无关的新闻 | 跨领域碰撞产生意外组合 |

---

## 三、技术方案

### 3.1 数据库改动 (models.py)

**opportunity_cards 表新增字段：**
```sql
ALTER TABLE opportunity_cards ADD COLUMN card_type TEXT NOT NULL DEFAULT 'related';
ALTER TABLE opportunity_cards ADD COLUMN source_ids TEXT;  -- JSON数组，关联的rss_items.id
```

- `card_type`: `'related'` 或 `'creative'`
- `source_ids`: JSON数组，记录这张卡片用了哪些RSS条目，方便溯源

**无需改动 rss_items 表**，现有结构已够用。

### 3.2 RSS抓取改动 (rss_fetcher.py)

**现状**：`fetch_and_store()` 只返回今日未分析的条目
**改动**：新增函数返回「今日新抓取的全部条目」，不依赖 `is_analyzed` 标记

```python
def fetch_and_store_all() -> list[dict]:
    """抓取RSS，全量增量存储，返回今日新抓取的全部条目（不论是否分析过）"""
    # INSERT OR IGNORE 保证不重复
    # 返回 WHERE date(fetched_at) = date('now') 的全部条目
```

### 3.3 新增聚类模块 (clustering.py)

**纯Python实现，不依赖外部服务：**

```python
def cluster_by_keywords(items: list[dict], n_clusters: int = 5) -> list[list[dict]]:
    """基于关键词重叠的简单聚类"""
    # 1. 对每条item提取关键词（标题+描述分词）
    # 2. 计算关键词Jaccard相似度
    # 3. 贪心聚类：每个cluster选一个seed，加入最相似的1-2条
    # 4. 返回 n_clusters 个组，每组2-3条
```

不需要ML模型，用关键词重叠就够——因为RSS标题通常包含明确的技术词/公司名，聚类效果不会差。

### 3.4 DeepSeek分析器改动 (deepseek_analyzer.py)

**从1个函数拆成3个：**

```python
def analyze_related(cluster: list[dict]) -> dict:
    """关联型：给2-3条相关新闻，生成1张卡片"""
    # Prompt: "这是一组关于同一趋势的AI新闻，从中发现产品机会"

def analyze_creative(items: list[dict]) -> dict:
    """创意型：给2-3条无关新闻，发现跨领域产品机会"""
    # Prompt: "这是一组看似无关的AI新闻，找到它们之间的意外联系，创造产品机会"

def generate_all_cards(today_items: list[dict]) -> list[dict]:
    """主入口：聚类→关联分析×3-5组 + 随机组合→创意分析×3-5组"""
    # 1. 聚类
    # 2. 每个cluster调analyze_related → 3-5张关联卡
    # 3. 随机从不同cluster各取1条，组合3-5组 → 调analyze_creative → 3-5张创意卡
    # 4. 合并返回
```

**关键设计：**
- 关联型的 Prompt 强调「趋势分析、竞争格局、成熟度判断」
- 创意型的 Prompt 强调「跨领域类比、反直觉组合、第一性原理」
- 两个Prompt都要求返回相同JSON结构，前端不需要区分渲染逻辑

### 3.5 调度器改动 (scheduler.py)

```python
def run_generation_once() -> dict:
    # 1. fetch_and_store_all() → 全量存储，获取今日全部条目
    # 2. generate_all_cards(today_items) → 生成6-10张卡片
    # 3. save_cards(cards) → 存入DB（带card_type和source_ids）
```

### 3.6 前端改动 (prototype.html)

**卡片区分：**
- 关联型卡片：左上角蓝色标签 `🔗 关联洞察`
- 创意型卡片：左上角紫色标签 `✨ 创意碰撞`
- 详情面板显示：`📰 基于N条资讯`，可点击查看原始新闻

**后续迭代（盲盒+解密）在本次改动稳定后再加。**

---

## 四、实施步骤

| 步骤 | 内容 | 改动文件 | 预估 |
|------|------|----------|------|
| 1 | DB schema 加 `card_type` + `source_ids` 字段 | models.py | 小 |
| 2 | 新增 `fetch_and_store_all()` | rss_fetcher.py | 小 |
| 3 | 新增 `clustering.py` 关键词聚类 | 新文件 | 中 |
| 4 | 拆分分析器为 related + creative | deepseek_analyzer.py | 中 |
| 5 | 更新调度器串联新流程 | scheduler.py | 小 |
| 6 | 前端卡片标签+来源显示 | prototype.html | 中 |
| 7 | 测试 + 部署到服务器 | - | - |

---

## 五、DeepSeek API 调用量估算

- 关联型：3-5组 × 1次 = 3-5次调用
- 创意型：3-5组 × 1次 = 3-5次调用
- **每日总计：6-10次 DeepSeek 调用**（现在是1次）
- DeepSeek-chat 价格很低，约 $0.14/百万token，每日成本 < ¥0.1

---

## 六、后续可叠加的创意（本次不做）

1. 🎰 盲盒开箱动画 — 每日首次打开，卡片翻转+数字跳动
2. ✨ 解密式展开 — AI分析过程逐字显现（Encrypted Text特效）
3. 🔮 对话式卡片 — 每张卡片是一个可对话的AI角色
4. 📅 时间河流视图 — 横向时间轴，机会的生长和消退
