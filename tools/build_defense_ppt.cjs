const fs = require("fs");
const path = require("path");
const PptxGenJS = require("pptxgenjs");
const sharp = require("sharp");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "答辩材料");
const PREVIEW = path.join(OUT, "ppt预览");
fs.mkdirSync(PREVIEW, { recursive: true });

const asset = (...parts) => path.join(ROOT, "docs", "thesis-assets", ...parts);
const outFile = (...parts) => path.join(OUT, ...parts);

const W = 13.333;
const H = 7.5;
const PXW = 1920;
const PXH = 1080;

const C = {
  ink: "17324D",
  muted: "62748A",
  bg: "F7FAFC",
  panel: "FFFFFF",
  mint: "2E8B7B",
  teal: "4FB7A5",
  blue: "3B6EA8",
  amber: "DDAA45",
  coral: "DA6B5D",
  line: "D9E5EA",
  pale: "EAF5F2",
  paleBlue: "EAF1F8",
  dark: "102A43",
};

const font = "Microsoft YaHei";
const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Codex";
pptx.subject = "本科毕业设计答辩";
pptx.title = "基于 Spring Boot 和 Vue 的心理健康服务平台";
pptx.company = "浙大宁波理工学院";
pptx.lang = "zh-CN";
pptx.theme = {
  headFontFace: font,
  bodyFontFace: font,
  lang: "zh-CN",
};
pptx.defineLayout({ name: "CUSTOM_WIDE", width: W, height: H });
pptx.layout = "CUSTOM_WIDE";
pptx.margin = 0;

function addText(slide, text, x, y, w, h, opts = {}) {
  slide.addText(text, {
    x, y, w, h,
    fontFace: font,
    color: opts.color || C.ink,
    fontSize: opts.size || 18,
    bold: !!opts.bold,
    align: opts.align || "left",
    valign: opts.valign || "top",
    fit: opts.fit || "shrink",
    breakLine: opts.breakLine,
    margin: opts.margin ?? 0.03,
    ...opts.extra,
  });
}

function bg(slide, fill = C.bg) {
  slide.background = { color: fill };
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: W, h: H, fill: { color: fill }, line: { color: fill, transparency: 100 } });
}

function header(slide, title, kicker = "心理健康服务平台 · 毕业设计答辩") {
  addText(slide, kicker, 0.62, 0.35, 5.4, 0.22, { size: 9.5, color: C.mint, bold: true });
  addText(slide, title, 0.62, 0.62, 9.1, 0.56, { size: 27, bold: true });
  slide.addShape(pptx.ShapeType.line, { x: 0.62, y: 1.28, w: 12.1, h: 0, line: { color: C.line, width: 1 } });
}

function footer(slide, n) {
  addText(slide, String(n).padStart(2, "0"), 12.18, 7.0, 0.5, 0.18, { size: 8.5, color: C.muted, align: "right" });
}

function rounded(slide, x, y, w, h, fill, line = C.line, r = 0.08) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: r,
    fill: { color: fill },
    line: { color: line, width: 1 },
  });
}

function bulletList(slide, items, x, y, w, h, opts = {}) {
  slide.addText(items.map(t => ({ text: t, options: { bullet: { type: "ul" }, breakLine: true } })), {
    x, y, w, h,
    fontFace: font,
    fontSize: opts.size || 17,
    color: opts.color || C.ink,
    breakLine: false,
    fit: "shrink",
    paraSpaceAfterPt: opts.after || 8,
    margin: 0.08,
  });
}

function image(slide, file, x, y, w, h, fit = "contain") {
  if (!fs.existsSync(file)) return;
  slide.addImage({ path: file, x, y, w, h, sizing: { type: fit, x, y, w, h } });
}

function sectionBar(slide, label, x, y, w, color) {
  slide.addShape(pptx.ShapeType.rect, { x, y, w, h: 0.07, fill: { color }, line: { color, transparency: 100 } });
  addText(slide, label, x, y + 0.12, w, 0.22, { size: 10.5, color, bold: true, align: "center" });
}

function card(slide, title, body, x, y, w, h, accent = C.mint) {
  rounded(slide, x, y, w, h, C.panel, "E1E8ED");
  slide.addShape(pptx.ShapeType.rect, { x, y, w: 0.08, h, fill: { color: accent }, line: { color: accent, transparency: 100 } });
  addText(slide, title, x + 0.22, y + 0.2, w - 0.35, 0.28, { size: 15.5, bold: true, color: C.ink });
  addText(slide, body, x + 0.22, y + 0.62, w - 0.35, h - 0.78, { size: 12.2, color: C.muted });
}

