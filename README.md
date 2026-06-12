# Product LingLing

AI 产品机会分析工具 — 把行业信号自动转化为可验证的产品机会。

🔗 **线上体验：** http://150.158.136.55

## 它做什么

每天自动订阅 AI HOT 精选 RSS feed，从约 50 条精编行业信号中，由 DeepSeek 筛选并生成 **4 张产品机会卡**。

每张卡包含：
- 用户痛点
- AI 解决方式
- MVP 方案
- 6 维度可解释评分（满分 10 分）
- 主要风险
- 下一步验证动作
- 原文信息源链接

机会卡自动沉淀到机会库，支持关键词搜索和方向筛选。

## 为什么做

AI 行业不缺信息，缺的是把信息转化成产品判断的能力。

常见问题：看完新闻不知道意味着什么、看不出背后的产品机会、信息无法沉淀。这个工具的价值不是帮你看更多信息，而是帮你在 5 分钟内把行业信号转化为结构化的产品判断。

## 技术栈

- **前端：** 单文件 HTML（基于 prototype.html）
- **后端：** FastAPI (Python)
- **数据库：** SQLite
- **大模型：** DeepSeek API
- **部署：** Docker Compose + Nginx

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
uvicorn main:app --reload

# 4. 打开前端
# 浏览器打开 frontend/prototype.html
```

## 项目结构

```
product-lingling/
├── PRD.md              # 产品需求文档
├── README.md           # 本文件
├── INTERVIEW-QA.md     # 面试追问准备
├── prototype.html      # 前端原型
├── .env.example        # 环境变量模板
├── .gitignore
├── backend/            # FastAPI 后端
│   ├── main.py
│   ├── models.py
│   ├── services/
│   │   ├── rss_fetcher.py
│   │   ├── deepseek_analyzer.py
│   │   └── opportunity_store.py
│   └── requirements.txt
└── frontend/           # 前端
    └── prototype.html
```

## 许可

MIT
