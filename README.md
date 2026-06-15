# Product LingLing

AI 产品机会分析工具 — 把行业信号自动转化为可验证的产品机会。

🔗 **线上体验：** http://YOUR_SERVER_IP

## 它做什么

每天自动抓取 AI HOT 精选 RSS（约 50 条行业信号），**全部增量存储**后，通过关键词聚类生成两种类型的产品机会卡：

| 类型 | 标签 | 策略 | 每日产出 |
|------|------|------|----------|
| 🔍 相关洞察 | 同领域 2-3 条新闻 | 趋势聚合，发现同类信号中的产品方向 | 3-5 张 |
| ✨ 跨界创新 | 不同领域各取 1 条 | 跨领域碰撞，从看似无关的信号中挖掘意外机会 | 3-5 张 |

每日总产出 **6-10 张机会卡**，自动累积到机会库。

每张卡包含：
- 用户痛点 + AI 解决方式 + MVP 方案
- 6 维度可解释评分（满分 10 分）
- 主要风险 + 下一步验证动作
- 原文信息源链接

## 为什么做

AI 行业不缺信息，缺的是把信息转化成产品判断的能力。

常见问题：看完新闻不知道意味着什么、看不出背后的产品机会、信息无法沉淀。这个工具的价值不是帮你看更多信息，而是帮你在 5 分钟内把行业信号转化为结构化的产品判断。

## 技术栈

- **前端：** 单文件 HTML（响应式，移动端适配）
- **后端：** FastAPI (Python)
- **数据库：** SQLite
- **大模型：** DeepSeek API
- **定时任务：** APScheduler（每日 08:30 自动生成）
- **部署：** Nginx + uvicorn + systemd

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/LLing486/product-lingling.git
cd product-lingling

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 DeepSeek API Key

# 3. 启动后端
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload

# 4. 打开前端
# 浏览器访问 http://localhost:8000
```

## 项目结构

```
product-lingling/
├── PRD.md                          # 产品需求文档
├── README.md                       # 本文件
├── prototype.html                  # 前端原型
├── .env.example                    # 环境变量模板
├── .gitignore
├── backend/                        # FastAPI 后端
│   ├── main.py                     # 路由定义
│   ├── models.py                   # 数据库模型 + 迁移
│   ├── services/
│   │   ├── rss_fetcher.py          # RSS 抓取 + 增量存储
│   │   ├── clustering.py           # 关键词聚类（9 大方向）
│   │   ├── deepseek_analyzer.py    # DeepSeek 双分析器
│   │   ├── opportunity_store.py    # 机会卡 CRUD
│   │   └── scheduler.py            # APScheduler 定时任务
│   └── requirements.txt
└── frontend/                       # 前端
    └── prototype.html
```

## 许可

MIT