const slides = [];
function slide(title, notes, build, preview) {
  const s = pptx.addSlide();
  build(s, slides.length + 1);
  s.addNotes(notes);
  slides.push({ title, notes, preview });
}

slide("封面", [
  "各位老师好，我的毕业设计题目是《基于 Spring Boot 和 Vue 的心理健康服务平台的设计与实现》。",
  "这个系统面向高校心理健康服务场景，重点解决学生自助测评、预约咨询、在线沟通以及后台管理统计之间流程分散的问题。",
  "接下来我会从研究背景、需求分析、系统设计、核心实现、测试结果和总结展望六个方面进行汇报。"
], (s) => {
  bg(s, "F3F8F7");
  s.addShape(pptx.ShapeType.rect, { x: 8.3, y: 0, w: 5.05, h: H, fill: { color: C.paleBlue }, line: { transparency: 100 } });
  image(s, asset("screenshot-user-portal.png"), 7.35, 1.15, 5.35, 3.05, "cover");
  image(s, asset("screenshot-admin-dashboard.png"), 8.2, 3.55, 4.7, 2.75, "cover");
  s.addShape(pptx.ShapeType.rect, { x: 7.1, y: 0.88, w: 5.95, h: 5.72, fill: { color: "FFFFFF", transparency: 88 }, line: { transparency: 100 } });
  addText(s, "本科毕业设计答辩", 0.72, 0.66, 2.2, 0.28, { size: 11, color: C.mint, bold: true });
  addText(s, "基于 Spring Boot 和 Vue 的", 0.72, 1.32, 6.0, 0.58, { size: 24, color: C.ink, bold: true });
  addText(s, "心理健康服务平台", 0.72, 1.86, 6.45, 0.9, { size: 41, color: C.dark, bold: true });
  addText(s, "设计与实现", 0.72, 2.78, 3.2, 0.5, { size: 24, color: C.mint, bold: true });
  addText(s, "面向高校心理服务场景，贯通“测评、预约、咨询、管理、统计”的 Web 原型系统", 0.76, 3.65, 5.5, 0.64, { size: 15.5, color: C.muted });
  addText(s, "答辩人：陈爽    学号：3220421092\n技术栈：Spring Boot 3 · Vue 3 · MySQL · WebSocket · CatBoost", 0.76, 5.84, 5.85, 0.55, { size: 12.5, color: C.ink });
}, { kind: "cover" });

slide("研究背景与目标", [
  "首先是研究背景。高校心理服务常见问题是流程分散：学生测评、预约、咨询、老师管理和统计往往在不同渠道完成。",
  "所以本课题的目标不是替代专业咨询，而是用信息系统降低求助门槛、规范服务流程，并为咨询师和管理员提供可追溯的数据支持。",
  "系统最终聚焦三类角色：普通用户、心理咨询师和管理员。"
], (s, n) => {
  bg(s); header(s, "研究背景与系统目标"); footer(s, n);
  addText(s, "从“分散处理”到“闭环服务”", 0.72, 1.55, 5.2, 0.48, { size: 26, bold: true, color: C.dark });
  addText(s, "传统线下窗口、电话沟通与表格登记在效率、留痕、风险线索识别和跨角色协同上存在明显瓶颈。", 0.75, 2.12, 5.35, 0.6, { size: 15.5, color: C.muted });
  sectionBar(s, "学生端", 0.88, 3.15, 1.5, C.teal);
  sectionBar(s, "咨询师端", 2.88, 3.15, 1.5, C.blue);
  sectionBar(s, "管理员端", 4.88, 3.15, 1.5, C.amber);
  card(s, "低门槛求助", "自助测评、文章阅读、预约申请、在线沟通，降低首次表达压力。", 0.72, 4.0, 3.75, 1.55, C.teal);
  card(s, "过程可追溯", "预约状态、测评结果、聊天记录和操作日志形成连续服务线索。", 4.82, 4.0, 3.75, 1.55, C.blue);
  card(s, "数据辅助管理", "统计用户、预约、测评和风险分布，为资源配置提供参考。", 8.92, 4.0, 3.75, 1.55, C.amber);
}, {});

