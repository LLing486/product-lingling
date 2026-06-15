"""Keyword-based clustering for RSS items."""

import random

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


def cluster_items(items: list[dict]) -> dict[str, list[dict]]:
    """Cluster items by keyword matching on title+description.

    Returns dict {cluster_name: [items]}.
    Items with no match go to '其他'.
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

    return clustered


def get_related_groups(
    clustered: dict[str, list[dict]],
    n_groups: int = 3,
    items_per_group: int = 3,
) -> list[list[dict]]:
    """Pick n_groups clusters that have 2+ items, return groups of items from the same cluster."""
    # Clusters with enough items
    eligible = [name for name, items in clustered.items() if len(items) >= 2]
    if not eligible:
        return []

    chosen = random.sample(eligible, min(n_groups, len(eligible)))
    groups = []
    for name in chosen:
        pool = clustered[name]
        size = min(items_per_group, len(pool))
        groups.append(random.sample(pool, size))

    return groups


def get_crossdomain_groups(
    clustered: dict[str, list[dict]],
    n_groups: int = 3,
    items_per_group: int = 3,
) -> list[list[dict]]:
    """Pick items from different clusters to form cross-domain groups.

    Each group = 2-3 items from 2-3 different clusters.
    """
    # Only clusters with at least 1 item
    eligible = [name for name, items in clustered.items() if items]
    if len(eligible) < 2:
        return []

    groups = []
    for _ in range(n_groups):
        # Pick 2-3 different clusters
        n_clusters = min(items_per_group, len(eligible))
        chosen_clusters = random.sample(eligible, n_clusters)
        group = []
        for cname in chosen_clusters:
            item = random.choice(clustered[cname])
            group.append(item)
        if len(group) >= 2:
            groups.append(group)

    return groups
