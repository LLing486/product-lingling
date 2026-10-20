/* 灵灵 · 每周实验 —— 期数据（唯一真源）
 *
 * 为什么是 .js 不是 .json：
 *   JSON 要用 fetch 读，而 file:// 下 fetch 会被浏览器拦（CORS），
 *   这个站点的硬约束是「双击就能打开」。用经典 script 挂全局变量，
 *   file:// 和 http 两种打开方式都能跑，也不需要构建。
 *
 * 新增一期怎么做：在 episodes 数组末尾加一条 + 写一个 exp/pN.html。
 *   其余文件（index.html / p1-p3.html / exp-shell.js）零改动。
 *
 * 字段说明见 docs/episode-contract.md
 */
window.LING_EPISODES = {
  updated: "2026-10-20",
  episodes: [
    {
      no: 1,
      date: "2026-09-14",
      file: "p1.html",
      tag: "拖拽分类",
      title: "你是 AI 工具合规官，8 条使用申请该不该放行",
      short: "",
      motif: "判断类",
      card: { id: 203, title: "面向 AI 编程助手的军事/双用途滥用检测与合规审计平台" },
      signal: "Anthropic 报告称胡塞组织用 Claude Code 开发导弹制导软件。",
      sourceTitle: "阅读原文 ↗",
      sourceUrl: "https://aihot.news/items/cmu01iavi08reroymepsxnar2",
      judgmentCurrent: "",
      reviewPrev: ""
    },
    {
      no: 2,
      date: "2026-09-15",
      file: "p2.html",
      tag: "参数调整",
      title: "接手 2011 年的老系统，三个旋钮决定它能答什么",
      short: "",
      motif: "取舍类",
      card: { id: 206, title: "用 1M 上下文大模型把「企业遗留代码考古」变成可对话的活体知识库" },
      signal: "硅基流动上线开源模型 Hy4 preview（770B 总参数、1M 上下文）；DeepSeek-V4.1-Flash（Max）进入 Agent Arena 开源模型第 3 名。",
      sourceTitle: "阅读原文 ↗",
      sourceUrl: "https://aihot.news/items/cmu1gt8gn097trocnxxvdhxli",
      judgmentCurrent: "",
      reviewPrev: ""
    },
    {
      no: 3,
      date: "2026-09-16",
      file: "p3.html",
      tag: "分支选择",
      title: "凌晨 2:33 的告警，AI 能接管到哪一步",
      short: "凌晨 2:33 的告警",
      motif: "分支类",
      card: { id: 208, title: "用实时语音智能体替代运维值班工程师，让 AI 语音助手自主完成基础设施运维" },
      signal: "Google DeepMind 发布 Gemini 3.8 Live 和 3.8 Live Extended Thinking。",
      sourceTitle: "阅读原文 ↗",
      sourceUrl: "https://aihot.news/items/cmu2xqfxz02zhroc1hxuzi6jm",
      judgmentCurrent: "",
      reviewPrev: ""
    },
    {
      no: 4,
      date: "2026-10-08",
      file: "p4.html",
      tag: "阈值滑块",
      title: "让 0.8B 的小模型，替你批准大模型的每一个动作",
      short: "让 0.8B 替你签字",
      motif: "取舍类",
      card: { id: 246, title: "给 Windows PC 上的 AI Agent 装上「本地决策概率大脑」：0.8B 决策模型当行动选择的守门人" },
      signal: "Unsloth 开源教程：本地训练 Qwen3.5 0.8B 决策模型，准确率从 20.7% 提升至 74.3%。",
      sourceTitle: "阅读原文 ↗",
      sourceUrl: "https://aihot.news/items/y7db2ly158hip5dw1evmjw5kv",
      judgmentCurrent: "",
      reviewPrev: ""
    },
    {
      no: 5,
      date: "2026-10-18",
      file: "p5.html",
      tag: "选边",
      title: "AI 写了 90% 的代码，该由谁先看",
      short: "该由谁先看",
      motif: "对比类",
      card: { id: 272, title: "为 AI 写的代码做「风险分级评审与合并前检查」：自动识别 AI 生成 PR 中可能被 revert 的变更" },
      signal: "Anthropic 如何在 Claude 写下 Claude Code 约 90% 代码后重新设计代码评审。",
      sourceTitle: "阅读原文 ↗",
      sourceUrl: "https://aihot.news/items/p4mq9t7wyzlxritu15i6d8dtv",
      judgmentCurrent: "",
      reviewPrev: ""
    },
    {
      no: 6,
      date: "2026-10-20",
      file: "p6.html",
      tag: "技能改写",
      title: "被 Agent 挤出去的人，怎么变成 Agent 的必需品",
      short: "被挤出去的人",
      motif: "改写类",
      card: { id: 275, title: "「AI 学徒制」平台：让被 Agent 挤出初级岗位的开发者，成为中小企业 AI 交付项目的技术监理" },
      signal: "DeepSeek-V4.1-Flash-20261017 登顶 Code Arena: WebDev 开源模型榜首。",
      sourceTitle: "阅读原文 ↗",
      sourceUrl: "https://aihot.news/items/bm95oliei5mcgy2tau7e22d59",
      judgmentCurrent: "",
      reviewPrev: ""
    }
  ]
};