slide("需求分析", [
  "需求分析阶段，我按三类角色梳理功能边界。",
  "普通用户关注能不能方便地获取帮助，咨询师关注能不能减少预约和沟通的事务负担，管理员关注平台治理和风险监控。",
  "这张系统功能图也对应后续的前端路由权限和后端接口鉴权设计。"
], (s, n) => {
  bg(s); header(s, "需求分析：三类角色形成业务闭环"); footer(s, n);
  image(s, asset("project-system-function.png"), 0.62, 1.55, 7.2, 4.8, "contain");
  card(s, "普通用户", "注册登录、心理测评、预约咨询、文章阅读、在线聊天、个人资料维护。", 8.2, 1.62, 4.1, 1.2, C.teal);
  card(s, "心理咨询师", "资料维护、预约处理、历史消息查看、与用户在线沟通。", 8.2, 3.05, 4.1, 1.2, C.blue);
  card(s, "管理员", "用户与咨询师管理、文章通知管理、测评记录监控、数据看板统计。", 8.2, 4.48, 4.1, 1.2, C.amber);
}, {});

slide("总体架构", [
  "系统采用前后端分离架构。前端负责页面交互、路由控制和数据可视化；后端提供 REST API、认证鉴权、业务服务和数据访问。",
  "在线聊天使用 WebSocket 做实时推送，同时保留 REST 接口保存和加载历史消息。",
  "心理测评模块预留 Python CatBoost 推理路径，失败时回退到 Java 内置可解释逻辑。"
], (s, n) => {
  bg(s); header(s, "总体架构：前后端分离 + 实时通信 + 可选模型推理"); footer(s, n);
  image(s, asset("project-system-architecture.png"), 0.74, 1.55, 8.05, 4.92, "contain");
  addText(s, "架构要点", 9.08, 1.62, 2.8, 0.3, { size: 18, bold: true });
  bulletList(s, [
    "Vue 3 单页应用负责交互体验",
    "Axios 携带 JWT 访问 REST API",
    "Spring Security 做接口访问控制",
    "MyBatis-Plus 映射 MySQL 业务表",
    "WebSocket 支撑在线咨询推送",
    "CatBoost 作为可选风险筛查模型"
  ], 9.08, 2.1, 3.25, 3.05, { size: 14.5 });
  addText(s, "设计原则：前端体验控制，后端安全兜底；模型给出辅助线索，不替代专业判断。", 9.08, 5.65, 3.2, 0.58, { size: 13.5, color: C.mint, bold: true });
}, {});

slide("技术路线", [
  "技术路线上，前端使用 Vue 3、TypeScript、Element Plus、Pinia、Vue Router、ECharts。",
  "后端使用 Spring Boot 3、Spring Security、JWT、MyBatis-Plus、MySQL、Redis 和 WebSocket。",
  "机器学习部分使用 Python 和 CatBoost，主要用于心理风险筛查的训练、推理和可解释输出。"
], (s, n) => {
  bg(s); header(s, "技术路线：工程可维护与部署弹性"); footer(s, n);
  const cols = [
    ["前端表现层", "Vue 3\nTypeScript\nElement Plus\nPinia / Vue Router\nECharts", C.teal],
    ["接口与安全层", "Axios 统一封装\nJWT 无状态认证\nSpring Security\n统一异常处理\n角色访问控制", C.blue],
    ["后端业务层", "Spring Boot 3\nController / Service\nMyBatis-Plus\nWebSocket\nRedis 预留缓存", C.mint],
    ["数据与模型层", "MySQL 业务数据\nCatBoost 模型文件\nSHAP/特征重要性\nJava 回退预测器\n测试数据集", C.amber],
  ];
  cols.forEach((c, i) => {
    const x = 0.72 + i * 3.05;
    rounded(s, x, 1.65, 2.62, 4.65, "FFFFFF", "DCE8EA");
    s.addShape(pptx.ShapeType.rect, { x, y: 1.65, w: 2.62, h: 0.12, fill: { color: c[2] }, line: { transparency: 100 } });
    addText(s, c[0], x + 0.18, 1.98, 2.2, 0.34, { size: 17, bold: true, color: C.dark, align: "center" });
    addText(s, c[1], x + 0.28, 2.75, 2.06, 2.65, { size: 15, color: C.ink, align: "center", valign: "mid" });
  });
  addText(s, "选择原因：主流生态成熟、学习资料充分、模块边界清晰，适合本科毕设完整展示“需求—设计—实现—测试”的工程过程。", 0.92, 6.62, 11.4, 0.34, { size: 13, color: C.muted, align: "center" });
}, {});

