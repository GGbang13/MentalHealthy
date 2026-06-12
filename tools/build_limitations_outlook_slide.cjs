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
};

pptx.author = "Codex";
pptx.subject = "本科毕业设计答辩单页";
pptx.title = "不足与展望";
pptx.company = "浙大宁波理工学院";
pptx.lang = "zh-CN";
pptx.defineLayout({ name: "CUSTOM_WIDE", width: W, height: H });
pptx.layout = "CUSTOM_WIDE";
pptx.margin = 0;
pptx.theme = { headFontFace: font, bodyFontFace: font, lang: "zh-CN" };

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

function addBlock(slide, idx, title, now, future, x, y, color) {
  slide.addShape(pptx.ShapeType.rect, { x, y: y + 0.02, w: 0.08, h: 1.26, fill: { color }, line: { transparency: 100 } });
  addText(slide, idx, x + 0.22, y, 0.42, 0.24, { size: 11.5, color, bold: true });
  addText(slide, title, x + 0.75, y - 0.01, 2.35, 0.28, { size: 15.2, color: C.dark, bold: true });
  addText(slide, `当前不足：${now}`, x + 0.75, y + 0.36, 4.4, 0.34, { size: 10.8, color: C.muted });
  addText(slide, `后续展望：${future}`, x + 0.75, y + 0.78, 4.4, 0.42, { size: 10.8, color: C.ink });
}

function addSlide() {
  const s = pptx.addSlide();
  s.background = { color: C.bg };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: W, h: H, fill: { color: C.bg }, line: { transparency: 100 } });
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.2, h: H, fill: { color: C.mint }, line: { transparency: 100 } });
  addText(s, "心理健康服务平台 · 毕业设计答辩", 0.72, 0.42, 4.8, 0.25, { size: 10, color: C.mint, bold: true });
  addText(s, "不足与展望", 0.72, 0.72, 4.2, 0.55, { size: 30, color: C.dark, bold: true });
  addText(s, "从原型系统走向可运营、可治理、可持续迭代的平台", 6.8, 0.82, 5.45, 0.36, { size: 15, color: C.muted, align: "right" });
  s.addShape(pptx.ShapeType.rect, { x: 0.72, y: 1.32, w: 11.85, h: 0.03, fill: { color: C.line }, line: { transparency: 100 } });

  rounded(s, 0.82, 1.64, 11.7, 0.78, C.pale, "CFE6DE");
  addText(s, "当前系统已完成多角色入口、测评、预约、聊天、文章通知与后台看板等核心功能，但仍属于原型系统。后续需要在安全合规、服务闭环、模型治理和多端体验上进一步完善。", 1.05, 1.88, 11.2, 0.28, { size: 13.4, color: C.mint, bold: true, align: "center" });

  addBlock(
    s,
    "01",
    "危机干预机制",
    "高风险测评结果目前主要以页面提示为主，缺少人工复核和应急处置闭环。",
    "增加高风险预警、咨询师复核、转介记录、紧急联系人和学校危机干预流程。",
    0.95,
    2.85,
    C.coral
  );
  addBlock(
    s,
    "02",
    "隐私与安全合规",
    "心理测评、聊天记录等数据较敏感，当前脱敏、授权和审计粒度仍可细化。",
    "完善字段脱敏、访问审批、数据导出控制、操作审计和最小化采集策略。",
    6.9,
    2.85,
    C.blue
  );
  addBlock(
    s,
    "03",
    "模型解释与治理",
    "CatBoost 风险筛查模型可输出影响因素，但模型版本、漂移监测和个体解释仍不足。",
    "引入模型版本管理、SHAP 个体解释、训练数据更新和人工确认机制。",
    0.95,
    4.55,
    C.amber
  );
  addBlock(
    s,
    "04",
    "平台体验与扩展",
    "目前主要面向 Web 端演示，预约提醒、移动端适配和实时互动能力仍可增强。",
    "扩展移动端或小程序，接入消息提醒、文件上传和会话缓存。",
    6.9,
    4.55,
    C.teal
  );

  addText(s, "收束：平台定位是心理健康服务的信息化辅助工具，不替代专业判断；未来重点是让流程更安全、数据更可信、服务更连续。", 1.2, 6.62, 10.8, 0.3, { size: 14.8, color: C.dark, bold: true, align: "center" });
  addText(s, "15", 12.18, 7.0, 0.5, 0.18, { size: 8.5, color: C.muted, align: "right" });

  s.addNotes(`本页讲述建议：
最后说明不足与展望。当前系统已经实现核心功能，但仍是原型系统。
后续可以从四个方向完善：第一是危机干预，把高风险识别和人工复核、转介流程结合起来；第二是隐私合规，对心理测评和聊天记录加强脱敏、授权和审计；第三是模型治理，增加模型版本管理、个体解释和人工确认；第四是体验扩展，进一步支持移动端、预约提醒和更稳定的实时通信。
收束时强调，平台不替代专业判断，而是提升服务可达性、流程规范性和数据可追溯性。`);
}

