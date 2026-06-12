const fs = require("fs");
const path = require("path");

const NODE_MODULES = process.env.CODEX_NODE_MODULES || "C:/Users/28994/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules";
const PptxGenJS = require(path.join(NODE_MODULES, "pptxgenjs"));
const sharp = require(path.join(NODE_MODULES, "sharp"));

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "答辩材料");
const PREVIEW = path.join(OUT, "单页预览");
fs.mkdirSync(PREVIEW, { recursive: true });

const pptx = new PptxGenJS();
const W = 13.333;
const H = 7.5;
const PXW = 1920;
const PXH = 1080;
const font = "Microsoft YaHei";

const C = {
  ink: "17324D",
  dark: "102A43",
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
};

pptx.author = "Codex";
pptx.subject = "本科毕业设计答辩单页";
pptx.title = "研究背景与系统目标";
pptx.company = "浙大宁波理工学院";
pptx.lang = "zh-CN";
pptx.defineLayout({ name: "CUSTOM_WIDE", width: W, height: H });
pptx.layout = "CUSTOM_WIDE";
pptx.margin = 0;
pptx.theme = {
  headFontFace: font,
  bodyFontFace: font,
  lang: "zh-CN",
};

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
    margin: opts.margin ?? 0.04,
    breakLine: opts.breakLine,
    paraSpaceAfterPt: opts.paraSpaceAfterPt,
    ...opts.extra,
  });
}

function rounded(slide, x, y, w, h, fill, line = C.line) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.08,
    fill: { color: fill },
    line: { color: line, width: 1 },
  });
}

function bulletList(slide, items, x, y, w, h, opts = {}) {
  slide.addText(items.map((item) => ({
    text: item,
    options: { bullet: { type: "ul" }, breakLine: true },
  })), {
    x, y, w, h,
    fontFace: font,
    fontSize: opts.size || 14,
    color: opts.color || C.ink,
    fit: "shrink",
    paraSpaceAfterPt: opts.after || 7,
    margin: 0.08,
  });
}