slide("数据库设计", [
  "数据库以 sys_user 为身份中心，根据角色扩展咨询师资料、预约、测评记录和聊天消息。",
  "核心表包括用户表、咨询师资料表、预约表、量表表、测评记录表、聊天消息表、文章通知和操作日志等。",
  "这种设计能把身份、服务、测评、沟通和后台治理连接起来。"
], (s, n) => {
  bg(s); header(s, "数据库设计：围绕身份与服务过程建模"); footer(s, n);
  image(s, asset("project-er-diagram-detailed.png"), 0.66, 1.48, 7.65, 5.35, "contain");
  const items = [
    ["身份中心", "sys_user 保存账号、角色、基础资料，是认证与权限控制基础。"],
    ["服务链路", "appointment 连接用户与咨询师，保存预约时间、状态和问题描述。"],
    ["测评闭环", "assessment_scale 保存题目配置，assessment_record 保存答案、概率、等级和影响因素。"],
    ["沟通留痕", "chat_message 持久化双方消息，支持历史追溯和实时推送。"],
  ];
  items.forEach((it, idx) => card(s, it[0], it[1], 8.55, 1.55 + idx * 1.28, 3.72, 1.02, [C.teal, C.blue, C.amber, C.coral][idx]));
}, {});

slide("核心实现一：认证与权限", [
  "认证模块采用 JWT 无状态会话。",
  "用户登录后，后端生成 token 并返回角色信息；前端保存 token 后通过路由守卫控制页面入口。",
  "同时后端 Spring Security 和服务层二次校验负责真正的安全边界，防止只靠前端隐藏菜单造成越权。"
], (s, n) => {
  bg(s); header(s, "核心实现一：登录认证与权限控制"); footer(s, n);
  image(s, asset("project-auth-flow.png"), 0.72, 1.48, 7.1, 5.25, "contain");
  addText(s, "关键机制", 8.25, 1.58, 2.0, 0.3, { size: 18, bold: true });
  bulletList(s, [
    "BCrypt 保存密码摘要",
    "JWT 携带用户身份与角色",
    "前端路由元信息限制页面访问",
    "Axios 拦截器统一携带 token",
    "后端过滤器解析并注入认证上下文",
    "管理员与敏感业务接口做二次校验"
  ], 8.25, 2.05, 3.85, 3.15, { size: 14.8 });
  addText(s, "答辩时强调：前端控制是体验，后端校验才是安全边界。", 8.25, 5.78, 3.72, 0.44, { size: 13.5, color: C.coral, bold: true });
}, {});

slide("核心实现二：心理测评", [
  "心理测评模块是本课题的重点之一。",
  "用户提交答案后，后端解析特征，生成分数、风险概率、风险等级和主要影响因素。",
  "这里有两个路径：有 CatBoost 模型时优先调用模型推理，没有模型或推理失败时使用 Java 回退逻辑，保证演示和部署的可用性。"
], (s, n) => {
  bg(s); header(s, "核心实现二：心理测评与可解释风险分析"); footer(s, n);
  image(s, asset("project-assessment-flow-detail.png"), 0.68, 1.48, 6.15, 4.75, "contain");
  rounded(s, 7.1, 1.55, 4.95, 4.65, "FFFFFF", "DCE8EA");
  addText(s, "模型训练结果（MHP 数据集）", 7.35, 1.85, 3.4, 0.32, { size: 17, bold: true });
  const rows = [
    ["任务", "准确率", "F1", "AUC"],
    ["抑郁风险", "0.825", "0.870", "0.920"],
    ["焦虑风险", "0.835", "0.872", "0.901"],
    ["综合风险", "0.567", "0.689", "0.648"],
  ];
  rows.forEach((r, i) => {
    const y = 2.35 + i * 0.52;
    const fill = i === 0 ? C.pale : (i % 2 ? "FFFFFF" : "F8FBFC");
    s.addShape(pptx.ShapeType.rect, { x: 7.38, y, w: 4.35, h: 0.42, fill: { color: fill }, line: { color: "E4ECEF", width: 0.5 } });
    r.forEach((t, j) => addText(s, t, 7.5 + j * 1.05, y + 0.1, j === 0 ? 1.15 : 0.72, 0.18, { size: i === 0 ? 10.5 : 11.5, bold: i === 0, color: i === 0 ? C.mint : C.ink, align: j === 0 ? "left" : "center" }));
  });
  addText(s, "输出不是医学诊断，而是风险筛查线索：概率、等级、分析文本和主要影响因素共同呈现。", 7.38, 4.85, 4.25, 0.62, { size: 13.2, color: C.muted });
}, {});

