"""Analyze RSS items with DeepSeek and generate opportunity cards."""

import json
import os
from openai import OpenAI

SYSTEM_PROMPT = """你是一位资深 AI 产品经理和产品机会分析师。

你的任务：从一批 AI 行业 RSS 资讯中，筛选出最有产品机会价值的 2 条，并为每条生成一张结构化的产品机会卡。

## 分析维度（6 维度评分，每项 1-5 分）

1. **痛点真实性** (pain_real) — 这个痛点是否真实存在？有多少人遇到？
2. **AI 适配度** (ai_fit) — AI 在这个场景中是否有独特优势？是否必须用 AI？
3. **市场规模** (market_size) — 目标市场有多大？增长趋势如何？
4. **竞争强度** (competition) — 现有竞争者多不多？壁垒高不高？（注意：竞争越激烈分数越低）
5. **技术可行性** (tech_feasibility) — 当前技术能否实现？成本是否可控？
6. **商业化潜力** (monetization) — 用户是否愿意付费？变现路径是否清晰？

## 加权总分计算
权重：痛点真实性×2.0, AI适配度×2.0, 市场规模×1.5, 竞争强度×1.0, 技术可行性×1.5, 商业化潜力×2.0
总分 = 加权分之和 / (5 × 总权重) × 10，保留一位小数

## 输出要求

从输入的资讯中选出得分最高的 2 条，为每条生成机会卡。

请严格返回以下 JSON 格式，不要包含任何其他文字：

```json
{
  "cards": [
    {
      "title": "一句话概括产品方向",
      "user_persona": "目标用户画像描述",
      "pain_point": "用户在真实场景中的具体困难",
      "ai_solution": "AI 在这个场景中的独特优势和解决方式",
      "mvp_plan": "最小可行产品的具体定义，包括核心功能、技术栈、开发周期",
      "score": {
        "pain_real": {"value": 4, "reason": "简短理由"},
        "ai_fit": {"value": 5, "reason": "简短理由"},
        "market_size": {"value": 3, "reason": "简短理由"},
        "competition": {"value": 4, "reason": "简短理由"},
        "tech_feasibility": {"value": 5, "reason": "简短理由"},
        "monetization": {"value": 4, "reason": "简短理由"},
        "total": 4.2
      },
      "risks": "主要风险点，如大厂覆盖、商业化困难、技术瓶颈等",
      "next_step": "具体可执行的下一步验证动作",
      "source_titles": ["原始资讯标题1", "原始资讯标题2"],
      "source_urls": ["原始资讯链接1", "原始资讯链接2"],
      "direction": "方向分类，如 Agent、AI 办公、AI 教育、AI 营销、AI 编程、AI 设计、AI 数据、AI 安全 等"
    }
  ]
}
```"""

CROSSDOMAIN_SYSTEM_PROMPT = """你是一位跨领域创新猎手，专门在看似毫不相关的技术领域之间发现隐藏的产品机会。

These news items are from completely different AI domains. Your task is to find unexpected product opportunities by combining insights from these unrelated fields. Think creatively about what happens when these domains collide.

你的思维方式：
- 不要寻找明显的关联，而是寻找「意外的嫁接点」——把 A 领域的核心能力当作 B 领域缺失的那块拼图
- 关注「技术溢出」：一个领域成熟的技术，往往是另一个领域突破的催化剂
- 思考用户身份的重叠：同一个人在不同场景下的需求碰撞，往往产生最有价值的产品
- 寻找「反直觉组合」：越不可能的组合，竞争壁垒越高

## 分析维度（6 维度评分，每项 1-5 分）

1. **痛点真实性** (pain_real) — 这个痛点是否真实存在？有多少人遇到？
2. **AI 适配度** (ai_fit) — AI 在这个场景中是否有独特优势？是否必须用 AI？
3. **市场规模** (market_size) — 目标市场有多大？增长趋势如何？
4. **竞争强度** (competition) — 现有竞争者多不多？壁垒高不高？（注意：竞争越激烈分数越低）
5. **技术可行性** (tech_feasibility) — 当前技术能否实现？成本是否可控？
6. **商业化潜力** (monetization) — 用户是否愿意付费？变现路径是否清晰？

## 加权总分计算
权重：痛点真实性×2.0, AI适配度×2.0, 市场规模×1.5, 竞争强度×1.0, 技术可行性×1.5, 商业化潜力×2.0
总分 = 加权分之和 / (5 × 总权重) × 10，保留一位小数

## 输出要求

从输入的资讯中，找出最出人意料的跨领域组合（最多 2 条），为每条生成机会卡。每张卡必须明确说明来自哪两个领域的碰撞。

请严格返回以下 JSON 格式，不要包含任何其他文字：

```json
{
  "cards": [
    {
      "title": "一句话概括产品方向（体现跨领域碰撞）",
      "user_persona": "目标用户画像描述",
      "pain_point": "用户在真实场景中的具体困难",
      "ai_solution": "AI 在这个场景中的独特优势和解决方式",
      "mvp_plan": "最小可行产品的具体定义，包括核心功能、技术栈、开发周期",
      "score": {
        "pain_real": {"value": 4, "reason": "简短理由"},
        "ai_fit": {"value": 5, "reason": "简短理由"},
        "market_size": {"value": 3, "reason": "简短理由"},
        "competition": {"value": 4, "reason": "简短理由"},
        "tech_feasibility": {"value": 5, "reason": "简短理由"},
        "monetization": {"value": 4, "reason": "简短理由"},
        "total": 4.2
      },
      "risks": "主要风险点",
      "next_step": "具体可执行的下一步验证动作",
      "source_titles": ["资讯标题1", "资讯标题2"],
      "source_urls": ["资讯链接1", "资讯链接2"],
      "direction": "方向分类"
    }
  ]
}
```"""


