from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "thesis-assets"


FONT_PATH = "C:/Windows/Fonts/msyh.ttc"
TITLE = ImageFont.truetype(FONT_PATH, 34)
H2 = ImageFont.truetype(FONT_PATH, 24)
TEXT = ImageFont.truetype(FONT_PATH, 20)
SMALL = ImageFont.truetype(FONT_PATH, 17)

INK = "#000000"
LINE = "#000000"
BG = "#FFFFFF"
GREEN = "#FFFFFF"
BLUE = "#F2F2F2"
YELLOW = "#E6E6E6"
PEACH = "#F7F7F7"
MINT = "#EFEFEF"
GRAY = "#FFFFFF"


def wrap(text: str, count: int) -> list[str]:
    lines: list[str] = []
    for raw in text.split("\n"):
        current = ""
        width = 0
        for ch in raw:
            step = 1 if ord(ch) < 128 else 2
            if width + step > count and current:
                lines.append(current)
                current = ch
                width = step
            else:
                current += ch
                width += step
        if current:
            lines.append(current)
    return lines or [""]


def box(draw: ImageDraw.ImageDraw, xy, text: str, fill=GREEN, font=TEXT, max_width=18):
    draw.rectangle(xy, fill=fill, outline=LINE, width=3)
    lines = wrap(text, max_width)
    total = len(lines) * 28
    y = xy[1] + max(12, (xy[3] - xy[1] - total) // 2)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = xy[0] + (xy[2] - xy[0] - (bbox[2] - bbox[0])) / 2
        draw.text((x, y), line, font=font, fill=INK)
        y += 28


def arrow(draw: ImageDraw.ImageDraw, start, end, color=LINE):
    draw.line((*start, *end), fill=color, width=4)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    if abs(dx) >= abs(dy):
        points = (
            [(end[0], end[1]), (end[0] - 18, end[1] - 10), (end[0] - 18, end[1] + 10)]
            if dx >= 0
            else [(end[0], end[1]), (end[0] + 18, end[1] - 10), (end[0] + 18, end[1] + 10)]
        )
    else:
        points = (
            [(end[0], end[1]), (end[0] - 10, end[1] - 18), (end[0] + 10, end[1] - 18)]
            if dy >= 0
            else [(end[0], end[1]), (end[0] - 10, end[1] + 18), (end[0] + 10, end[1] + 18)]
        )
    draw.polygon(points, fill=color)


def title(draw: ImageDraw.ImageDraw, text: str):
    draw.text((60, 36), text, font=TITLE, fill=INK)


def save(img: Image.Image, name: str):
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / name)


def note(draw: ImageDraw.ImageDraw, xy, text: str, max_width=42):
    lines = wrap(text, max_width)
    y = xy[1]
    for line in lines:
        draw.text((xy[0], y), line, font=SMALL, fill=INK)
        y += 25


