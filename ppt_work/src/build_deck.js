import {
  Presentation,
  PresentationFile,
  row,
  column,
  grid,
  layers,
  panel,
  text,
  image,
  shape,
  rule,
  fill,
  hug,
  fixed,
  wrap,
  grow,
  fr,
  auto,
} from "@oai/artifact-tool";
import { readFile, writeFile } from "node:fs/promises";

const W = 1920;
const H = 1080;

const c = {
  ink: "#13201D",
  muted: "#5C6F68",
  soft: "#EDF6F2",
  soft2: "#F8FBF9",
  line: "#CFE1D8",
  green: "#1F8A70",
  teal: "#2A9D8F",
  blue: "#2563EB",
  amber: "#F2B544",
  red: "#D9534F",
  white: "#FFFFFF",
  dark: "#0E1A17",
};

const titleStyle = { fontSize: 54, bold: true, color: c.ink, fontFace: "Microsoft YaHei" };
const subStyle = { fontSize: 25, color: c.muted, fontFace: "Microsoft YaHei" };
const bodyStyle = { fontSize: 27, color: c.ink, fontFace: "Microsoft YaHei" };
const smallStyle = { fontSize: 18, color: c.muted, fontFace: "Microsoft YaHei" };

const assetNames = [
  "screenshot-login.png",
  "screenshot-user-portal.png",
  "screenshot-assessment.png",
  "screenshot-chat.png",
  "project-system-architecture.png",
  "project-use-case-model.png",
  "project-system-function.png",
  "project-er-diagram-detailed.png",
  "project-auth-flow.png",
  "project-assessment-flow-detail.png",
  "project-appointment-flow.png",
  "project-test-case-table.png",
];

const assetData = Object.fromEntries(
  await Promise.all(
    assetNames.map(async (name) => {
      const bytes = await readFile(`scratch/assets/${name}`);
      return [name, `data:image/png;base64,${bytes.toString("base64")}`];
    }),
  ),
);

const asset = (name) => assetData[name];

function add(slide, child, background = c.soft2) {
  slide.compose(
    panel(
      { name: "slide-bg", width: fill, height: fill, fill: background },
      child,
    ),
    { frame: { left: 0, top: 0, width: W, height: H }, baseUnit: 8 },
  );
}

function titleBlock(title, subtitle) {
  return column(
    { name: "title-block", width: fill, height: hug, gap: 12 },
    [
      text(title, { name: "slide-title", width: fill, height: hug, style: titleStyle }),
      subtitle ? text(subtitle, { name: "slide-subtitle", width: wrap(1320), height: hug, style: subStyle }) : null,
    ].filter(Boolean),
  );
}

function bullet(textValue, accent = c.green) {
  return row(
    { name: "bullet-row", width: fill, height: hug, gap: 18, align: "start" },
    [
      shape({ name: "bullet-dot", geometry: "ellipse", width: fixed(16), height: fixed(16), fill: accent }),
      text(textValue, { name: "bullet-text", width: fill, height: hug, style: bodyStyle }),
    ],
  );
}

function note(label, value, color = c.green) {
  return column(
    { name: "note", width: fill, height: hug, gap: 10 },
    [
      text(label, { name: "note-label", width: fill, height: hug, style: { ...smallStyle, bold: true, color } }),
      text(value, { name: "note-value", width: fill, height: hug, style: { ...bodyStyle, fontSize: 25 } }),
    ],
  );
}

function framedImage(name, alt, fit = "contain") {
  return panel(
    { name: `frame-${name}`, width: fill, height: fill, fill: c.white, line: { color: c.line, width: 1 }, borderRadius: 20, padding: 18 },
    image({ name, dataUrl: asset(name), width: fill, height: fill, fit, alt }),
  );
}

function sectionLabel(value, color = c.green) {
  return text(value, {
    name: "section-label",
    width: hug,
    height: hug,
    style: { fontSize: 20, bold: true, color, fontFace: "Microsoft YaHei" },
  });
}

const presentation = Presentation.create({ slideSize: { width: W, height: H } });

