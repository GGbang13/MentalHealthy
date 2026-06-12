from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "thesis-assets" / "project-system-flow.png"
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
LINE = (70, 70, 70)


def font(size: int):
    for p in [
        r"C:\Windows\Fonts\simsun.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\NotoSansSC-VF.ttf",
    ]:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def text_size(draw, text, ft):
    box = draw.textbbox((0, 0), text, font=ft)
    return box[2] - box[0], box[3] - box[1]


def center_text(draw, box, text, size=23):
    ft = font(size)
    x1, y1, x2, y2 = box
    lines = text.split("\n")
    line_h = size + 8
    total_h = line_h * len(lines)
    y = y1 + (y2 - y1 - total_h) / 2
    for line in lines:
        tw, th = text_size(draw, line, ft)
        draw.text((x1 + (x2 - x1 - tw) / 2, y), line, font=ft, fill=BLACK)
        y += line_h


def rect(draw, cx, cy, w, h, text, size=23):
    box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    draw.rectangle(box, outline=LINE, width=2, fill=WHITE)
    center_text(draw, box, text, size)
    return box


def diamond(draw, cx, cy, w, h, text, size=22):
    pts = [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)]
    draw.polygon(pts, outline=LINE, fill=WHITE)
    draw.line(pts + [pts[0]], fill=LINE, width=2)
    center_text(draw, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), text, size)
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def line(draw, *pts, width=2):
    draw.line(pts, fill=LINE, width=width)


def arrow_head(draw, p1, p2, size=14):
    x1, y1 = p1
    x2, y2 = p2
    ang = math.atan2(y2 - y1, x2 - x1)
    a1 = ang + math.pi * 0.82
    a2 = ang - math.pi * 0.82
    q1 = (x2 + size * math.cos(a1), y2 + size * math.sin(a1))
    q2 = (x2 + size * math.cos(a2), y2 + size * math.sin(a2))
    draw.polygon([(x2, y2), q1, q2], fill=LINE)


def orth_arrow(draw, pts, width=2):
    """Draw a horizontal/vertical polyline with exactly one arrow at the end."""
    for a, b in zip(pts, pts[1:]):
        line(draw, a, b, width=width)
    arrow_head(draw, pts[-2], pts[-1])


def label(draw, x, y, text, size=21):
    draw.text((x, y), text, font=font(size), fill=BLACK)


