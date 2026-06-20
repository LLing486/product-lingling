# Product LingLing

AI 产品机会分析工具 — 把行业信号自动转化为可验证的产品机会。

## 它做什么

每天自动抓取 AI HOT 精选 RSS（约 50 条行业信号），全量增量存储，通过信号评分 + 智能聚类生成两张产品机会卡：

| 类型 | 标签 | 策略 |
|------|------|------|
| ◎ 相关洞察 | 同领域高信号条目 | 按信号质量评分选最优簇，取该簇最佳条目分析 |
| ⚡ 跨界创新 | 距离最远的两个领域各取一条 | 簇间距离矩阵最大化碰撞感 |

每日固定产出 **1 张相关洞察 + 1 张跨界创新**，自动累积到机会库。

每张卡包含：用户痛点、AI 解决方式、MVP 方案、6 维度可解释评分（满分 10 分）、主要风险、下一步验证动作、原文信息源链接。

## 界面设计

v2 界面采用空间纵深设计：前景是机会卡，后景是信息源星图，通过鼠标滚轮或按钮穿越两层。

**前景层（机会）**
- 今日 2 张卡以对角线错落排列，中间有碰撞连线可视化两种灵感的交汇
- 历史机会卡以极坐标轨道分布在周围，hover 浮起，点击打开全屏详情
- 底部：类型 / 评分筛选栏 + 深度轨道 + 潜入按钮

**后景层（信息源）**
- 信息源条目以漂浮节点形式展示，节点随机慢漂，邻近节点之间有连线
- 节点颜色区分状态：已关联机会卡（琥珀）/ 跨界来源 / 普通信号
- 点击节点展开单条信息卡片；"展开全部信号"一次性展开所有节点
- 底部：信号状态 / 类型筛选栏（左）+ 浮出按钮（中）+ 展开切换（右）

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | 单文件 HTML（v2 空间纵深界面 + v1 原型保留为基线） |
| 后端 | FastAPI (Python) |
| 数据库 | SQLite |
| 大模型 | DeepSeek API |
| 定时任务 | APScheduler（每日 08:30 CST） |
| 部署 | Nginx + uvicorn + systemd |

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/LLing486/product-lingling.git
cd product-lingling

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 DeepSeek API Key

# 3. 启动后端
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload

# 4. 打开前端
# 浏览器访问 http://localhost:8000
```

无后端时直接打开 `frontend/v2.html` 会进入演示模式（Mock 数据）。

## 项目结构

```
product-lingling/
├── PRD.md                          # 产品需求文档
├── README.md                       # 本文件
├── .env.example                    # 环境变量模板
├── .gitignore
├── backend/                        # FastAPI 后端
│   ├── main.py                     # 路由定义（5 个端点）
│   ├── models.py                   # SQLite schema + 自动迁移
│   ├── services/
│   │   ├── rss_fetcher.py          # RSS 抓取 + 增量存储
│   │   ├── clustering.py           # 信号评分 + 关键词聚类（9 类）
│   │   ├── deepseek_analyzer.py    # DeepSeek 双分析器（相关 + 跨界）
│   │   ├── opportunity_store.py    # 机会卡 CRUD
│   │   └── scheduler.py            # APScheduler 定时任务
│   └── requirements.txt
└── frontend/
    ├── v2.html                     # 主前端：空间纵深 3D 界面（当前版本）
    └── prototype.html              # v1 原型：稳定基线，备用
```

## API 端点

| 端点 | 说明 |
|------|------|
| `GET /health` | 健康检查 |
| `GET /api/cards` | 机会卡列表（支持 keyword / direction / date 筛选） |
| `GET /api/cards/today` | 今日机会卡（无数据时回退到最近一天） |
| `GET /api/cards/{id}` | 单卡详情 |
| `POST /api/cards/generate` | 手动触发生成（仅 development 模式） |
| `GET /api/sources` | 全部 RSS 条目 |

## 许可

MIT