// 1 Cover
{
  const slide = presentation.slides.add();
  add(
    slide,
    grid(
      {
        name: "cover-root",
        width: fill,
        height: fill,
        columns: [fr(0.95), fr(1.05)],
        columnGap: 64,
        padding: { x: 92, y: 72 },
      },
      [
        column(
          { name: "cover-copy", width: fill, height: fill, gap: 28, justify: "center" },
          [
            sectionLabel("本科毕业论文（设计）答辩", c.teal),
            text("基于 Spring Boot 和 Vue 的心理健康服务平台", {
              name: "cover-title",
              width: fill,
              height: hug,
              style: { fontSize: 68, bold: true, color: c.white, fontFace: "Microsoft YaHei" },
            }),
            text("设计与实现", {
              name: "cover-kicker",
              width: fill,
              height: hug,
              style: { fontSize: 46, bold: true, color: "#A7F3D0", fontFace: "Microsoft YaHei" },
            }),
            rule({ name: "cover-rule", width: fixed(260), stroke: c.teal, weight: 5 }),
            text("陈爽  3220421092  ·  计算机科学与技术223班\n指导教师：刘璇  ·  2026年5月", {
              name: "cover-meta",
              width: wrap(760),
              height: hug,
              style: { fontSize: 24, color: "#DCEFE8", fontFace: "Microsoft YaHei" },
            }),
          ],
        ),
        panel(
          { name: "cover-image-frame", width: fill, height: fill, fill: "#15251F", borderRadius: 28, padding: 16 },
          image({ name: "cover-ui", dataUrl: asset("screenshot-login.png"), width: fill, height: fill, fit: "cover", alt: "平台登录界面截图" }),
        ),
      ],
    ),
    c.dark,
  );
}

// 2 Background
{
  const slide = presentation.slides.add();
  add(
    slide,
    grid(
      { name: "root", width: fill, height: fill, columns: [fr(1)], rows: [auto, fr(1)], rowGap: 52, padding: { x: 92, y: 72 } },
      [
        titleBlock("研究背景与意义", "高校心理服务从线下登记走向线上协同，核心问题是效率、连续性与风险可解释。"),
        grid(
          { name: "body", width: fill, height: fill, columns: [fr(1.1), fr(0.9)], columnGap: 62 },
          [
            column(
              { name: "bullets", width: fill, height: fill, gap: 30, justify: "center" },
              [
                bullet("线下预约和人工记录容易受到时间、场地、人员数量限制。"),
                bullet("学生需要低门槛入口，完成测评、预约、阅读和沟通。"),
                bullet("咨询师和管理员需要统一数据视图，支持跟进和统计。"),
                bullet("测评结果应给出风险概率、等级和影响因素，而不是单一分数。"),
              ],
            ),
            framedImage("screenshot-user-portal.png", "用户端服务首页截图", "cover"),
          ],
        ),
      ],
    ),
  );
}

// 3 Goals and route
{
  const slide = presentation.slides.add();
  add(
    slide,
    grid(
      { name: "root", width: fill, height: fill, columns: [fr(1)], rows: [auto, fr(1)], rowGap: 44, padding: { x: 92, y: 72 } },
      [
        titleBlock("课题目标与技术路线", "以“前端视图层、接口交互层、后端服务层、数据持久层”为主线完成系统实现。"),
        grid(
          { name: "body", width: fill, height: fill, columns: [fr(0.78), fr(1.22)], columnGap: 52 },
          [
            column(
              { name: "notes", width: fill, height: fill, gap: 32, justify: "center" },
              [
                note("目标一", "构建普通用户、咨询师、管理员三类角色的协同平台。"),
                note("目标二", "实现测评、预约、聊天、文章、通知与后台管理闭环。", c.blue),
                note("目标三", "预留 CatBoost 风险筛查路径，并提供 Java 规则回退。", c.amber),
              ],
            ),
            framedImage("project-system-architecture.png", "系统架构图"),
          ],
        ),
      ],
    ),
  );
}

// 4 Requirements
{
  const slide = presentation.slides.add();
  add(
    slide,
    grid(
      { name: "root", width: fill, height: fill, columns: [fr(1)], rows: [auto, fr(1)], rowGap: 38, padding: { x: 92, y: 72 } },
      [
        titleBlock("需求分析：三类角色，一个服务闭环", "平台围绕学生自助服务、咨询师事务处理、管理员运营监管展开。"),
        grid(
          { name: "body", width: fill, height: fill, columns: [fr(1.1), fr(0.9)], columnGap: 52 },
          [
            framedImage("project-use-case-model.png", "系统用例模型图"),
            column(
              { name: "role-list", width: fill, height: fill, gap: 30, justify: "center" },
              [
                note("普通用户", "注册登录、心理测评、预约咨询、在线聊天、查看文章公告。", c.green),
                note("心理咨询师", "维护资料、处理预约、查看沟通对象、开展在线沟通。", c.blue),
                note("管理员", "管理用户、咨询师、文章通知，查看数据看板和风险记录。", c.red),
              ],
            ),
          ],
        ),
      ],
    ),
  );
}