def generate():
    img = Image.new("RGB", (2300, 1700), WHITE)
    draw = ImageDraw.Draw(img)

    # 顶部登录流程
    start = rect(draw, 1150, 70, 190, 54, "开始", 24)
    login = rect(draw, 1150, 170, 330, 60, "用户输入账号密码", 23)
    login_ok = diamond(draw, 1150, 315, 250, 120, "登录\n是否成功", 22)
    retry = rect(draw, 760, 315, 280, 58, "提示错误并重新登录", 22)
    role = diamond(draw, 1150, 485, 260, 120, "判断\n用户角色", 22)

    orth_arrow(draw, [(1150, start[3]), (1150, login[1])])
    orth_arrow(draw, [(1150, login[3]), (1150, login_ok[1])])
    orth_arrow(draw, [(login_ok[0], 315), (retry[2], 315)])
    label(draw, 970, 288, "否")
    # 登录失败返回账号密码输入：仅水平/竖直折线，终点一个箭头。
    orth_arrow(draw, [(retry[0], 315), (610, 315), (610, 170), (login[0], 170)])
    orth_arrow(draw, [(1150, login_ok[3]), (1150, role[1])])
    label(draw, 1180, 390, "是")

    # 角色入口。这里也采用正交线，保证全图没有斜线。
    user_x, counselor_x, admin_x = 430, 1150, 1870
    user_home = rect(draw, user_x, 660, 240, 58, "进入用户端首页", 22)
    counselor_home = rect(draw, counselor_x, 660, 275, 58, "进入咨询师工作台", 22)
    admin_home = rect(draw, admin_x, 660, 240, 58, "进入管理员后台", 22)

    role_branch_y = 580
    orth_arrow(draw, [(role[0], 485), (user_x, 485), (user_x, user_home[1])])
    label(draw, 640, 455, "普通用户")
    orth_arrow(draw, [(1150, role[3]), (1150, counselor_home[1])])
    label(draw, 1185, 565, "咨询师")
    orth_arrow(draw, [(role[2], 485), (admin_x, 485), (admin_x, admin_home[1])])
    label(draw, 1500, 455, "管理员")

    # 普通用户流程
    assess_q = diamond(draw, user_x, 815, 260, 115, "是否进行\n心理测评", 22)
    assess = rect(draw, user_x, 955, 260, 58, "提交量表答案", 22)
    result = rect(draw, user_x, 1070, 300, 58, "生成风险等级与记录", 22)
    appoint_q = diamond(draw, user_x, 1215, 260, 115, "是否预约\n心理咨询", 22)
    appoint = rect(draw, user_x, 1360, 255, 58, "提交预约申请", 22)
    wait = rect(draw, user_x, 1470, 270, 58, "等待咨询师处理", 22)
    browse = rect(draw, 160, 1070, 230, 58, "阅读文章或消息", 22)

    orth_arrow(draw, [(user_x, user_home[3]), (user_x, assess_q[1])])
    orth_arrow(draw, [(user_x, assess_q[3]), (user_x, assess[1])])
    label(draw, user_x + 28, 875, "是")
    orth_arrow(draw, [(user_x, assess[3]), (user_x, result[1])])
    orth_arrow(draw, [(user_x, result[3]), (user_x, appoint_q[1])])
    orth_arrow(draw, [(user_x, appoint_q[3]), (user_x, appoint[1])])
    label(draw, user_x + 28, 1278, "是")
    orth_arrow(draw, [(user_x, appoint[3]), (user_x, wait[1])])

    # 是否进行心理测评：否分支只用横竖折线，终点一个箭头。
    orth_arrow(draw, [(assess_q[0], 815), (160, 815), (160, browse[1])])
    label(draw, 250, 785, "否")
    # 是否进行心理预约：否分支只用横竖折线，终点一个箭头。
    orth_arrow(draw, [(appoint_q[0], 1215), (160, 1215), (160, browse[3])])
    label(draw, 250, 1182, "否")

    # 咨询师流程
    view_req = rect(draw, counselor_x, 815, 260, 58, "查看预约申请", 22)
    accept_q = diamond(draw, counselor_x, 970, 260, 115, "是否同意\n预约", 22)
    confirm = rect(draw, counselor_x, 1115, 250, 58, "确认预约", 22)
    reject = rect(draw, 1450, 970, 230, 58, "拒绝并关闭", 22)
    chat = rect(draw, counselor_x, 1255, 250, 58, "开放在线聊天", 22)
    follow = rect(draw, counselor_x, 1395, 260, 58, "持续咨询沟通", 22)
    orth_arrow(draw, [(counselor_x, counselor_home[3]), (counselor_x, view_req[1])])
    orth_arrow(draw, [(counselor_x, view_req[3]), (counselor_x, accept_q[1])])
    orth_arrow(draw, [(counselor_x, accept_q[3]), (counselor_x, confirm[1])])
    label(draw, counselor_x + 28, 1035, "是")
    orth_arrow(draw, [(accept_q[2], 970), (reject[0], 970)])
    label(draw, 1288, 940, "否")
    orth_arrow(draw, [(counselor_x, confirm[3]), (counselor_x, chat[1])])
    orth_arrow(draw, [(counselor_x, chat[3]), (counselor_x, follow[1])])

    # 管理员流程
    monitor = rect(draw, admin_x, 815, 280, 58, "查看测评与预约数据", 22)
    abnormal_q = diamond(draw, admin_x, 970, 260, 115, "是否存在\n异常记录", 22)
    handle = rect(draw, admin_x, 1115, 270, 58, "审核处理异常内容", 22)
    maintain = rect(draw, admin_x, 1255, 270, 58, "维护用户与文章", 22)
    board = rect(draw, admin_x, 1395, 250, 58, "查看数据面板", 22)
    orth_arrow(draw, [(admin_x, admin_home[3]), (admin_x, monitor[1])])
    orth_arrow(draw, [(admin_x, monitor[3]), (admin_x, abnormal_q[1])])
    orth_arrow(draw, [(admin_x, abnormal_q[3]), (admin_x, handle[1])])
    label(draw, admin_x + 28, 1035, "是")
    orth_arrow(draw, [(admin_x, handle[3]), (admin_x, maintain[1])])
    orth_arrow(draw, [(admin_x, maintain[3]), (admin_x, board[1])])
    # 是否存在异常记录：否分支只用横竖折线，终点一个箭头。
    orth_arrow(draw, [(abnormal_q[0], 970), (1630, 970), (1630, 1255), (maintain[0], 1255)])
    label(draw, 1650, 940, "否")

    # 底部汇聚
    end = rect(draw, 1150, 1625, 230, 58, "结束并保存记录", 23)
    join_y = 1545
    for x, b in [(user_x, wait), (counselor_x, follow), (admin_x, board)]:
        line(draw, (x, b[3]), (x, join_y))
    line(draw, (user_x, join_y), (admin_x, join_y))
    orth_arrow(draw, [(1150, join_y), (1150, end[1])])

    img.save(OUT)


if __name__ == "__main__":
    generate()
    print(OUT)