slide("核心实现三：预约与在线聊天", [
  "预约咨询模块负责连接用户和咨询师。",
  "用户创建预约后进入待确认状态，咨询师同意后双方才能进入沟通场景。",
  "聊天模块采用 REST 持久化加 WebSocket 推送，实时连接异常时仍可以通过 REST 发送和加载历史消息。"
], (s, n) => {
  bg(s); header(s, "核心实现三：预约状态流转与在线咨询"); footer(s, n);
  image(s, asset("project-appointment-flow.png"), 0.65, 1.55, 5.85, 4.8, "contain");
  image(s, asset("project-chat-flow.png"), 6.88, 1.55, 5.85, 4.8, "contain");
  addText(s, "预约：待确认 → 已确认/已拒绝 → 可取消/改期", 0.8, 6.45, 5.2, 0.26, { size: 13, color: C.blue, bold: true, align: "center" });
  addText(s, "聊天：先保存消息，再向在线会话推送", 7.18, 6.45, 5.0, 0.26, { size: 13, color: C.teal, bold: true, align: "center" });
}, {});

slide("系统展示", [
  "这一页展示实际系统界面。",
  "登录后普通用户可以进入门户、测评、咨询师列表和聊天；管理员端可以查看数据看板、管理用户咨询师、文章通知和测评记录。",
  "如果现场允许演示，我建议按登录、用户测评、预约、聊天、管理员看板的顺序演示，时间控制在两分钟内。"
], (s, n) => {
  bg(s); header(s, "系统展示：用户端与管理员端主要页面"); footer(s, n);
  const imgs = [
    ["screenshot-login.png", 0.72, 1.45, 3.65, 2.1, "登录认证"],
    ["screenshot-user-portal.png", 4.72, 1.45, 3.65, 2.1, "用户门户"],
    ["screenshot-assessment.png", 8.72, 1.45, 3.65, 2.1, "心理测评"],
    ["screenshot-chat.png", 0.72, 4.08, 3.65, 2.1, "在线聊天"],
    ["screenshot-admin-dashboard.png", 4.72, 4.08, 3.65, 2.1, "管理员看板"],
  ];
  imgs.forEach(([f, x, y, w, h, label]) => {
    rounded(s, x - 0.03, y - 0.03, w + 0.06, h + 0.38, "FFFFFF", "DCE8EA");
    image(s, asset(f), x, y, w, h, "cover");
    addText(s, label, x, y + h + 0.12, w, 0.18, { size: 10.5, color: C.muted, align: "center" });
  });
  addText(s, "页面围绕三类角色分流，突出“测评—预约—沟通—管理”的完整业务路径。", 8.78, 4.42, 3.42, 1.2, { size: 18, color: C.dark, bold: true, align: "center", valign: "mid" });
}, {});

slide("测试与验证", [
  "测试部分围绕功能完整性、权限边界、异常处理和兼容性展开。",
  "重点验证了登录鉴权、角色访问控制、测评提交、预约状态流转、聊天记录和管理员看板等流程。",
  "测试结果表明主要业务流程能够跑通，系统具备基本可用性和扩展性。"
], (s, n) => {
  bg(s); header(s, "测试与验证：覆盖主流程与边界行为"); footer(s, n);
  image(s, asset("project-test-case-table.png"), 0.65, 1.52, 7.05, 4.9, "contain");
  card(s, "功能测试", "登录、注册、测评提交、预约创建、聊天发送、文章通知管理。", 8.08, 1.58, 4.0, 1.08, C.teal);
  card(s, "权限测试", "未登录拦截、角色跳转、普通用户访问管理员页面被拒绝。", 8.08, 2.88, 4.0, 1.08, C.blue);
  card(s, "异常测试", "错误 token、空表单、异常量表配置、WebSocket 连接异常兜底。", 8.08, 4.18, 4.0, 1.08, C.coral);
  addText(s, "结论：主要业务流程可用，页面在桌面和窄屏场景下具备基本适配能力。", 8.12, 5.85, 3.85, 0.42, { size: 13.5, bold: true, color: C.mint });
}, {});