// 5 Architecture
{
  const slide = presentation.slides.add();
  add(
    slide,
    grid(
      { name: "root", width: fill, height: fill, columns: [fr(1)], rows: [auto, fr(1)], rowGap: 36, padding: { x: 92, y: 72 } },
      [
        titleBlock("系统总体架构", "前后端分离，REST API 负责业务操作，WebSocket 负责聊天实时推送。"),
        grid(
          { name: "body", width: fill, height: fill, columns: [fr(1.24), fr(0.76)], columnGap: 46 },
          [
            framedImage("project-system-architecture.png", "系统总体架构图"),
            column(
              { name: "architecture-points", width: fill, height: fill, gap: 26, justify: "center" },
              [
                bullet("Vue 3 单页应用承载门户、表单、列表和图表。", c.teal),
                bullet("Spring Boot 提供认证、权限、业务接口和异常处理。", c.teal),
                bullet("MyBatis-Plus 负责实体映射与条件查询。", c.teal),
                bullet("MySQL 保存核心业务数据，Redis 预留缓存能力。", c.teal),
              ],
            ),
          ],
        ),
      ],
    ),
  );
}

// 6 Function structure
{
  const slide = presentation.slides.add();
  add(
    slide,
    grid(
      { name: "root", width: fill, height: fill, columns: [fr(1)], rows: [auto, fr(1)], rowGap: 34, padding: { x: 92, y: 72 } },
      [
        titleBlock("功能结构设计", "功能按角色入口组织，但底层数据和服务形成统一业务流。"),
        framedImage("project-system-function.png", "系统功能结构图"),
      ],
    ),
  );
}

// 7 Database
{
  const slide = presentation.slides.add();
  add(
    slide,
    grid(
      { name: "root", width: fill, height: fill, columns: [fr(1)], rows: [auto, fr(1)], rowGap: 34, padding: { x: 92, y: 72 } },
      [
        titleBlock("数据库设计", "以用户表为身份中心，连接咨询师、预约、测评、聊天和管理内容。"),
        grid(
          { name: "body", width: fill, height: fill, columns: [fr(1.18), fr(0.82)], columnGap: 44 },
          [
            framedImage("project-er-diagram-detailed.png", "系统 ER 图"),
            column(
              { name: "db-points", width: fill, height: fill, gap: 28, justify: "center" },
              [
                note("核心实体", "sys_user、counselor_profile、appointment、assessment_record、chat_message。"),
                note("关系设计", "用户身份、咨询关系、测评记录和聊天记录通过用户编号关联。", c.blue),
                note("可扩展性", "文章、通知、日志表支撑内容运营和审计追踪。", c.amber),
              ],
            ),
          ],
        ),
      ],
    ),
  );
}

// 8 Auth and permission
{
  const slide = presentation.slides.add();
  add(
    slide,
    grid(
      { name: "root", width: fill, height: fill, columns: [fr(1)], rows: [auto, fr(1)], rowGap: 34, padding: { x: 92, y: 72 } },
      [
        titleBlock("核心实现一：登录认证与角色权限", "JWT 认证结合前端路由守卫和后端接口校验，保护敏感业务数据。"),
        grid(
          { name: "body", width: fill, height: fill, columns: [fr(1.05), fr(0.95)], columnGap: 46 },
          [
            column(
              { name: "auth-points", width: fill, height: fill, gap: 32, justify: "center" },
              [
                bullet("登录成功后，后端生成包含用户编号和角色的 token。", c.blue),
                bullet("前端 Pinia 和 localStorage 保存登录态，请求拦截器自动携带 token。", c.blue),
                bullet("路由 meta 控制角色访问；后端服务层继续校验数据归属。", c.blue),
                bullet("401 响应会清理登录信息并跳转回登录页。", c.blue),
              ],
            ),
            framedImage("project-auth-flow.png", "登录认证流程图"),
          ],
        ),
      ],
    ),
  );
}

// 9 Assessment
{
  const slide = presentation.slides.add();
  add(
    slide,
    grid(
      { name: "root", width: fill, height: fill, columns: [fr(1)], rows: [auto, fr(1)], rowGap: 34, padding: { x: 92, y: 72 } },
      [
        titleBlock("核心实现二：心理测评与风险分析", "测评模块返回风险概率、风险等级、模型名称和主要影响因素。"),
        grid(
          { name: "body", width: fill, height: fill, columns: [fr(0.94), fr(1.06)], columnGap: 42 },
          [
            framedImage("screenshot-assessment.png", "心理测评页面截图", "cover"),
            column(
              { name: "assessment-right", width: fill, height: fill, gap: 26 },
              [
                framedImage("project-assessment-flow-detail.png", "心理测评流程图"),
                text("实现要点：前端根据 question_json 渲染表单，提交 answer_json；后端优先调用 CatBoost 推理，失败时使用 Java 规则回退，保证测评流程不断档。", {
                  name: "assessment-caption",
                  width: fill,
                  height: hug,
                  style: { ...bodyStyle, fontSize: 24, color: c.muted },
                }),
              ],
            ),
          ],
        ),
      ],
    ),
  );
}

