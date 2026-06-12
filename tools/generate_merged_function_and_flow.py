from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "docs" / "thesis-assets"
FONT = Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf")
BLACK = (30, 30, 30)
LINE = (55, 55, 55)
WHITE = (255, 255, 255)


def f(size):
    return ImageFont.truetype(str(FONT), size)


def text_size(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def rect(draw, cx, cy, w, h, text, size=26, lw=2):
    x1, y1, x2, y2 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    draw.rectangle((x1, y1, x2, y2), outline=LINE, width=lw, fill=WHITE)
    font = f(size)
    tw, th = text_size(draw, text, font)
    draw.text((cx - tw / 2, cy - th / 2 - 2), text, fill=BLACK, font=font)
    return (x1, y1, x2, y2)


def vrect(draw, cx, top, w, h, text, size=24):
    x1, y1, x2, y2 = cx - w / 2, top, cx + w / 2, top + h
    draw.rectangle((x1, y1, x2, y2), outline=LINE, width=2, fill=WHITE)
    font = f(size)
    chars = list(text)
    step = 30
    y = top + (h - step * len(chars)) / 2
    for ch in chars:
        tw, th = text_size(draw, ch, font)
        draw.text((cx - tw / 2, y), ch, fill=BLACK, font=font)
        y += step
    return (x1, y1, x2, y2)


def line(draw, x1, y1, x2, y2, lw=2):
    draw.line((x1, y1, x2, y2), fill=LINE, width=lw)


def arrow(draw, x1, y1, x2, y2, lw=2):
    line(draw, x1, y1, x2, y2, lw)
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    size = 12
    a1 = ang + math.pi * 0.82
    a2 = ang - math.pi * 0.82
    p1 = (x2 + size * math.cos(a1), y2 + size * math.sin(a1))
    p2 = (x2 + size * math.cos(a2), y2 + size * math.sin(a2))
    draw.polygon([(x2, y2), p1, p2], fill=LINE)


def connect_down(draw, parent, child):
    px = (parent[0] + parent[2]) / 2
    py = parent[3]
    cx = (child[0] + child[2]) / 2
    cy = child[1]
    mid = (py + cy) / 2
    line(draw, px, py, px, mid)
    line(draw, px, mid, cx, mid)
    line(draw, cx, mid, cx, cy)


def draw_group(draw, parent, x, y, title, leaves, leaf_top):
    title_box = rect(draw, x, y, 150, 48, title, 25)
    connect_down(draw, parent, title_box)
    if len(leaves) == 1:
        xs = [x]
    else:
        gap = 78
        xs = [x - gap * (len(leaves) - 1) / 2 + i * gap for i in range(len(leaves))]
    junction = leaf_top - 38
    tx = (title_box[0] + title_box[2]) / 2
    line(draw, tx, title_box[3], tx, junction)
    line(draw, xs[0], junction, xs[-1], junction)
    for lx, leaf in zip(xs, leaves):
        line(draw, lx, junction, lx, leaf_top)
        vrect(draw, lx, leaf_top, 48, 150, leaf, 23)
    return title_box


def generate_merged():
    img = Image.new("RGB", (2600, 1500), WHITE)
    draw = ImageDraw.Draw(img)

    title = rect(draw, 1300, 70, 560, 52, "心理健康服务平台系统结构与功能图", 25)

    # 结构层作为独立说明，不向下连线，避免与功能树交叉。
    layer_text = "结构层次：表现层 / 业务服务层 / 数据访问层 / 数据存储层 / 模型分析层"
    rect(draw, 1300, 170, 980, 48, layer_text, 23)

    role_y = 300
    user = rect(draw, 520, role_y, 130, 50, "用户", 25)
    counselor = rect(draw, 1320, role_y, 165, 50, "心理咨询师", 24)
    admin = rect(draw, 2120, role_y, 140, 50, "管理员", 25)
    role_fork = 235
    line(draw, 1300, title[3], 1300, role_fork)
    line(draw, 520, role_fork, 2120, role_fork)
    for b in (user, counselor, admin):
        cx = (b[0] + b[2]) / 2
        line(draw, cx, role_fork, cx, b[1])

    # 用户分支
    draw_group(draw, user, 180, 430, "账号管理", ["注册登录", "修改资料"], 585)
    draw_group(draw, user, 440, 430, "心理测评", ["选择量表", "提交答案", "查看结果"], 585)
    draw_group(draw, user, 730, 430, "咨询预约", ["浏览咨询师", "提交预约", "取消预约"], 585)
    draw_group(draw, user, 1010, 430, "互动服务", ["在线聊天", "消息查看", "阅读文章"], 585)

    # 咨询师分支：独立区域，线不跨到管理员
    draw_group(draw, counselor, 1120, 820, "资料维护", ["编辑简介", "设置擅长"], 970)
    draw_group(draw, counselor, 1320, 820, "预约处理", ["查看预约", "同意预约", "拒绝预约"], 970)
    draw_group(draw, counselor, 1540, 820, "咨询沟通", ["在线聊天", "消息查看"], 970)

    # 管理员分支
    draw_group(draw, admin, 1800, 430, "用户管理", ["管理用户", "管理咨询师"], 585)
    draw_group(draw, admin, 2070, 430, "内容管理", ["管理文章", "通知管理"], 585)
    draw_group(draw, admin, 2340, 430, "数据监管", ["监控测评", "数据面板", "统计分析"], 585)

    # 底部技术结构说明，独立成一行，不与树线连接，避免视觉交叉。
    rect(draw, 500, 1370, 210, 50, "Vue 页面组件", 23)
    rect(draw, 960, 1370, 230, 50, "Controller / Service", 23)
    rect(draw, 1370, 1370, 190, 50, "Mapper", 23)
    rect(draw, 1740, 1370, 190, 50, "MySQL", 23)
    rect(draw, 2140, 1370, 220, 50, "风险预测模型", 23)

    img.save(ASSET / "project-system-function.png")


def diamond(draw, cx, cy, w, h, text, size=24):
    pts = [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)]
    draw.polygon(pts, outline=LINE, fill=WHITE)
    font = f(size)
    lines = text.split("\n")
    total_h = len(lines) * 31
    y = cy - total_h / 2
    for line_text in lines:
        tw, th = text_size(draw, line_text, font)
        draw.text((cx - tw / 2, y), line_text, fill=BLACK, font=font)
        y += 31
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def label(draw, x, y, text):
    draw.text((x, y), text, fill=BLACK, font=f(21))