slide("成果总结", [
  "总结一下，本课题完成了一套可运行的前后端分离 Web 原型。",
  "主要成果是贯通了心理文章、心理测评、预约咨询、在线聊天和后台管理统计流程。",
  "创新或特色主要体现在三点：多角色闭环、可解释测评结果、以及聊天模块的持久化和实时推送结合。"
], (s, n) => {
  bg(s); header(s, "成果总结：完成可运行的多角色服务平台"); footer(s, n);
  addText(s, "完成成果", 0.82, 1.55, 2.1, 0.35, { size: 20, bold: true });
  bulletList(s, [
    "实现普通用户、咨询师、管理员三类角色入口",
    "完成测评、预约、聊天、文章、通知、看板等核心模块",
    "形成数据库脚本、论文图表、模型训练脚本与前后端工程",
    "提供可选 CatBoost 推理与 Java 回退逻辑"
  ], 0.82, 2.05, 5.45, 2.2, { size: 16 });
  const blocks = [
    ["多角色闭环", "宣传教育、心理测评、预约咨询、在线沟通和后台治理在同一平台中贯通。", C.teal],
    ["可解释测评", "展示风险概率、等级、模型名称和主要影响因素，避免只给单一分数。", C.blue],
    ["通信韧性", "聊天记录先持久化，再通过 WebSocket 推送，实时通道异常时 REST 兜底。", C.amber],
  ];
  blocks.forEach((b, i) => card(s, b[0], b[1], 7.05, 1.58 + i * 1.48, 4.85, 1.18, b[2]));
}, {});

slide("不足与展望", [
  "最后是不足与展望。",
  "当前系统仍是原型级实现，未来可以从危机干预流程、隐私合规、移动端体验、模型治理和消息提醒等方面继续完善。",
  "特别是心理健康场景必须强调边界：平台只能提供辅助服务和风险线索，真正的危机处置仍需要专业人员和学校制度流程配合。"
], (s, n) => {
  bg(s); header(s, "不足与展望：从原型系统走向可运营平台"); footer(s, n);
  const items = [
    ["危机干预", "补充高风险预警、人工复核、转介与应急联系流程。"],
    ["隐私合规", "完善数据最小化、敏感字段脱敏、审计日志和导出审批。"],
    ["模型治理", "增加模型版本、漂移监测、个体解释和人工确认机制。"],
    ["体验扩展", "适配移动端、小程序、预约提醒和消息通知渠道。"],
  ];
  items.forEach((it, idx) => {
    const x = 0.95 + (idx % 2) * 5.75;
    const y = 1.65 + Math.floor(idx / 2) * 2.0;
    card(s, it[0], it[1], x, y, 4.9, 1.45, [C.coral, C.blue, C.amber, C.teal][idx]);
  });
  addText(s, "答辩收束句：本系统不替代专业判断，而是提升服务可达性、流程规范性和数据可追溯性。", 1.15, 6.02, 10.8, 0.48, { size: 17, bold: true, color: C.dark, align: "center" });
}, {});

slide("致谢", [
  "我的汇报到这里结束，感谢各位老师的聆听，恳请老师批评指正。"
], (s, n) => {
  bg(s, "F3F8F7"); footer(s, n);
  addText(s, "感谢各位老师聆听", 2.25, 2.2, 8.8, 0.75, { size: 40, bold: true, color: C.dark, align: "center" });
  addText(s, "恳请批评指正", 4.18, 3.18, 4.95, 0.42, { size: 22, color: C.mint, bold: true, align: "center" });
  addText(s, "基于 Spring Boot 和 Vue 的心理健康服务平台的设计与实现", 2.8, 4.7, 7.8, 0.36, { size: 15, color: C.muted, align: "center" });
}, {});