// 10 Appointment and chat
{
  const slide = presentation.slides.add();
  add(
    slide,
    grid(
      { name: "root", width: fill, height: fill, columns: [fr(1)], rows: [auto, fr(1)], rowGap: 34, padding: { x: 92, y: 72 } },
      [
        titleBlock("核心实现三：预约咨询与在线聊天", "预约确认后开放沟通入口，聊天消息保存到数据库并通过 WebSocket 推送。"),
        grid(
          { name: "body", width: fill, height: fill, columns: [fr(1), fr(1)], columnGap: 38 },
          [
            column(
              { name: "left", width: fill, height: fill, gap: 22 },
              [
                framedImage("project-appointment-flow.png", "预约咨询流程图"),
                text("预约流程覆盖提交、查询、取消、改期、确认、拒绝等状态变化。", { name: "appointment-caption", width: fill, height: hug, style: { ...smallStyle, fontSize: 20 } }),
              ],
            ),
            column(
              { name: "right", width: fill, height: fill, gap: 22 },
              [
                framedImage("screenshot-chat.png", "在线聊天界面截图", "cover"),
                text("REST API 负责历史记录与保存，WebSocket 负责新消息实时推送。", { name: "chat-caption", width: fill, height: hug, style: { ...smallStyle, fontSize: 20 } }),
              ],
            ),
          ],
        ),
      ],
    ),
  );
}

// 11 Testing
{
  const slide = presentation.slides.add();
  add(
    slide,
    grid(
      { name: "root", width: fill, height: fill, columns: [fr(1)], rows: [auto, fr(1)], rowGap: 36, padding: { x: 92, y: 72 } },
      [
        titleBlock("系统测试", "围绕功能流程、接口返回、异常场景和页面展示进行验证。"),
        grid(
          { name: "body", width: fill, height: fill, columns: [fr(0.82), fr(1.18)], columnGap: 48 },
          [
            column(
              { name: "testing-points", width: fill, height: fill, gap: 30, justify: "center" },
              [
                note("功能测试", "登录、测评、预约、聊天、后台管理流程均按预期完成。", c.green),
                note("接口测试", "校验参数、鉴权、状态变化和统一响应结构。", c.blue),
                note("异常测试", "未登录、越权、空表单、无效数据等场景有提示或拦截。", c.red),
              ],
            ),
            framedImage("project-test-case-table.png", "系统测试用例表"),
          ],
        ),
      ],
    ),
  );
}

// 12 Summary
{
  const slide = presentation.slides.add();
  add(
    slide,
    grid(
      { name: "root", width: fill, height: fill, columns: [fr(1)], rows: [auto, fr(1), auto], rowGap: 44, padding: { x: 92, y: 72 } },
      [
        titleBlock("总结与展望", "平台完成了高校心理服务的核心线上化流程，也为后续智能化扩展留下接口。"),
        grid(
          { name: "summary-grid", width: fill, height: fill, columns: [fr(1), fr(1)], columnGap: 64 },
          [
            column(
              { name: "done", width: fill, height: fill, gap: 26, justify: "center" },
              [
                sectionLabel("已完成"),
                bullet("三类角色门户与权限控制。"),
                bullet("心理测评、预约咨询、在线聊天、文章通知、后台管理。"),
                bullet("数据看板与风险记录展示。"),
                bullet("CatBoost 推理路径与规则回退机制。"),
              ],
            ),
            column(
              { name: "future", width: fill, height: fill, gap: 26, justify: "center" },
              [
                sectionLabel("可扩展方向", c.amber),
                bullet("完善 WebSocket 鉴权和会话管理。", c.amber),
                bullet("接入对象存储、消息队列和预约提醒。", c.amber),
                bullet("引入更多真实测评数据和 SHAP 个体解释。", c.amber),
                bullet("补充单元测试、压测和部署监控。", c.amber),
              ],
            ),
          ],
        ),
        text("谢谢各位老师，请批评指正。", {
          name: "thanks",
          width: fill,
          height: hug,
          style: { fontSize: 34, bold: true, color: c.green, fontFace: "Microsoft YaHei" },
        }),
      ],
    ),
  );
}

const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save("output/3220421092_陈爽_毕业设计答辩.pptx");

for (let i = 0; i < presentation.slides.count; i += 1) {
  const slide = presentation.slides.getItem(i);
  const png = await presentation.export({ format: "png", slide });
  await writeFile(
    `scratch/preview-slide-${String(i + 1).padStart(2, "0")}.png`,
    Buffer.from(await png.arrayBuffer()),
  );
}

const report = await presentation.inspect({ includeTextLayout: true });
await writeFile("scratch/layout-report.json", JSON.stringify(report, null, 2), "utf8");
