from __future__ import annotations

from pathlib import Path


W, H = 1900, 1280
OUT = Path("docs/thesis-assets/project-er-chen.svg")


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


parts: list[str] = []


def add(raw: str) -> None:
    parts.append(raw)


def line(x1: int, y1: int, x2: int, y2: int, label: str | None = None, lx: int | None = None, ly: int | None = None) -> None:
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#222" stroke-width="2"/>')
    if label:
        add_text(label, lx if lx is not None else (x1 + x2) // 2, ly if ly is not None else (y1 + y2) // 2, 20)


def add_text(text: str, x: int, y: int, size: int = 24, weight: str = "400", anchor: str = "middle") -> None:
    add(
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="middle" '
        f'font-family="Microsoft YaHei, SimSun, Arial, sans-serif" font-size="{size}" '
        f'font-weight="{weight}" fill="#111">{esc(text)}</text>'
    )


def entity(name: str, x: int, y: int, w: int = 150, h: int = 64) -> tuple[int, int, int, int]:
    add(f'<rect x="{x - w // 2}" y="{y - h // 2}" width="{w}" height="{h}" fill="#fff" stroke="#222" stroke-width="2"/>')
    add_text(name, x, y, 25)
    return x - w // 2, y - h // 2, w, h


def attr(name: str, x: int, y: int, w: int = 140, h: int = 58) -> tuple[int, int]:
    add(f'<ellipse cx="{x}" cy="{y}" rx="{w // 2}" ry="{h // 2}" fill="#fff" stroke="#666" stroke-width="2"/>')
    add_text(name, x, y, 21)
    return x, y


def rel(name: str, x: int, y: int, w: int = 120, h: int = 72) -> tuple[int, int]:
    points = f"{x},{y - h // 2} {x + w // 2},{y} {x},{y + h // 2} {x - w // 2},{y}"
    add(f'<polygon points="{points}" fill="#fff" stroke="#222" stroke-width="2"/>')
    add_text(name, x, y, 22)
    return x, y


def connect_attr(ax: int, ay: int, ex: int, ey: int) -> None:
    line(ax, ay, ex, ey)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    add('<rect width="100%" height="100%" fill="#ffffff"/>')
    add_text("心理健康服务平台 ER 图", W // 2, 44, 34, "700")

    # Entities
    user = (250, 410)
    counselor = (650, 180)
    appointment = (650, 410)
    scale = (1060, 180)
    record = (1060, 410)
    review = (420, 720)
    chat = (820, 720)
    article = (1410, 300)
    notification = (1410, 540)
    log = (1410, 780)

    entity("用户", *user)
    entity("咨询师资料", *counselor, 170, 64)
    entity("预约记录", *appointment, 160, 64)
    entity("测评量表", *scale, 160, 64)
    entity("测评记录", *record, 160, 64)
    entity("咨询评价", *review, 160, 64)
    entity("聊天消息", *chat, 160, 64)
    entity("心理文章", *article, 160, 64)
    entity("通知公告", *notification, 160, 64)
    entity("操作日志", *log, 160, 64)

    # User attributes
    for name, x, y in [
        ("用户编号", 90, 250),
        ("用户名", 250, 230),
        ("角色", 80, 410),
        ("账号状态", 250, 590),
        ("联系方式", 95, 540),
    ]:
        attr(name, x, y)
        connect_attr(x, y, user[0], user[1])

    # Counselor attributes
    for name, x, y in [
        ("资料编号", 520, 70),
        ("职称", 650, 70),
        ("擅长方向", 800, 80),
        ("资质证书", 500, 300),
        ("在线状态", 790, 300),
    ]:
        attr(name, x, y)
        connect_attr(x, y, counselor[0], counselor[1])

    # Appointment attributes
    for name, x, y in [
        ("预约编号", 520, 515),
        ("预约时间", 650, 555),
        ("咨询方式", 790, 520),
        ("预约状态", 650, 300),
    ]:
        attr(name, x, y)
        connect_attr(x, y, appointment[0], appointment[1])

    # Scale attributes
    for name, x, y in [
        ("量表编号", 920, 70),
        ("量表名称", 1060, 65),
        ("量表类型", 1210, 75),
        ("适用人群", 1230, 300),
    ]:
        attr(name, x, y)
        connect_attr(x, y, scale[0], scale[1])

    # Assessment record attributes
    for name, x, y in [
        ("记录编号", 925, 520),
        ("得分", 1060, 560),
        ("风险概率", 1215, 520),
        ("结果等级", 1220, 395),
    ]:
        attr(name, x, y)
        connect_attr(x, y, record[0], record[1])

    # Review attributes
    for name, x, y in [
        ("评价编号", 235, 710),
        ("评分", 420, 855),
        ("评价内容", 570, 850),
    ]:
        attr(name, x, y)
        connect_attr(x, y, review[0], review[1])

    # Chat attributes
    for name, x, y in [
        ("消息编号", 700, 870),
        ("消息内容", 840, 885),
        ("消息时间", 980, 870),
        ("审核状态", 1005, 720),
    ]:
        attr(name, x, y)
        connect_attr(x, y, chat[0], chat[1])

    # Article attributes
    for name, x, y in [
        ("文章编号", 1260, 170),
        ("文章标题", 1410, 150),
        ("文章分类", 1570, 175),
        ("发布状态", 1570, 315),
    ]:
        attr(name, x, y)
        connect_attr(x, y, article[0], article[1])

    # Notification attributes
    for name, x, y in [
        ("通知编号", 1265, 505),
        ("通知标题", 1410, 420),
        ("目标角色", 1580, 505),
        ("发布时间", 1580, 610),
    ]:
        attr(name, x, y)
        connect_attr(x, y, notification[0], notification[1])

    # Log attributes
    for name, x, y in [
        ("日志编号", 1265, 865),
        ("操作模块", 1408, 930),
        ("操作行为", 1580, 860),
        ("操作详情", 1580, 760),
    ]:
        attr(name, x, y)
        connect_attr(x, y, log[0], log[1])

    # Relationships
    rel("拥有", 450, 280)
    line(user[0] + 75, user[1] - 40, 390, 300, "1", 345, 315)
    line(510, 260, counselor[0] - 85, counselor[1] + 28, "0..1", 565, 245)

    rel("预约", 450, 410)
    line(user[0] + 75, user[1], 390, 410, "1", 350, 392)
    line(510, 410, appointment[0] - 80, appointment[1], "N", 565, 392)

    rel("接收", 650, 290)
    line(counselor[0], counselor[1] + 32, 650, 254, "1", 672, 245)
    line(650, 326, appointment[0], appointment[1] - 32, "N", 672, 360)

    rel("提交", 840, 410)
    line(user[0] + 75, user[1], 780, 410, "1", 760, 390)
    line(900, 410, record[0] - 80, record[1], "N", 945, 390)

    rel("生成", 1060, 290)
    line(scale[0], scale[1] + 32, 1060, 254, "1", 1082, 250)
    line(1060, 326, record[0], record[1] - 32, "N", 1082, 360)

    rel("评价", 320, 610)
    line(user[0] + 30, user[1] + 32, 300, 574, "1", 286, 540)
    line(340, 646, review[0] - 80, review[1] - 20, "N", 365, 675)

    rel("被评", 560, 610)
    line(counselor[0] - 35, counselor[1] + 32, 560, 574, "1", 575, 360)
    line(560, 646, review[0] + 80, review[1] - 20, "N", 555, 690)

    rel("发送", 610, 620)
    line(user[0] + 55, user[1] + 32, 560, 596, "1", 500, 555)
    line(660, 644, chat[0] - 80, chat[1] - 22, "N", 700, 675)

    rel("接收", 780, 610)
    line(user[0] + 75, user[1] + 20, 720, 590, "1", 610, 520)
    line(820, 630, chat[0], chat[1] - 32, "N", 840, 665)

    rel("维护", 1245, 300)
    line(user[0] + 75, user[1] - 25, 1185, 300, "1", 1110, 280)
    line(1305, 300, article[0] - 80, article[1], "N", 1330, 280)

    rel("发布", 1245, 540)
    line(user[0] + 75, user[1] + 15, 1185, 540, "1", 1100, 520)
    line(1305, 540, notification[0] - 80, notification[1], "N", 1330, 520)

    rel("记录", 1245, 780)
    line(user[0] + 75, user[1] + 30, 1185, 780, "1", 1110, 760)
    line(1305, 780, log[0] - 80, log[1], "N", 1330, 760)

    add_text("注：图中 0..1 表示可选一对一；N 表示一对多。文章、通知和日志主要服务于后台内容管理与审计追踪。", W // 2, H - 38, 22)
    add("</svg>")

    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(OUT.resolve())


if __name__ == "__main__":
    main()