function addSlide() {
  const s = pptx.addSlide();
  s.background = { color: C.bg };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: W, h: H, fill: { color: C.bg }, line: { transparency: 100 } });
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.2, h: H, fill: { color: C.mint }, line: { transparency: 100 } });
  s.addShape(pptx.ShapeType.rect, { x: 0.72, y: 1.32, w: 11.85, h: 0.03, fill: { color: C.line }, line: { transparency: 100 } });

  addText(s, "心理健康服务平台 · 毕业设计答辩", 0.72, 0.42, 4.8, 0.25, { size: 10, color: C.mint, bold: true });
  addText(s, "研究背景与系统目标", 0.72, 0.72, 5.8, 0.55, { size: 30, color: C.dark, bold: true });
  addText(s, "从分散处理走向可追溯的服务闭环", 7.15, 0.82, 5.1, 0.36, { size: 15, color: C.muted, align: "right" });

  addText(s, "研究背景", 0.82, 1.62, 1.65, 0.32, { size: 18, bold: true, color: C.dark });
  addText(
    s,
    "高校学生面临学业、人际、就业等多重压力，心理服务需求持续增加。传统服务方式常依赖线下登记、电话沟通和人工统计，容易出现入口分散、过程难追踪、数据难沉淀的问题。",
    0.82,
    2.08,
    5.35,
    1.12,
    { size: 14.6, color: C.ink, fit: "shrink" }
  );

  rounded(s, 0.82, 3.5, 5.35, 1.72, C.panel, "DCE8EA");
  addText(s, "主要痛点", 1.06, 3.72, 1.5, 0.24, { size: 15.5, bold: true, color: C.coral });
  bulletList(s, [
    "学生端：求助入口不集中，首次表达压力较高",
    "咨询师端：预约与沟通记录分散，服务连续性不足",
    "管理端：风险线索和服务数据缺少统一统计视图",
  ], 1.02, 4.08, 4.85, 0.88, { size: 12.0, after: 4 });

  addText(s, "系统目标", 6.95, 1.62, 1.65, 0.32, { size: 18, bold: true, color: C.dark });
  const goals = [
    ["01", "降低求助门槛", "提供注册登录、心理文章、自助测评、咨询师浏览与预约入口，让学生更容易开始使用服务。", C.teal],
    ["02", "规范服务流程", "围绕“测评—预约—沟通—反馈”建立连续业务链路，保存关键过程数据。", C.blue],
    ["03", "辅助后台管理", "通过角色权限、测评记录、预约状态和数据看板，为管理员提供可追溯的管理依据。", C.amber],
  ];
  goals.forEach(([num, title, body, color], i) => {
    const y = 2.06 + i * 1.18;
    s.addShape(pptx.ShapeType.rect, { x: 6.95, y, w: 0.08, h: 0.86, fill: { color }, line: { transparency: 100 } });
    addText(s, num, 7.22, y + 0.02, 0.42, 0.26, { size: 12.5, color, bold: true });
    addText(s, title, 7.72, y, 2.25, 0.28, { size: 15.2, color: C.dark, bold: true });
    addText(s, body, 7.72, y + 0.36, 4.3, 0.45, { size: 11.8, color: C.muted });
  });

  rounded(s, 0.82, 5.55, 11.35, 0.76, C.pale, "CFE6DE");
  addText(
    s,
    "课题定位：本系统不替代专业心理咨询，而是以信息化方式提升服务可达性、流程规范性和数据可追溯性，为后续人工评估与管理决策提供辅助线索。",
    1.05,
    5.77,
    10.85,
    0.36,
    { size: 13.4, color: C.mint, bold: true, align: "center" }
  );
  addText(s, "02", 12.18, 7.0, 0.5, 0.18, { size: 8.5, color: C.muted, align: "right" });

  s.addNotes(`本页重写后的讲述建议：
首先介绍研究背景。高校学生面临学业、人际和就业等多重压力，心理服务需求持续增加。
传统处理方式依赖线下登记、电话沟通和人工统计，容易出现入口分散、过程难追踪、数据难沉淀的问题。
因此本课题的目标，是建设一个面向学生、咨询师和管理员三类角色的心理健康服务平台。
系统重点不是替代专业咨询，而是降低学生求助门槛，规范测评、预约、沟通和管理流程，并为后台统计和后续人工评估提供辅助线索。`);
}