def generate_flow():
    img = Image.new("RGB", (2200, 1650), WHITE)
    draw = ImageDraw.Draw(img)

    start = rect(draw, 1100, 70, 200, 54, "开始", 25)
    login = rect(draw, 1100, 170, 300, 60, "用户输入账号密码", 24)
    d_login = diamond(draw, 1100, 310, 250, 120, "登录\n是否成功", 23)
    retry = rect(draw, 760, 310, 260, 60, "提示错误并重新登录", 23)
    d_role = diamond(draw, 1100, 470, 260, 120, "判断\n用户角色", 23)

    arrow(draw, 1100, start[3], 1100, login[1])
    arrow(draw, 1100, login[3], 1100, d_login[1])
    arrow(draw, d_login[0], 310, retry[2], 310)
    label(draw, 930, 282, "否")
    arrow(draw, retry[0], 310, 760, 170)
    line(draw, 760, 170, 950, 170)
    arrow(draw, 950, 170, login[0], 170)
    arrow(draw, 1100, d_login[3], 1100, d_role[1])
    label(draw, 1130, 383, "是")

    # 三个角色泳道，互不交叉。
    user_x, counselor_x, admin_x = 430, 1100, 1770
    user_home = rect(draw, user_x, 650, 240, 58, "进入用户端首页", 23)
    counselor_home = rect(draw, counselor_x, 650, 270, 58, "进入咨询师工作台", 23)
    admin_home = rect(draw, admin_x, 650, 240, 58, "进入管理员后台", 23)
    arrow(draw, d_role[0], 470, user_x, user_home[1])
    label(draw, 610, 505, "普通用户")
    arrow(draw, 1100, d_role[3], counselor_x, counselor_home[1])
    label(draw, 1130, 560, "咨询师")
    arrow(draw, d_role[2], 470, admin_x, admin_home[1])
    label(draw, 1440, 505, "管理员")

    # 用户端流程
    d_assess = diamond(draw, user_x, 800, 260, 115, "是否进行\n心理测评", 22)
    assess = rect(draw, user_x, 935, 260, 58, "提交量表答案", 23)
    result = rect(draw, user_x, 1045, 285, 58, "生成风险等级与记录", 23)
    d_appoint = diamond(draw, user_x, 1185, 260, 115, "是否预约\n心理咨询", 22)
    appoint = rect(draw, user_x, 1320, 250, 58, "提交预约申请", 23)
    wait = rect(draw, user_x, 1430, 260, 58, "等待咨询师处理", 23)
    arrow(draw, user_x, user_home[3], user_x, d_assess[1])
    arrow(draw, user_x, d_assess[3], user_x, assess[1])
    label(draw, user_x + 25, 860, "是")
    arrow(draw, user_x, assess[3], user_x, result[1])
    arrow(draw, user_x, result[3], user_x, d_appoint[1])
    arrow(draw, user_x, d_appoint[3], user_x, appoint[1])
    label(draw, user_x + 25, 1245, "是")
    arrow(draw, user_x, appoint[3], user_x, wait[1])
    # 否分支直接查看文章/消息
    browse = rect(draw, 170, 1045, 210, 58, "阅读文章或消息", 23)
    arrow(draw, d_assess[0], 800, 170, browse[1])
    label(draw, 275, 765, "否")
    arrow(draw, d_appoint[0], 1185, 170, browse[3])
    label(draw, 275, 1150, "否")

    # 咨询师流程
    view_req = rect(draw, counselor_x, 800, 260, 58, "查看预约申请", 23)
    d_accept = diamond(draw, counselor_x, 950, 260, 115, "是否同意\n预约", 22)
    confirm = rect(draw, counselor_x, 1090, 250, 58, "确认预约", 23)
    reject = rect(draw, 1365, 950, 230, 58, "拒绝并关闭", 23)
    chat = rect(draw, counselor_x, 1225, 250, 58, "开放在线聊天", 23)
    follow = rect(draw, counselor_x, 1360, 260, 58, "持续咨询沟通", 23)
    arrow(draw, counselor_x, counselor_home[3], counselor_x, view_req[1])
    arrow(draw, counselor_x, view_req[3], counselor_x, d_accept[1])
    arrow(draw, counselor_x, d_accept[3], counselor_x, confirm[1])
    label(draw, counselor_x + 25, 1010, "是")
    arrow(draw, d_accept[2], 950, reject[0], 950)
    label(draw, 1235, 915, "否")
    arrow(draw, counselor_x, confirm[3], counselor_x, chat[1])
    arrow(draw, counselor_x, chat[3], counselor_x, follow[1])

    # 管理员流程
    monitor = rect(draw, admin_x, 800, 270, 58, "查看测评与预约数据", 23)
    d_abnormal = diamond(draw, admin_x, 950, 260, 115, "是否存在\n异常记录", 22)
    handle = rect(draw, admin_x, 1090, 260, 58, "审核处理异常内容", 23)
    maintain = rect(draw, admin_x, 1225, 260, 58, "维护用户与文章", 23)
    board = rect(draw, admin_x, 1360, 245, 58, "查看数据面板", 23)
    arrow(draw, admin_x, admin_home[3], admin_x, monitor[1])
    arrow(draw, admin_x, monitor[3], admin_x, d_abnormal[1])
    arrow(draw, admin_x, d_abnormal[3], admin_x, handle[1])
    label(draw, admin_x + 25, 1010, "是")
    arrow(draw, d_abnormal[0], 950, 1580, 950)
    line(draw, 1580, 950, 1580, 1225)
    arrow(draw, 1580, 1225, maintain[0], 1225)
    label(draw, 1615, 915, "否")
    arrow(draw, admin_x, handle[3], admin_x, maintain[1])
    arrow(draw, admin_x, maintain[3], admin_x, board[1])

    # 结束汇聚，使用底部横线避免交叉。
    end = rect(draw, 1100, 1570, 220, 58, "结束并保存记录", 24)
    y_join = 1500
    for x, b in [(user_x, wait), (counselor_x, follow), (admin_x, board)]:
        line(draw, x, b[3], x, y_join)
    line(draw, user_x, y_join, admin_x, y_join)
    arrow(draw, 1100, y_join, 1100, end[1])

    img.save(ASSET / "project-system-flow.png")


if __name__ == "__main__":
    generate_merged()
    generate_flow()
    print(ASSET / "project-system-function.png")
    print(ASSET / "project-system-flow.png")