def system_structure():
    img = Image.new("RGB", (1600, 1000), BG)
    draw = ImageDraw.Draw(img)
    title(draw, "心理健康服务平台系统结构图")

    box(draw, (640, 110, 960, 210), "心理健康服务平台", YELLOW, H2, 18)
    modules = [
        ((90, 320, 390, 430), "用户服务子系统\n注册登录、个人资料、文章阅读", GREEN),
        ((470, 320, 770, 430), "心理测评子系统\n量表作答、风险分析、历史记录", BLUE),
        ((850, 320, 1150, 430), "咨询预约子系统\n咨询师浏览、预约申请、状态流转", PEACH),
        ((1230, 320, 1530, 430), "在线沟通子系统\n联系人、消息记录、实时推送", MINT),
        ((270, 620, 570, 730), "咨询师工作台\n预约处理、资料维护、会话沟通", YELLOW),
        ((650, 620, 950, 730), "管理员后台\n用户、咨询师、文章、通知管理", GREEN),
        ((1030, 620, 1330, 730), "数据看板子系统\n统计概览、风险分布、运营指标", BLUE),
    ]
    for xy, text, fill in modules:
        box(draw, xy, text, fill, TEXT, 24)
        arrow(draw, (800, 210), ((xy[0] + xy[2]) // 2, xy[1]))

    draw.text((120, 845), "说明：系统结构按业务职责划分，各子系统通过统一后端接口和共享数据库协同工作。", font=H2, fill=INK)
    save(img, "project-system-structure.png")


def system_function():
    img = Image.new("RGB", (1700, 1100), BG)
    draw = ImageDraw.Draw(img)
    title(draw, "心理健康服务平台系统功能图")
    columns = [
        ("普通用户", 90, GREEN, ["账号注册登录", "个人资料维护", "心理文章阅读", "心理测评提交", "测评结果查看", "咨询师浏览", "预约咨询", "在线聊天"]),
        ("心理咨询师", 600, BLUE, ["咨询师资料维护", "预约申请处理", "查看预约记录", "与用户在线沟通", "查看历史消息", "阅读平台文章"]),
        ("管理员", 1110, YELLOW, ["用户管理", "咨询师管理", "文章发布管理", "通知发布管理", "测评记录监控", "平台数据看板", "风险分布统计"]),
    ]
    for role, x, fill, items in columns:
        box(draw, (x, 120, x + 390, 210), role, fill, H2, 12)
        y = 270
        for item in items:
            box(draw, (x, y, x + 390, y + 62), item, GRAY, TEXT, 18)
            arrow(draw, (x + 195, 210), (x + 195, y))
            y += 90
    draw.text((100, 1015), "说明：功能图从角色视角展开，体现普通用户、咨询师和管理员在同一平台中的功能边界。", font=H2, fill=INK)
    save(img, "project-system-function.png")


def data_flow():
    img = Image.new("RGB", (1700, 1050), BG)
    draw = ImageDraw.Draw(img)
    title(draw, "心理健康服务平台数据流图")
    box(draw, (80, 160, 350, 260), "普通用户", GREEN, H2, 12)
    box(draw, (80, 430, 350, 530), "心理咨询师", BLUE, H2, 12)
    box(draw, (80, 700, 350, 800), "管理员", YELLOW, H2, 12)
    box(draw, (620, 170, 980, 270), "前端页面\nVue / Router / Pinia", BLUE, TEXT, 22)
    box(draw, (620, 440, 980, 540), "后端业务服务\nController / Service", GREEN, TEXT, 24)
    box(draw, (1230, 150, 1580, 250), "认证与权限\nJWT / Security", PEACH, TEXT, 20)
    box(draw, (1230, 385, 1580, 485), "业务数据库\n用户/预约/测评/聊天/文章", YELLOW, TEXT, 25)
    box(draw, (1230, 620, 1580, 720), "机器学习推理\nCatBoost / Java 回退", MINT, TEXT, 22)
    box(draw, (1230, 810, 1580, 910), "WebSocket 通道\n实时消息推送", BLUE, TEXT, 22)

    for y in [210, 480, 750]:
        arrow(draw, (350, y), (620, 220 if y == 210 else 490))
    arrow(draw, (800, 270), (800, 440))
    arrow(draw, (980, 210), (1230, 200))
    arrow(draw, (980, 490), (1230, 435))
    arrow(draw, (980, 490), (1230, 670))
    arrow(draw, (980, 490), (1230, 860))
    arrow(draw, (1230, 435), (980, 490))
    arrow(draw, (1230, 670), (980, 490))
    arrow(draw, (1230, 860), (980, 490))

    labels = [
        (390, 180, "登录、测评答案、预约申请、聊天内容"),
        (390, 450, "预约处理、资料维护、消息回复"),
        (390, 720, "管理操作、通知、文章、监控查询"),
        (1020, 375, "业务数据持久化与查询"),
        (1020, 610, "测评特征与风险结果"),
        (1020, 805, "实时消息与在线会话"),
    ]
    for x, y, text in labels:
        draw.text((x, y), text, font=SMALL, fill=INK)
    save(img, "project-data-flow.png")


def system_architecture():
    img = Image.new("RGB", (1600, 1000), "#F7F4EC")
    draw = ImageDraw.Draw(img)
    title(draw, "心理健康服务平台系统架构图")
    layers = [
        ("用户访问层\n浏览器、用户端、咨询师端、管理员端", GREEN),
        ("前端表现层\nVue 3、TypeScript、Element Plus、ECharts", BLUE),
        ("接口通信层\nAxios REST API、JWT、WebSocket", YELLOW),
        ("后端应用层\nSpring Boot、Spring Security、Controller、Service", MINT),
        ("数据访问层\nMyBatis-Plus、Mapper、实体对象", PEACH),
        ("数据与模型层\nMySQL、Redis、CatBoost 模型、文件上传目录", GREEN),
    ]
    y = 110
    for text, fill in layers:
        box(draw, (170, y, 1430, y + 100), text, fill, H2, 44)
        if y < 760:
            arrow(draw, (800, y + 100), (800, y + 140))
        y += 135
    save(img, "project-system-architecture.png")


def system_flow():
    img = Image.new("RGB", (1700, 1050), BG)
    draw = ImageDraw.Draw(img)
    title(draw, "心理健康服务平台系统流程图")
    nodes = [
        ((80, 150, 330, 240), "进入平台", GREEN),
        ((450, 150, 700, 240), "登录/注册", BLUE),
        ((820, 150, 1070, 240), "角色识别", YELLOW),
        ((1190, 60, 1500, 150), "用户首页", GREEN),
        ((1190, 205, 1500, 295), "咨询师首页", BLUE),
        ((1190, 350, 1500, 440), "管理员首页", YELLOW),
        ((170, 590, 480, 690), "测评/预约/文章/聊天", GREEN),
        ((700, 590, 1010, 690), "处理预约/维护资料/沟通", BLUE),
        ((1230, 590, 1540, 690), "管理用户/内容/通知/看板", YELLOW),
        ((700, 825, 1010, 925), "数据保存与结果反馈", PEACH),
    ]
    for xy, text, fill in nodes:
        box(draw, xy, text, fill, H2, 18)
    for start, end in [
        ((330, 195), (450, 195)),
        ((700, 195), (820, 195)),
        ((1070, 195), (1190, 105)),
        ((1070, 195), (1190, 250)),
        ((1070, 195), (1190, 395)),
        ((1345, 150), (325, 590)),
        ((1345, 295), (855, 590)),
        ((1345, 440), (1385, 590)),
        ((325, 690), (700, 875)),
        ((855, 690), (855, 825)),
        ((1385, 690), (1010, 875)),
    ]:
        arrow(draw, start, end)
    save(img, "project-system-flow.png")


def use_case_model():
    img = Image.new("RGB", (1700, 1100), BG)
    draw = ImageDraw.Draw(img)
    title(draw, "心理健康服务平台用例模型图")
    box(draw, (60, 220, 270, 320), "普通用户", GREEN, H2, 12)
    box(draw, (60, 520, 270, 620), "心理咨询师", BLUE, H2, 12)
    box(draw, (60, 820, 270, 920), "管理员", YELLOW, H2, 12)
    draw.rounded_rectangle((380, 130, 1620, 980), radius=26, outline=LINE, width=4, fill="#FBFDFC")
    draw.text((950, 155), "系统边界", font=H2, fill=INK)

    use_cases = [
        ((470, 220, 760, 285), "注册/登录"),
        ((470, 325, 760, 390), "维护个人资料"),
        ((470, 430, 760, 495), "完成心理测评"),
        ((470, 535, 760, 600), "预约咨询师"),
        ((470, 640, 760, 705), "在线聊天"),
        ((830, 270, 1120, 335), "处理预约"),
        ((830, 430, 1120, 495), "维护咨询师资料"),
        ((830, 590, 1120, 655), "查看历史消息"),
        ((1190, 220, 1500, 285), "管理用户与咨询师"),
        ((1190, 340, 1500, 405), "管理文章与通知"),
        ((1190, 460, 1500, 525), "查看数据看板"),
        ((1190, 580, 1500, 645), "监控测评记录"),
    ]
    for xy, text in use_cases:
        draw.ellipse(xy, fill=GRAY, outline=LINE, width=3)
        bbox = draw.textbbox((0, 0), text, font=TEXT)
        draw.text((xy[0] + (xy[2] - xy[0] - bbox[2]) / 2, xy[1] + 20), text, font=TEXT, fill=INK)

    for end in [(470, 252), (470, 357), (470, 462), (470, 567), (470, 672)]:
        arrow(draw, (270, 270), end)
    for end in [(830, 302), (830, 462), (830, 622), (470, 672)]:
        arrow(draw, (270, 570), end)
    for end in [(1190, 252), (1190, 372), (1190, 492), (1190, 612), (470, 252)]:
        arrow(draw, (270, 870), end)
    save(img, "project-use-case-model.png")


def auth_flow():
    img = Image.new("RGB", (1700, 1050), BG)
    draw = ImageDraw.Draw(img)
    title(draw, "登录认证与权限控制功能流程图")
    nodes = [
        ((80, 140, 360, 230), "输入账号密码"),
        ((500, 140, 780, 230), "前端表单校验"),
        ((920, 140, 1200, 230), "调用登录接口"),
        ((1340, 140, 1620, 230), "后端校验用户"),
        ((1340, 360, 1620, 450), "生成 JWT\n返回用户角色"),
        ((920, 360, 1200, 450), "保存 token\nPinia/localStorage"),
        ((500, 360, 780, 450), "路由守卫判断\nallowedRoles"),
        ((80, 360, 360, 450), "跳转角色首页"),
        ((500, 640, 780, 730), "请求业务接口\n携带 Authorization"),
        ((920, 640, 1200, 730), "JWT 过滤器解析"),
        ((1340, 640, 1620, 730), "服务层二次校验\n返回业务数据"),
    ]
    for xy, text in nodes:
        box(draw, xy, text, BLUE if "校验" in text or "判断" in text else GREEN, H2, 20)
    for start, end in [
        ((360, 185), (500, 185)), ((780, 185), (920, 185)), ((1200, 185), (1340, 185)),
        ((1480, 230), (1480, 360)), ((1340, 405), (1200, 405)), ((920, 405), (780, 405)),
        ((500, 405), (360, 405)), ((640, 450), (640, 640)), ((780, 685), (920, 685)),
        ((1200, 685), (1340, 685)),
    ]:
        arrow(draw, start, end)
    note(draw, (90, 875), "说明：认证流程采用前端状态保存与后端无状态校验相结合。前端路由守卫用于提升页面访问体验，后端 JWT 过滤器和服务层权限判断用于保证接口安全，避免仅依赖前端隐藏菜单造成越权访问。", 82)
    save(img, "project-auth-flow.png")


def assessment_detail_flow():
    img = Image.new("RGB", (1700, 1100), BG)
    draw = ImageDraw.Draw(img)
    title(draw, "心理测评功能流程图")
    nodes = [
        ((80, 130, 360, 220), "用户进入测评页"),
        ((500, 130, 780, 220), "获取量表列表"),
        ((920, 130, 1200, 220), "读取 questionJson"),
        ((1340, 130, 1620, 220), "动态渲染题目"),
        ((1340, 340, 1620, 430), "提交答案 JSON"),
        ((920, 340, 1200, 430), "解析特征\n计算基础得分"),
        ((500, 340, 780, 430), "CatBoost 推理\n或 Java 回退"),
        ((80, 340, 360, 430), "生成风险概率\n等级和影响因素"),
        ((80, 565, 360, 655), "保存测评记录"),
        ((500, 565, 780, 655), "用户查看结果"),
        ((920, 565, 1200, 655), "管理员监控记录"),
        ((1340, 565, 1620, 655), "后续人工复核\n线下干预依据"),
    ]
    for xy, text in nodes:
        box(draw, xy, text, GREEN, H2, 19)
    for start, end in [
        ((360, 175), (500, 175)), ((780, 175), (920, 175)), ((1200, 175), (1340, 175)),
        ((1480, 220), (1480, 340)), ((1340, 385), (1200, 385)), ((920, 385), (780, 385)),
        ((500, 385), (360, 385)), ((220, 430), (220, 565)), ((360, 610), (500, 610)),
        ((360, 610), (920, 610)), ((1200, 610), (1340, 610)),
    ]:
        arrow(draw, start, end)
    note(draw, (90, 840), "说明：测评模块的数据处理重点在于量表配置、答案结构化、风险计算和结果解释。系统将题目配置保存为 JSON，前端根据配置动态生成题目；后端提交后解析答案，优先调用机器学习模型，模型不可用时使用 Java 回退逻辑，最终保存风险概率、风险等级、分析文本和主要影响因素。", 82)
    save(img, "project-assessment-flow-detail.png")


def appointment_flow():
    img = Image.new("RGB", (1700, 1050), BG)
    draw = ImageDraw.Draw(img)
    title(draw, "预约咨询功能流程图")
    nodes = [
        ((80, 130, 360, 220), "用户浏览咨询师"),
        ((500, 130, 780, 220), "查看擅长方向\n价格和状态"),
        ((920, 130, 1200, 220), "填写预约时间\n形式和问题描述"),
        ((1340, 130, 1620, 220), "提交预约申请"),
        ((1340, 350, 1620, 440), "预约状态\n待确认"),
        ((920, 350, 1200, 440), "咨询师处理"),
        ((500, 300, 780, 390), "同意预约\n状态已确认"),
        ((500, 460, 780, 550), "拒绝预约\n状态已拒绝"),
        ((80, 300, 360, 390), "开放聊天入口"),
        ((80, 460, 360, 550), "用户重新选择\n或取消"),
        ((920, 650, 1200, 740), "预约记录留存\n支持后台统计"),
    ]
    for xy, text in nodes:
        box(draw, xy, text, BLUE, H2, 18)
    for start, end in [
        ((360, 175), (500, 175)), ((780, 175), (920, 175)), ((1200, 175), (1340, 175)),
        ((1480, 220), (1480, 350)), ((1340, 395), (1200, 395)),
        ((920, 380), (780, 345)), ((920, 410), (780, 505)), ((500, 345), (360, 345)),
        ((500, 505), (360, 505)), ((1060, 440), (1060, 650)),
    ]:
        arrow(draw, start, end)
    note(draw, (90, 865), "说明：预约咨询模块以状态流转为核心。用户提交预约后，系统保存为待确认状态；咨询师根据个人安排同意或拒绝。同意后用户与咨询师之间形成可沟通关系，系统开放聊天入口；拒绝或取消后，记录仍然保留，用于用户查看和管理员统计。", 82)
    save(img, "project-appointment-flow.png")


def chat_flow():
    img = Image.new("RGB", (1700, 1050), BG)
    draw = ImageDraw.Draw(img)
    title(draw, "在线聊天功能流程图")
    nodes = [
        ((80, 130, 360, 220), "用户/咨询师\n进入聊天页"),
        ((500, 130, 780, 220), "加载联系人列表"),
        ((920, 130, 1200, 220), "选择联系人\n加载历史消息"),
        ((1340, 130, 1620, 220), "建立 WebSocket\n携带 token"),
        ((1340, 350, 1620, 440), "发送消息"),
        ((920, 350, 1200, 440), "后端校验关系\n保存消息"),
        ((500, 350, 780, 440), "数据库持久化"),
        ((80, 350, 360, 440), "推送接收方\n刷新会话"),
        ((500, 610, 780, 700), "连接异常时\n保留 REST 发送"),
        ((920, 610, 1200, 700), "历史记录可追溯"),
    ]
    for xy, text in nodes:
        box(draw, xy, text, GREEN, H2, 20)
    for start, end in [
        ((360, 175), (500, 175)), ((780, 175), (920, 175)), ((1200, 175), (1340, 175)),
        ((1480, 220), (1480, 350)), ((1340, 395), (1200, 395)), ((920, 395), (780, 395)),
        ((500, 395), (360, 395)), ((640, 440), (640, 610)), ((1060, 440), (1060, 610)),
    ]:
        arrow(draw, start, end)
    note(draw, (90, 845), "说明：聊天模块同时使用 REST 接口和 WebSocket。REST 接口负责消息保存与历史记录查询，WebSocket 负责在线状态下的实时推送。这样即使实时连接短暂异常，消息仍可通过普通接口保存，保证业务连续性和记录可追溯。", 82)
    save(img, "project-chat-flow.png")


def counselor_workbench_flow():
    img = Image.new("RGB", (1700, 1050), BG)
    draw = ImageDraw.Draw(img)
    title(draw, "咨询师端功能流程图")
    nodes = [
        ((80, 150, 360, 240), "咨询师登录"),
        ((500, 150, 780, 240), "进入咨询师首页"),
        ((920, 80, 1200, 170), "维护个人资料"),
        ((920, 230, 1200, 320), "查看预约列表"),
        ((920, 380, 1200, 470), "处理待确认预约"),
        ((1340, 230, 1620, 320), "同意/拒绝\n更新状态"),
        ((1340, 440, 1620, 530), "进入会话\n在线沟通"),
        ((920, 650, 1200, 740), "查看历史消息"),
        ((500, 650, 780, 740), "资料和处理结果\n同步用户端"),
    ]
    for xy, text in nodes:
        box(draw, xy, text, BLUE, H2, 18)
    for start, end in [
        ((360, 195), (500, 195)), ((780, 195), (920, 125)), ((780, 195), (920, 275)),
        ((780, 195), (920, 425)), ((1200, 275), (1340, 275)), ((1200, 425), (1340, 485)),
        ((1340, 485), (1200, 695)), ((920, 695), (780, 695)),
    ]:
        arrow(draw, start, end)
    note(draw, (90, 860), "说明：咨询师端围绕服务处理展开，重点包括资料维护、预约处理和在线沟通。咨询师资料会影响用户选择，预约处理结果会影响聊天准入，历史消息则为后续沟通提供上下文。", 82)
    save(img, "project-counselor-workbench-flow.png")


def admin_backend_flow():
    img = Image.new("RGB", (1700, 1100), BG)
    draw = ImageDraw.Draw(img)
    title(draw, "管理员端功能流程图")
    nodes = [
        ((80, 140, 360, 230), "管理员登录"),
        ((500, 140, 780, 230), "进入后台首页"),
        ((920, 70, 1200, 160), "用户管理"),
        ((920, 210, 1200, 300), "咨询师管理"),
        ((920, 350, 1200, 440), "文章管理"),
        ((920, 490, 1200, 580), "通知管理"),
        ((920, 630, 1200, 720), "测评记录监控"),
        ((920, 770, 1200, 860), "数据看板统计"),
        ((1340, 350, 1620, 440), "写入/更新\n业务数据"),
        ((1340, 630, 1620, 720), "风险分布\n运营指标"),
    ]
    for xy, text in nodes:
        box(draw, xy, text, YELLOW, H2, 18)
    for end_y in [115, 255, 395, 535, 675, 815]:
        arrow(draw, (780, 185), (920, end_y))
    arrow(draw, (360, 185), (500, 185))
    for y in [115, 255, 395, 535]:
        arrow(draw, (1200, y), (1340, 395))
    for y in [675, 815]:
        arrow(draw, (1200, y), (1340, 675))
    note(draw, (90, 940), "说明：管理员端承担平台治理职责，包括用户与咨询师数据维护、文章和通知内容运营、测评记录监控以及看板统计。该模块权限较高，论文中应强调后端二次校验、操作日志和敏感数据治理的必要性。", 82)
    save(img, "project-admin-backend-flow.png")


def er_diagram_detailed():
    img = Image.new("RGB", (1800, 1250), BG)
    draw = ImageDraw.Draw(img)
    title(draw, "心理健康服务平台数据库 E-R 图")
    entities = {
        "sys_user\n用户账号\nid PK\nusername\npassword\nrole\nstatus": (90, 470, 390, 680),
        "counselor_profile\n咨询师资料\nid PK\nuser_id FK\ntitle\nspecialties\nprice_per_hour": (560, 120, 900, 350),
        "appointment\n预约记录\nid PK\nuser_id FK\ncounselor_id FK\nappointment_time\nstatus": (1180, 120, 1520, 350),
        "assessment_scale\n测评量表\nid PK\nname\ncode\nquestion_json\nrule_json": (560, 470, 900, 700),
        "assessment_record\n测评记录\nid PK\nuser_id FK\nscale_id FK\nscore\nresult_level": (1180, 470, 1520, 700),
        "chat_message\n聊天消息\nid PK\nsender_id FK\nreceiver_id FK\ncontent\nreview_status": (1180, 820, 1520, 1050),
        "article\n心理文章\nid PK\ntitle\ncategory\ncontent\nstatus": (90, 820, 390, 1030),
        "notification\n通知信息\nid PK\ntarget_user_id\ntarget_role\ntitle\ncreated_by": (560, 820, 900, 1050),
        "counselor_review\n咨询师评价\nid PK\ncounselor_id FK\nuser_id FK\nrating\ncontent": (1450, 470, 1760, 700),
        "operation_log\n操作日志\nid PK\nuser_id FK\nmodule\naction\nip": (1450, 820, 1760, 1050),
    }
    def relation(points, label, label_at):
        draw.line(points, fill=LINE, width=4)
        x, y = label_at
        draw.rectangle((x - 48, y - 18, x + 88, y + 18), fill=BG, outline=LINE, width=1)
        draw.text((x - 38, y - 13), label, font=SMALL, fill=INK)

    relation([(390, 505), (475, 505), (475, 235), (560, 235)], "1:1", (470, 235))
    relation([(900, 235), (1180, 235)], "1:N", (1030, 235))
    relation([(390, 555), (1040, 555), (1040, 180), (1180, 180)], "1:N", (970, 180))
    relation([(390, 600), (560, 600)], "1:N", (470, 600))
    relation([(900, 585), (1180, 585)], "1:N", (1030, 585))
    relation([(390, 650), (1040, 650), (1040, 935), (1180, 935)], "1:N", (985, 935))
    relation([(390, 640), (490, 640), (490, 935), (560, 935)], "1:N", (470, 935))
    relation([(390, 880), (470, 880), (470, 660), (390, 660)], "作者", (465, 835))
    relation([(900, 235), (980, 235), (980, 585), (1450, 585)], "1:N", (1030, 585))
    relation([(390, 670), (1320, 670), (1320, 935), (1450, 935)], "1:N", (1280, 935))
    for text, xy in entities.items():
        box(draw, xy, text, GREEN, SMALL, 24)
    note(draw, (70, 1145), "说明：用户表是身份体系中心表；咨询师资料、预约、测评记录、聊天消息、通知、评价和操作日志均通过用户编号或咨询师资料编号建立关联。", 96)
    save(img, "project-er-diagram-detailed.png")


def database_table_design():
    img = Image.new("RGB", (1900, 1400), BG)
    draw = ImageDraw.Draw(img)
    title(draw, "核心数据表设计表")
    headers = ["表名", "核心字段", "作用说明"]
    rows = [
        ["sys_user", "id, username, password, email, phone, role, nickname, avatar, gender, age, status", "保存平台用户账号、角色和基础资料，是登录认证和权限控制的基础表。"],
        ["counselor_profile", "id, user_id, title, specialties, years_of_experience, introduction, price_per_hour, online_status, rating", "保存咨询师扩展资料，与 sys_user 形成一对一关系，用于用户选择咨询师和后台管理。"],
        ["appointment", "id, user_id, counselor_id, appointment_time, duration_minutes, type, issue_description, status", "保存用户预约咨询师的业务记录，支撑待确认、已确认、已拒绝、已取消等状态流转。"],
        ["assessment_scale", "id, name, code, description, question_json, rule_json, enabled", "保存心理测评量表及题目配置，前端根据 question_json 动态渲染题目。"],
        ["assessment_record", "id, user_id, scale_id, answer_json, score, risk_probability, result_level, analysis, model_name", "保存用户测评结果、风险概率、风险等级和模型解释结果。"],
        ["chat_message", "id, sender_id, receiver_id, content, file_url, sensitive_flag, review_status", "保存用户与咨询师之间的聊天消息，支持历史消息查询和合规审计。"],
        ["article", "id, title, category, summary, content, author_name, status", "保存心理健康文章内容，用于用户、咨询师和管理员阅读及后台维护。"],
        ["notification", "id, target_user_id, target_role, title, content, created_by", "保存平台通知，可面向指定用户或指定角色进行消息触达。"],
        ["counselor_review", "id, counselor_id, user_id, rating, content", "保存用户对咨询师服务的评价，为后续评分展示和服务质量分析预留数据。"],
        ["operation_log", "id, user_id, module, action, ip, detail", "保存管理员和关键业务操作记录，便于权限审计和问题追踪。"],
    ]
    x = [60, 320, 980, 1840]
    y = 120
    row_h = 110
    draw.rectangle((x[0], y, x[-1], y + row_h), fill="#E6E6E6", outline=LINE, width=3)
    for i, h in enumerate(headers):
        draw.text((x[i] + 18, y + 38), h, font=H2, fill=INK)
    for col in x[1:-1]:
        draw.line((col, y, col, y + row_h * (len(rows) + 1)), fill=LINE, width=2)
    y += row_h
    for idx, row in enumerate(rows):
        fill = "#FFFFFF" if idx % 2 == 0 else "#F2F2F2"
        draw.rectangle((x[0], y, x[-1], y + row_h), fill=fill, outline=LINE, width=2)
        widths = [16, 48, 56]
        for i, value in enumerate(row):
            for line_no, line in enumerate(wrap(value, widths[i])[:4]):
                draw.text((x[i] + 18, y + 14 + line_no * 24), line, font=SMALL, fill=INK)
        y += row_h
    save(img, "project-database-table-design.png")


def interface_design_table():
    img = Image.new("RGB", (1900, 1400), BG)
    draw = ImageDraw.Draw(img)
    title(draw, "核心接口设计表")
    headers = ["模块", "接口", "方法", "权限/说明"]
    rows = [
        ["认证模块", "/api/auth/register", "POST", "用户或咨询师注册，咨询师注册时同步创建咨询师资料。"],
        ["认证模块", "/api/auth/login", "POST", "账号密码登录，返回 JWT、用户编号和角色信息。"],
        ["认证模块", "/api/auth/forgot-password", "POST", "根据用户名重置密码，密码摘要后存储。"],
        ["用户模块", "/api/users/me", "GET/PUT", "查询和修改当前登录用户资料。"],
        ["咨询师模块", "/api/counselors", "GET", "用户或管理员查询咨询师列表。"],
        ["咨询师模块", "/api/counselors/me", "GET/PUT", "咨询师查询或修改个人执业资料。"],
        ["预约模块", "/api/appointments", "POST/GET", "用户创建预约并查看自己的预约列表。"],
        ["预约模块", "/api/appointments/{id}/confirm", "POST", "咨询师确认预约，状态变为已确认。"],
        ["预约模块", "/api/appointments/{id}/reject", "POST", "咨询师拒绝预约，状态变为已拒绝。"],
        ["测评模块", "/api/assessments/scales", "GET", "获取启用的心理测评量表配置。"],
        ["测评模块", "/api/assessments/submit", "POST", "提交答案并生成风险分析结果。"],
        ["聊天模块", "/api/chat/history/{peerId}", "GET", "查询当前用户与指定对象的历史消息。"],
        ["聊天模块", "/api/chat/send", "POST", "发送消息并保存到聊天消息表。"],
        ["后台模块", "/api/admin/users", "GET/POST", "管理员查询或新增用户。"],
        ["看板模块", "/api/dashboard/summary", "GET", "管理员获取平台用户、预约、测评和风险统计。"],
    ]
    x = [60, 360, 930, 1120, 1840]
    y = 120
    row_h = 78
    draw.rectangle((x[0], y, x[-1], y + row_h), fill="#E6E6E6", outline=LINE, width=3)
    for i, h in enumerate(headers):
        draw.text((x[i] + 18, y + 25), h, font=H2, fill=INK)
    for col in x[1:-1]:
        draw.line((col, y, col, y + row_h * (len(rows) + 1)), fill=LINE, width=2)
    y += row_h
    for idx, row in enumerate(rows):
        fill = "#FFFFFF" if idx % 2 == 0 else "#F2F2F2"
        draw.rectangle((x[0], y, x[-1], y + row_h), fill=fill, outline=LINE, width=2)
        widths = [16, 42, 10, 48]
        for i, value in enumerate(row):
            for line_no, line in enumerate(wrap(value, widths[i])[:3]):
                draw.text((x[i] + 18, y + 10 + line_no * 22), line, font=SMALL, fill=INK)
        y += row_h
    save(img, "project-interface-design-table.png")


def test_case_table():
    img = Image.new("RGB", (1900, 1300), BG)
    draw = ImageDraw.Draw(img)
    title(draw, "系统测试用例表")
    headers = ["编号", "测试模块", "测试内容", "预期结果"]
    rows = [
        ["T01", "登录认证", "输入正确账号密码登录系统。", "登录成功，系统根据角色跳转到对应首页。"],
        ["T02", "登录认证", "未登录状态直接访问业务页面。", "系统跳转到登录页，无法访问受保护页面。"],
        ["T03", "权限控制", "普通用户访问管理员页面。", "前端路由拦截，后端接口拒绝越权操作。"],
        ["T04", "心理测评", "用户进入测评页并提交完整答案。", "系统生成风险概率、风险等级和主要影响因素并保存记录。"],
        ["T05", "心理测评", "量表配置为空或异常。", "页面给出提示，系统不产生无效测评记录。"],
        ["T06", "预约咨询", "用户选择咨询师并提交预约申请。", "预约记录生成，状态为待确认。"],
        ["T07", "预约咨询", "咨询师确认用户预约。", "预约状态变为已确认，用户获得聊天入口。"],
        ["T08", "预约咨询", "用户取消预约。", "预约状态变为已取消，列表刷新正确。"],
        ["T09", "在线聊天", "用户向已确认咨询师发送消息。", "消息保存成功，接收方在线时收到实时推送。"],
        ["T10", "在线聊天", "WebSocket 断开后发送消息。", "REST 接口仍可保存消息，历史记录可查询。"],
        ["T11", "后台管理", "管理员发布文章或通知。", "内容保存成功，并可在对应列表中查看。"],
        ["T12", "数据看板", "管理员查看统计概览。", "系统展示用户、咨询师、预约、测评和风险统计数据。"],
    ]
    x = [60, 190, 470, 1030, 1840]
    y = 120
    row_h = 82
    draw.rectangle((x[0], y, x[-1], y + row_h), fill="#E6E6E6", outline=LINE, width=3)
    for i, h in enumerate(headers):
        draw.text((x[i] + 18, y + 27), h, font=H2, fill=INK)
    for col in x[1:-1]:
        draw.line((col, y, col, y + row_h * (len(rows) + 1)), fill=LINE, width=2)
    y += row_h
    for idx, row in enumerate(rows):
        fill = "#FFFFFF" if idx % 2 == 0 else "#F2F2F2"
        draw.rectangle((x[0], y, x[-1], y + row_h), fill=fill, outline=LINE, width=2)
        widths = [6, 16, 40, 54]
        for i, value in enumerate(row):
            for line_no, line in enumerate(wrap(value, widths[i])[:3]):
                draw.text((x[i] + 18, y + 12 + line_no * 22), line, font=SMALL, fill=INK)
        y += row_h
    save(img, "project-test-case-table.png")


def main():
    system_structure()
    system_function()
    data_flow()
    system_architecture()
    system_flow()
    use_case_model()
    auth_flow()
    assessment_detail_flow()
    appointment_flow()
    chat_flow()
    counselor_workbench_flow()
    admin_backend_flow()
    er_diagram_detailed()
    database_table_design()
    interface_design_table()
    test_case_table()
    print(OUT)


if __name__ == "__main__":
    main()
