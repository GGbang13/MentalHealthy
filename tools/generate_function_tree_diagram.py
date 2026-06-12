from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "thesis-assets" / "project-system-function.png"
BACKUP = ROOT / "docs" / "thesis-assets" / "project-system-function.old.png"

FONT_REGULAR = Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf")


W, H = 2400, 1320
BLACK = (35, 35, 35)
WHITE = (255, 255, 255)
LINE = (55, 55, 55)


def font(size: int, bold: bool = False):
    path = FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(str(path), size)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def rect(draw, center_x, center_y, w, h, text, fnt, lw=2):
    x1, y1 = center_x - w / 2, center_y - h / 2
    x2, y2 = center_x + w / 2, center_y + h / 2
    draw.rectangle((x1, y1, x2, y2), outline=LINE, width=lw, fill=WHITE)
    tw, th = text_size(draw, text, fnt)
    draw.text((center_x - tw / 2, center_y - th / 2 - 2), text, fill=BLACK, font=fnt)
    return (x1, y1, x2, y2)


def vrect(draw, center_x, top_y, w, h, text, fnt):
    x1, y1 = center_x - w / 2, top_y
    x2, y2 = center_x + w / 2, top_y + h
    draw.rectangle((x1, y1, x2, y2), outline=LINE, width=2, fill=WHITE)
    chars = list(text)
    char_h = 31
    total = len(chars) * char_h
    y = top_y + (h - total) / 2
    for ch in chars:
        tw, th = text_size(draw, ch, fnt)
        draw.text((center_x - tw / 2, y), ch, fill=BLACK, font=fnt)
        y += char_h
    return (x1, y1, x2, y2)


def line(draw, x1, y1, x2, y2, lw=2):
    draw.line((x1, y1, x2, y2), fill=LINE, width=lw)


def connect_vertical(draw, parent_box, child_box):
    px = (parent_box[0] + parent_box[2]) / 2
    py = parent_box[3]
    cx = (child_box[0] + child_box[2]) / 2
    cy = child_box[1]
    mid = (py + cy) / 2
    line(draw, px, py, px, mid)
    line(draw, px, mid, cx, mid)
    line(draw, cx, mid, cx, cy)


def draw_group(draw, parent_box, group_x, group_y, title, leaves, leaf_start_y=560):
    title_font = font(25)
    leaf_font = font(24)
    box = rect(draw, group_x, group_y, 150, 48, title, title_font)
    connect_vertical(draw, parent_box, box)

    base_y = box[3]
    leaf_top = leaf_start_y
    leaf_w = 50
    leaf_h = 150
    if len(leaves) == 1:
        xs = [group_x]
    else:
        gap = 86
        start = group_x - gap * (len(leaves) - 1) / 2
        xs = [start + i * gap for i in range(len(leaves))]

    junction_y = leaf_top - 45
    line(draw, group_x, base_y, group_x, junction_y)
    if xs:
        line(draw, xs[0], junction_y, xs[-1], junction_y)
    for x, text in zip(xs, leaves):
        line(draw, x, junction_y, x, leaf_top)
        vrect(draw, x, leaf_top, leaf_w, leaf_h, text, leaf_font)
    return box


def main():
    if OUT.exists() and not BACKUP.exists():
        BACKUP.write_bytes(OUT.read_bytes())

    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    title = rect(draw, W / 2, 90, 540, 52, "基于SpringBoot和Vue的心理健康服务平台", font(25), lw=2)

    role_y = 245
    user = rect(draw, 520, role_y, 140, 50, "用户", font(25))
    counselor = rect(draw, 1200, role_y, 170, 50, "心理咨询师", font(24))
    admin = rect(draw, 1880, role_y, 150, 50, "管理员", font(25))

    fork_y = 165
    line(draw, W / 2, title[3], W / 2, fork_y)
    line(draw, 520, fork_y, 1880, fork_y)
    for role in (user, counselor, admin):
        cx = (role[0] + role[2]) / 2
        line(draw, cx, fork_y, cx, role[1])

    # 用户端
    draw_group(draw, user, 205, 385, "账号管理", ["注册登录", "修改资料"], 540)
    draw_group(draw, user, 430, 385, "心理测评", ["选择量表", "提交答案", "查看结果"], 540)
    draw_group(draw, user, 700, 385, "咨询预约", ["浏览咨询师", "提交预约", "取消预约"], 540)
    draw_group(draw, user, 955, 385, "互动服务", ["在线聊天", "消息查看", "阅读文章"], 540)

    # 咨询师端
    draw_group(draw, counselor, 1120, 765, "资料维护", ["编辑简介", "设置擅长"], 910)
    draw_group(draw, counselor, 1340, 765, "预约处理", ["查看预约", "同意预约", "拒绝预约"], 910)
    draw_group(draw, counselor, 1595, 765, "咨询沟通", ["在线聊天", "消息查看"], 910)

    # 管理员端
    draw_group(draw, admin, 1585, 385, "用户管理", ["管理用户", "管理咨询师"], 540)
    draw_group(draw, admin, 1825, 385, "内容管理", ["管理文章", "通知管理"], 540)
    draw_group(draw, admin, 2075, 385, "数据监管", ["监控测评", "数据面板", "统计分析"], 540)

    # 管理员与咨询师下层分支的连接增强，保持树状视觉。
    line(draw, 1200, counselor[3], 1200, 700)
    line(draw, 1120, 700, 1595, 700)
    for x in (1120, 1340, 1595):
        line(draw, x, 700, x, 741)

    # 外框留白与论文图风格一致，不使用色块。
    img.save(OUT)
    print(OUT)
    print(BACKUP if BACKUP.exists() else "no backup")


if __name__ == "__main__":
    main()