function escapeXml(s) {
  return String(s).replace(/[<>&'"]/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", "'": "&apos;", '"': "&quot;" }[c]));
}

function svgBlock(num, title, now, future, x, y, color) {
  return `
    <rect x="${x}" y="${y}" width="12" height="181" fill="#${color}"/>
    <text x="${x + 40}" y="${y + 27}" font-family="${font}, SimHei, sans-serif" font-size="28" font-weight="700" fill="#${color}">${num}</text>
    <text x="${x + 108}" y="${y + 26}" font-family="${font}, SimHei, sans-serif" font-size="35" font-weight="700" fill="#${C.dark}">${title}</text>
    <text x="${x + 108}" y="${y + 82}" font-family="${font}, SimHei, sans-serif" font-size="22" fill="#${C.muted}">当前不足：${escapeXml(now)}</text>
    <text x="${x + 108}" y="${y + 139}" font-family="${font}, SimHei, sans-serif" font-size="22" fill="#${C.ink}">后续展望：${escapeXml(future.slice(0, 31))}</text>
    <text x="${x + 108}" y="${y + 171}" font-family="${font}, SimHei, sans-serif" font-size="22" fill="#${C.ink}">${escapeXml(future.slice(31))}</text>`;
}

async function makePreview() {
  const blocks = [
    ["01", "危机干预机制", "高风险结果缺少人工复核和应急处置闭环。", "增加高风险预警、咨询师复核、转介记录和学校危机干预流程。", 137, 410, C.coral],
    ["02", "隐私与安全合规", "敏感数据的脱敏、授权和审计粒度仍可细化。", "完善字段脱敏、访问审批、数据导出控制和操作审计。", 994, 410, C.blue],
    ["03", "模型解释与治理", "模型版本、漂移监测和个体解释仍不足。", "引入模型版本管理、SHAP 个体解释、数据更新和人工确认机制。", 137, 655, C.amber],
    ["04", "平台体验与扩展", "预约提醒、移动端适配和实时互动能力仍可增强。", "扩展移动端或小程序，接入消息提醒、文件上传和会话缓存。", 994, 655, C.teal],
  ];
  const svg = `
  <svg xmlns="http://www.w3.org/2000/svg" width="${PXW}" height="${PXH}" viewBox="0 0 ${PXW} ${PXH}">
    <rect width="100%" height="100%" fill="#${C.bg}"/>
    <rect width="29" height="1080" fill="#${C.mint}"/>
    <text x="104" y="98" font-family="${font}, SimHei, sans-serif" font-size="29" font-weight="700" fill="#${C.mint}">心理健康服务平台 · 毕业设计答辩</text>
    <text x="104" y="184" font-family="${font}, SimHei, sans-serif" font-size="74" font-weight="700" fill="#${C.dark}">不足与展望</text>
    <text x="995" y="168" font-family="${font}, SimHei, sans-serif" font-size="32" fill="#${C.muted}">从原型系统走向可运营、可治理、可持续迭代的平台</text>
    <line x1="104" y1="190" x2="1810" y2="190" stroke="#${C.line}" stroke-width="4"/>
    <rect x="118" y="236" width="1685" height="112" rx="13" fill="#${C.pale}" stroke="#CFE6DE"/>
    <text x="205" y="300" font-family="${font}, SimHei, sans-serif" font-size="27" font-weight="700" fill="#${C.mint}">当前系统已完成核心功能，但仍属于原型系统；后续需在安全合规、服务闭环、模型治理和多端体验上进一步完善。</text>
    ${blocks.map((b) => svgBlock(...b)).join("")}
    <text x="960" y="956" text-anchor="middle" font-family="${font}, SimHei, sans-serif" font-size="28" font-weight="700" fill="#${C.dark}">收束：平台不替代专业判断；未来重点是让流程更安全、数据更可信、服务更连续。</text>
    <text x="1755" y="995" font-family="${font}, SimHei, sans-serif" font-size="24" fill="#${C.muted}">15</text>
  </svg>`;
  const file = path.join(PREVIEW, "不足与展望-单页.png");
  await sharp(Buffer.from(svg)).png().toFile(file);
  return file;
}

(async () => {
  addSlide();
  const pptFile = path.join(OUT, "不足与展望-单页.pptx");
  await pptx.writeFile({ fileName: pptFile });
  const preview = await makePreview();
  console.log(JSON.stringify({ pptx: pptFile, preview }, null, 2));
})();