function escapeXml(s) {
  return String(s).replace(/[<>&'"]/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", "'": "&apos;", '"': "&quot;" }[c]));
}

async function makePreview() {
  const svg = `
  <svg xmlns="http://www.w3.org/2000/svg" width="${PXW}" height="${PXH}" viewBox="0 0 ${PXW} ${PXH}">
    <rect width="100%" height="100%" fill="#${C.bg}"/>
    <rect width="29" height="1080" fill="#${C.mint}"/>
    <text x="104" y="98" font-family="${font}, SimHei, sans-serif" font-size="29" font-weight="700" fill="#${C.mint}">心理健康服务平台 · 毕业设计答辩</text>
    <text x="104" y="184" font-family="${font}, SimHei, sans-serif" font-size="74" font-weight="700" fill="#${C.dark}">研究背景与系统目标</text>
    <line x1="104" y1="190" x2="1810" y2="190" stroke="#${C.line}" stroke-width="4"/>
    <text x="1180" y="168" font-family="${font}, SimHei, sans-serif" font-size="32" fill="#${C.muted}">从分散处理走向可追溯的服务闭环</text>
    <text x="118" y="278" font-family="${font}, SimHei, sans-serif" font-size="40" font-weight="700" fill="#${C.dark}">研究背景</text>
    <text x="118" y="338" font-family="${font}, SimHei, sans-serif" font-size="28" fill="#${C.ink}">高校学生面临学业、人际、就业等多重压力，心理服务需求持续增加。</text>
    <text x="118" y="382" font-family="${font}, SimHei, sans-serif" font-size="28" fill="#${C.ink}">传统服务方式常依赖线下登记、电话沟通和人工统计，容易出现入口</text>
    <text x="118" y="426" font-family="${font}, SimHei, sans-serif" font-size="28" fill="#${C.ink}">分散、过程难追踪、数据难沉淀的问题。</text>
    <rect x="118" y="504" width="770" height="248" rx="13" fill="#fff" stroke="#DCE8EA"/>
    <text x="152" y="570" font-family="${font}, SimHei, sans-serif" font-size="34" font-weight="700" fill="#${C.coral}">主要痛点</text>
    <text x="150" y="633" font-family="${font}, SimHei, sans-serif" font-size="25" fill="#${C.ink}">• 学生端：求助入口不集中，首次表达压力较高</text>
    <text x="150" y="680" font-family="${font}, SimHei, sans-serif" font-size="25" fill="#${C.ink}">• 咨询师端：预约与沟通记录分散，服务连续性不足</text>
    <text x="150" y="727" font-family="${font}, SimHei, sans-serif" font-size="25" fill="#${C.ink}">• 管理端：风险线索和服务数据缺少统一统计视图</text>
    <text x="1001" y="278" font-family="${font}, SimHei, sans-serif" font-size="40" font-weight="700" fill="#${C.dark}">系统目标</text>
    ${[
      ["01", "降低求助门槛", "提供注册登录、心理文章、自助测评、咨询师浏览与预约入口，让学生更容易开始使用服务。", C.teal, 315],
      ["02", "规范服务流程", "围绕“测评—预约—沟通—反馈”建立连续业务链路，保存关键过程数据。", C.blue, 485],
      ["03", "辅助后台管理", "通过角色权限、测评记录、预约状态和数据看板，为管理员提供可追溯的管理依据。", C.amber, 655],
    ].map(([num, title, body, color, y]) => `
      <rect x="1001" y="${y - 18}" width="12" height="124" fill="#${color}"/>
      <text x="1040" y="${y + 20}" font-family="${font}, SimHei, sans-serif" font-size="29" font-weight="700" fill="#${color}">${num}</text>
      <text x="1112" y="${y + 18}" font-family="${font}, SimHei, sans-serif" font-size="33" font-weight="700" fill="#${C.dark}">${title}</text>
      <text x="1112" y="${y + 55}" font-family="${font}, SimHei, sans-serif" font-size="23" fill="#${C.muted}">${escapeXml(body.slice(0, 34))}</text>
      <text x="1112" y="${y + 90}" font-family="${font}, SimHei, sans-serif" font-size="23" fill="#${C.muted}">${escapeXml(body.slice(34))}</text>
    `).join("")}
    <rect x="118" y="799" width="1634" height="109" rx="13" fill="#${C.pale}" stroke="#CFE6DE"/>
    <text x="210" y="858" font-family="${font}, SimHei, sans-serif" font-size="27" font-weight="700" fill="#${C.mint}">课题定位：本系统不替代专业心理咨询，而是提升服务可达性、流程规范性和数据可追溯性，</text>
    <text x="488" y="896" font-family="${font}, SimHei, sans-serif" font-size="27" font-weight="700" fill="#${C.mint}">为后续人工评估与管理决策提供辅助线索。</text>
    <text x="1755" y="995" font-family="${font}, SimHei, sans-serif" font-size="24" fill="#${C.muted}">02</text>
  </svg>`;
  const file = path.join(PREVIEW, "研究背景与系统目标-单页.png");
  await sharp(Buffer.from(svg)).png().toFile(file);
  return file;
}

(async () => {
  addSlide();
  const pptFile = path.join(OUT, "研究背景与系统目标-单页.pptx");
  await pptx.writeFile({ fileName: pptFile });
  const preview = await makePreview();
  console.log(JSON.stringify({ pptx: pptFile, preview }, null, 2));
})();
