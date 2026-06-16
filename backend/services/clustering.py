"""Keyword-based clustering with signal scoring and smart group selection."""

import re
from collections import Counter

KEYWORDS = {
    "Agent": ["agent", "自动化", "工作流", "multi-agent", "任务编排"],
    "大模型": ["llm", "gpt", "claude", "gemini", "deepseek", "模型", "开源", "参数", "训练"],
    "AI编程": ["code", "代码", "cursor", "copilot", "coding", "ide", "开发者", "编程"],
    "AI办公": ["办公", "效率", "文档", "会议", "邮件", "知识", "翻译"],
    "AI营销": ["营销", "内容", "seo", "广告", "社媒", "品牌", "增长"],
    "AI创意": ["图像", "视频", "音乐", "游戏", "设计", "创作", "生成"],
    "AI医疗": ["医疗", "健康", "药物", "诊断", "生物"],
    "机器人": ["机器人", "自动驾驶", "具身智能", "传感器"],
    "硬件": ["芯片", "算力", "gpu", "服务器", "tpu"],
}


def score_item_signal(item: dict) -> float:
    """Rate an RSS item's 'signal strength' — how likely it carries a real product insight.

    Returns a float in [0, 3]. Higher = more signal-rich.
    """
    title = (item.get("title", "") or "")
    desc = (item.get("description", "") or "")
    score = 1.0  # baseline

    # Positive signals
    if re.search(r"\d+%|\d+亿|\d+万", title):
        score += 1.0  # contains metrics
    if re.search(
        r"发布|推出|开源|开放|上线|发布|new|launch|release|announce",
        title, re.IGNORECASE,
    ):
        score += 1.0  # new development
    if re.search(r"融资|收购|IPO|上市|invest|funding|acquire", title, re.IGNORECASE):
        score += 1.0  # business signal

    # Negative signals
    if len(desc) < 50:
        score -= 1.0  # likely clickbait or empty

    return max(0.0, min(3.0, score))


def _handle_other(items: list[dict]) -> dict[str, list[dict]]:
    """Dynamically split '其他' into sub-clusters by high-frequency title words."""
    if len(items) < 3:
        return {"其他": items}

    # Collect meaningful words (2+ CJK chars or 3+ ASCII chars)
    words: list[str] = []
    for item in items:
        title = item.get("title", "") or ""
        for token in re.findall(r"[一-鿿]{2,}|[a-zA-Z]{3,}", title):
            words.append(token.lower())

    freq = Counter(words)
    # Find words shared by 3+ items
    cluster_words = {w for w, c in freq.most_common(10) if c >= 3}
    if not cluster_words:
        return {"其他": items}

    result: dict[str, list[dict]] = {}
    assigned: set[int] = set()
    for w in sorted(cluster_words):
        cluster_name = f"趋势-{w}"
        result[cluster_name] = []
        for i, item in enumerate(items):
            if i in assigned:
                continue
            if w in (item.get("title", "") or "").lower():
                result[cluster_name].append(item)
                assigned.add(i)

    leftover = [item for i, item in enumerate(items) if i not in assigned]
    if leftover:
        result["其他"] = leftover
    return result


def cluster_items(items: list[dict]) -> dict[str, list[dict]]:
    """Cluster items by keyword matching. '其他' items get dynamic sub-clustering.

    Returns {cluster_name: [items]}.
    """
    clustered: dict[str, list[dict]] = {}

    for item in items:
        text = (item.get("title", "") + " " + item.get("description", "")).lower()
        matched = False
        for cluster_name, keywords in KEYWORDS.items():
            if any(kw in text for kw in keywords):
                clustered.setdefault(cluster_name, []).append(item)
                matched = True
                break
        if not matched:
            clustered.setdefault("其他", []).append(item)

    # Dynamically split "其他" if it has >= 3 items
    if "其他" in clustered and len(clustered["其他"]) >= 3:
        sub = _handle_other(clustered.pop("其他"))
        clustered.update(sub)

    return clustered


def _cluster_distance(a: str, b: str) -> float:
    """Compute topic distance between two cluster names.

    Returns 0.0 (identical) to 1.0 (completely unrelated).
    """
    kw_a = set(KEYWORDS.get(a, []))
    kw_b = set(KEYWORDS.get(b, []))
    if not kw_a or not kw_b:
        # Dynamic clusters: treat as highly distant from known clusters
        return 0.8
    intersection = kw_a & kw_b
    union = kw_a | kw_b
    return 1.0 - (len(intersection) / len(union)) if union else 0.5


def get_related_groups(
    clustered: dict[str, list[dict]],
    n_groups: int = 1,
    items_per_group: int = 3,
) -> list[list[dict]]:
    """Pick the best cluster(s) for related-insight analysis.

    Selection criteria (quality-first, deterministic):
    1. Score each item in each cluster by signal strength
    2. Prefer larger clusters (more industry activity)
    3. Take top-signal items from the best cluster
    """
    if not clustered:
        return []

    # Score and sort items within each cluster
    scored: dict[str, list[tuple[float, dict]]] = {}
    for name, items in clustered.items():
        if name == "其他":
            continue  # skip misc — no coherent theme for related analysis
        scored[name] = sorted(
            [(score_item_signal(it), it) for it in items],
            key=lambda x: x[0],
            reverse=True,
        )

    if not scored:
        return []

    # Rank clusters: larger first, break ties by average signal
    def cluster_rank(name: str) -> tuple[int, float]:
        items = scored[name]
        avg_signal = sum(s for s, _ in items) / len(items) if items else 0
        return (len(items), avg_signal)

    ranked = sorted(scored.keys(), key=cluster_rank, reverse=True)

    groups = []
    for name in ranked[:n_groups]:
        items = scored[name]
        size = min(items_per_group, len(items))
        groups.append([it for _, it in items[:size]])

    return groups


def get_crossdomain_groups(
    clustered: dict[str, list[dict]],
    n_groups: int = 1,
    items_per_group: int = 2,
) -> list[list[dict]]:
    """Pick item pairs from distant clusters for cross-domain innovation analysis.

    Selection criteria:
    1. Compute pairwise cluster distances
    2. Pick the most distant pair of clusters
    3. From each, take the highest-signal item
    """
    eligible = {name: items for name, items in clustered.items() if items}
    if len(eligible) < 2:
        return []

    # Compute all cluster pairs with distances
    names = list(eligible.keys())
    pairs: list[tuple[float, str, str]] = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            dist = _cluster_distance(names[i], names[j])
            pairs.append((dist, names[i], names[j]))

    # Sort by distance desc — prefer most distant pairs
    pairs.sort(key=lambda x: x[0], reverse=True)

    groups = []
    used_urls: set[str] = set()
    for _, name_a, name_b in pairs[:n_groups]:
        # Best signal item from each cluster
        pool_a = sorted(
            [it for it in eligible[name_a] if it.get("url") not in used_urls],
            key=lambda it: score_item_signal(it),
            reverse=True,
        )
        pool_b = sorted(
            [it for it in eligible[name_b] if it.get("url") not in used_urls],
            key=lambda it: score_item_signal(it),
            reverse=True,
        )

        if not pool_a or not pool_b:
            continue

        item_a = pool_a[0]
        item_b = pool_b[0]
        used_urls.add(item_a.get("url", ""))
        used_urls.add(item_b.get("url", ""))

        group = [item_a, item_b]
        if len(group) >= 2:
            groups.append(group)

    return groups