async function makePreview(i, meta) {
  const title = meta.title;
  const bg = meta.preview?.kind === "cover" ? "#F3F8F7" : "#F7FAFC";
  const svg = `
  <svg xmlns="http://www.w3.org/2000/svg" width="${PXW}" height="${PXH}" viewBox="0 0 ${PXW} ${PXH}">
    <rect width="100%" height="100%" fill="${bg}"/>
    <rect x="88" y="76" width="1744" height="4" fill="#2E8B7B"/>
    <text x="96" y="160" font-family="Microsoft YaHei, SimHei, sans-serif" font-size="${i === 0 ? 82 : 58}" font-weight="700" fill="#102A43">${escapeXml(title)}</text>
    <text x="96" y="236" font-family="Microsoft YaHei, SimHei, sans-serif" font-size="28" fill="#62748A">基于 Spring Boot 和 Vue 的心理健康服务平台 · 毕业设计答辩</text>
    ${i === 0 ? `<text x="96" y="430" font-family="Microsoft YaHei, SimHei, sans-serif" font-size="38" fill="#2E8B7B">测评 · 预约 · 咨询 · 管理 · 统计</text>` : ""}
    <text x="96" y="900" font-family="Microsoft YaHei, SimHei, sans-serif" font-size="24" fill="#62748A">${escapeXml(meta.notes[0] || "")}</text>
    <text x="1810" y="996" text-anchor="end" font-family="Microsoft YaHei, SimHei, sans-serif" font-size="22" fill="#62748A">${String(i + 1).padStart(2, "0")}</text>
  </svg>`;
  const file = path.join(PREVIEW, `slide-${String(i + 1).padStart(2, "0")}.png`);
  await sharp(Buffer.from(svg)).png().toFile(file);
}

function escapeXml(s) {
  return String(s).replace(/[<>&'"]/g, c => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", "'": "&apos;", '"': "&quot;" }[c]));
}

async function writeGuide() {
  const lines = [];
  lines.push("# 毕设答辩讲稿与讲述建议\n");
  lines.push("## 总体节奏\n");
  lines.push("- 建议总时长：8-10 分钟。若学院要求 5 分钟，保留第 1、2、4、8、9、10、11、12 页，其他页一句话带过。\n");
  lines.push("- 讲述主线：为什么做 → 给谁用 → 怎么设计 → 核心功能怎么实现 → 测试结果如何 → 不足和展望。\n");
  lines.push("- 现场演示顺序：登录 → 用户测评 → 预约咨询 → 在线聊天 → 管理员看板。演示控制在 2 分钟内，失败时直接回到 PPT 讲截图。\n");
  lines.push("## 逐页讲稿\n");
  slides.forEach((s, i) => {
    lines.push(`### ${i + 1}. ${s.title}\n`);
    s.notes.forEach(n => lines.push(`${n}\n`));
  });
  lines.push("## 常见提问回答\n");
  lines.push("**问：平台能否替代心理咨询师？** 不能。平台定位是信息化辅助，提供低门槛入口、流程留痕和风险线索，真正判断与危机处置仍依赖专业人员和学校制度。\n");
  lines.push("**问：为什么使用前后端分离？** 便于前端页面迭代、后端接口复用和后续扩展移动端；同时职责边界清晰，适合三类角色和多个业务模块并行维护。\n");
  lines.push("**问：JWT 和 Spring Security 分别做什么？** JWT 用于无状态身份凭证传递，Spring Security 负责服务端过滤器链和接口访问控制；前端路由守卫只改善体验，不能作为安全边界。\n");
  lines.push("**问：测评模型结果如何理解？** 模型输出是风险筛查线索，不是医学诊断；系统展示概率、等级和影响因素，目的是辅助理解和后续咨询，而不是自动定性。\n");
  lines.push("**问：WebSocket 断开怎么办？** 消息发送和历史加载保留 REST 接口，WebSocket 主要负责实时推送，因此实时连接异常不会导致聊天记录丢失。\n");
  lines.push("**问：项目最大的特色是什么？** 多角色业务闭环、可解释心理测评、以及在线聊天“持久化 + 实时推送”的组合设计。\n");
  fs.writeFileSync(outFile("答辩讲稿与问答准备.md"), lines.join("\n"), "utf8");
}

(async () => {
  await pptx.writeFile({ fileName: outFile("基于SpringBoot和Vue的心理健康服务平台-毕设答辩.pptx") });
  await writeGuide();
  for (let i = 0; i < slides.length; i++) await makePreview(i, slides[i]);
  console.log(JSON.stringify({
    pptx: outFile("基于SpringBoot和Vue的心理健康服务平台-毕设答辩.pptx"),
    guide: outFile("答辩讲稿与问答准备.md"),
    previews: PREVIEW,
    slides: slides.length
  }, null, 2));
})();
