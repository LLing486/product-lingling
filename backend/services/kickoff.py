"""Compose a copy-paste-ready validation kickoff prompt (验证 SOP 开工提示词) from a card.

Design: DeepSeek only fills small structured slots (kickoff.first_milestone /
falsify_signals / research_queries / resources_needed). The full SOP text is
assembled here by a deterministic template, so old cards without slots degrade
gracefully using existing card fields.
"""

import json


def _get_kickoff_slots(card: dict) -> dict:
    k = card.get("kickoff") or {}
    if isinstance(k, str):
        try:
            k = json.loads(k)
        except (json.JSONDecodeError, TypeError):
            k = {}
    return k if isinstance(k, dict) else {}


def _as_list(val) -> list[str]:
    if isinstance(val, list):
        return [str(v).strip() for v in val if str(v).strip()]
    if isinstance(val, str) and val.strip():
        return [val.strip()]
    return []


def build_kickoff_prompt(card: dict) -> str:
    """Build the full validation SOP prompt text for one opportunity card."""
    slots = _get_kickoff_slots(card)

    title = card.get("title", "")
    persona = card.get("user_persona", "")
    pain = card.get("pain_point", "")
    solution = card.get("ai_solution", "")
    mvp = card.get("mvp_plan", "")
    risks = card.get("risks", "")
    next_step = card.get("next_step", "")

    # Slot fallbacks from existing fields
    milestone = slots.get("first_milestone") or next_step or f"围绕「{title}」做一个单场景可演示 demo"
    falsify = _as_list(slots.get("falsify_signals")) or ([risks] if risks else [])
    queries = _as_list(slots.get("research_queries")) or [title]
    resources = _as_list(slots.get("resources_needed")) or ["按 MVP 方案所列技术栈准备开发环境与必要的 API Key"]

    # Sources
    titles = card.get("source_titles") or ([card.get("source_title")] if card.get("source_title") else [])
    urls = card.get("source_urls") or ([card.get("source_url")] if card.get("source_url") else [])
    src_lines = []
    for i, t in enumerate(titles):
        if not t:
            continue
        u = urls[i] if i < len(urls) else ""
        src_lines.append(f"- {t}" + (f"（{u}）" if u and u != "#" else ""))
    sources_block = "\n".join(src_lines) if src_lines else "- （无）"

    queries_block = "、".join(f"「{q}」" for q in queries)
    resources_block = "；".join(resources)
    falsify_block = "\n".join(f"   - {f}" for f in falsify) if falsify else "   - 大厂已有同类功能且免费提供\n   - 痛点讨论多但无人表达付费意愿"

    return f"""你是我的产品验证助手。请帮我验证下面这个 AI 产品机会是否值得投入开发。先验证，不要急着写代码。

## 机会卡
- 机会方向：{title}
- 目标用户：{persona}
- 用户痛点：{pain}
- AI 解法：{solution}
- MVP 方案：{mvp}
- 已知风险：{risks}
- 信息源：
{sources_block}

## 验证 SOP

### 第一步 · 桌面调研（先做这个）
1. 搜索关键词：{queries_block}，找出现有竞品和相关开源项目。
2. 对每个竞品记录：产品定位、目标用户、定价、最近 3 个月动态。
3. 判断这个机会属于哪种情况：市场空白 / 可差异化切入 / 已是红海。

### 第二步 · 痛点证伪（主动找反面证据）
4. 重点检查以下证伪信号，任何一条成立都要明确指出：
{falsify_block}
5. 找 2-3 处真实用户讨论（Reddit / V2EX / 即刻 / 小红书等），确认痛点是否真实存在、用户是否表达过付费意愿。

### 第三步 · 最小验证物（只有前两步通过才做）
6. 开工前先准备：{resources_block}。
7. 第一个可验证的里程碑：{milestone}
8. 优先做能拿到真实用户反馈的最小形态（落地页 / 可交互原型 / 单场景 demo），不要一上来做完整产品；技术选型从 MVP 方案出发，能降级就降级。

## 输出要求
最后给出明确结论：**值得做 / 需要转向 / 建议放弃**，附上关键证据和理由。如果是「需要转向」，说明转向后的新切入点。"""
