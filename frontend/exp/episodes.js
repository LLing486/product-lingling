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
  updated: "2026-09-22",
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
    }
  ]
};