def _build_user_prompt(items: list[dict]) -> str:
    lines = ["以下是今日 AI 行业资讯，请分析以下资讯：\n"]
    for i, item in enumerate(items, 1):
        lines.append(f"--- 资讯 {i} ---")
        lines.append(f"标题: {item['title']}")
        lines.append(f"链接: {item['url']}")
        if item.get("description"):
            lines.append(f"摘要: {item['description'][:300]}")
        lines.append("")
    return "\n".join(lines)


def _recalculate_scores(cards: list[dict]) -> list[dict]:
    """Ensure score.total is calculated correctly and sort by total desc."""
    weights = {
        "pain_real": 2.0,
        "ai_fit": 2.0,
        "market_size": 1.5,
        "competition": 1.0,
        "tech_feasibility": 1.5,
        "monetization": 2.0,
    }
    total_weight = sum(weights.values())

    for card in cards:
        score = card.get("score", {})
        weighted_sum = 0
        for dim, w in weights.items():
            val = score.get(dim, {})
            if isinstance(val, dict):
                weighted_sum += val.get("value", 0) * w
            else:
                weighted_sum += val * w
        score["total"] = round(weighted_sum / (5 * total_weight) * 10, 1)
        card["score"] = score

    cards.sort(key=lambda c: c.get("score", {}).get("total", 0), reverse=True)
    return cards[:2]


def _normalize_sources(cards: list[dict]) -> list[dict]:
    """Ensure each card has source_titles and source_urls arrays, plus backward-compat singular fields."""
    for card in cards:
        if "source_titles" not in card or not card["source_titles"]:
            card["source_titles"] = [card.get("source_title", "")]
        if "source_urls" not in card or not card["source_urls"]:
            card["source_urls"] = [card.get("source_url", "")]
        # Split combined "A + B" style source_titles into separate entries
        if len(card["source_titles"]) == 1 and " + " in card["source_titles"][0]:
            parts = [p.strip() for p in card["source_titles"][0].split(" + ") if p.strip()]
            if len(parts) > 1:
                card["source_titles"] = parts
                # If URLs also combined, split them too; otherwise pad with "#"
                if len(card["source_urls"]) == 1 and " + " in card["source_urls"][0]:
                    card["source_urls"] = [u.strip() for u in card["source_urls"][0].split(" + ") if u.strip()]
                while len(card["source_urls"]) < len(card["source_titles"]):
                    card["source_urls"].append("#")
        # Backward compat: set singular fields from first element
        if not card.get("source_title"):
            card["source_title"] = card["source_titles"][0] if card["source_titles"] else ""
        if not card.get("source_url"):
            card["source_url"] = card["source_urls"][0] if card["source_urls"] else ""
    return cards


def _call_deepseek(system_prompt: str, user_prompt: str) -> list[dict]:
    """Shared DeepSeek API call. Returns parsed cards list."""
    api_key = os.environ.get("LING_DEEPSEEK_API", "")
    if not api_key:
        raise RuntimeError("LING_DEEPSEEK_API not set in environment")

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=8192,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    data = json.loads(raw)
    return data.get("cards", [])


def analyze_items(items: list[dict], card_type: str = "related") -> list[dict]:
    """Send items to DeepSeek for analysis, return up to 4 opportunity cards."""
    if not items:
        return []

    batch = items[:50]
    cards = _call_deepseek(SYSTEM_PROMPT, _build_user_prompt(batch))
    cards = _recalculate_scores(cards)
    cards = _normalize_sources(cards)

    for card in cards:
        card["card_type"] = card_type

    return cards


def analyze_items_crossdomain(items: list[dict], card_type: str = "crossdomain") -> list[dict]:
    """Analyze 2-3 items from DIFFERENT domains for cross-domain innovation opportunities."""
    if not items:
        return []

    batch = items[:3]  # Cross-domain works best with fewer, more diverse items
    cards = _call_deepseek(CROSSDOMAIN_SYSTEM_PROMPT, _build_user_prompt(batch))
    cards = _recalculate_scores(cards)
    cards = _normalize_sources(cards)

    for card in cards:
        card["card_type"] = card_type

    return cards
