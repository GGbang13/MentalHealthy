from __future__ import annotations

from pathlib import Path


W, H = 1800, 980
OUT = Path("docs/thesis-assets/project-er-chen-clean.svg")
FONT = "Microsoft YaHei, SimSun, Arial, sans-serif"


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


parts: list[str] = []


def add(raw: str) -> None:
    parts.append(raw)


def text(s: str, x: int, y: int, size: int = 24, weight: int = 400, anchor: str = "middle") -> None:
    add(
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="middle" '
        f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="#111">{esc(s)}</text>'
    )


def line(x1: int, y1: int, x2: int, y2: int, label: str = "", lx: int | None = None, ly: int | None = None) -> None:
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#222" stroke-width="2"/>')
    if label:
        text(label, lx if lx is not None else (x1 + x2) // 2, ly if ly is not None else (y1 + y2) // 2, 20)


def entity(name: str, x: int, y: int, w: int = 150, h: int = 62) -> None:
    add(f'<rect x="{x-w//2}" y="{y-h//2}" width="{w}" height="{h}" fill="#fff" stroke="#222" stroke-width="2"/>')
    text(name, x, y, 24, 500)


def attr(name: str, x: int, y: int, w: int = 128, h: int = 52) -> None:
    add(f'<ellipse cx="{x}" cy="{y}" rx="{w//2}" ry="{h//2}" fill="#fff" stroke="#666" stroke-width="2"/>')
    text(name, x, y, 20)


def rel(name: str, x: int, y: int, w: int = 112, h: int = 68) -> None:
    pts = f"{x},{y-h//2} {x+w//2},{y} {x},{y+h//2} {x-w//2},{y}"
    add(f'<polygon points="{pts}" fill="#fff" stroke="#222" stroke-width="2"/>')
    text(name, x, y, 22)


def attach_attrs(cx: int, cy: int, attrs: list[tuple[str, int, int]]) -> None:
    for name, ax, ay in attrs:
        attr(name, ax, ay)
        line(ax, ay, cx, cy)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    add('<rect width="100%" height="100%" fill="#fff"/>')
    text("心理健康服务平台 ER 图（简化版）", W // 2, 42, 34, 700)

    # Entity coordinates
    user = (210, 455)
    counselor = (520, 190)
    appointment = (860, 190)
    scale = (520, 455)
    record = (860, 455)
    chat = (520, 720)
    review = (860, 720)
    article = (1310, 260)
    notice = (1310, 505)
    log = (1310, 750)

    # Draw entities
    entity("用户", *user)
    entity("咨询师资料", *counselor, 170)
    entity("预约记录", *appointment, 160)
    entity("测评量表", *scale, 160)
    entity("测评记录", *record, 160)
    entity("聊天消息", *chat, 160)
    entity("咨询评价", *review, 160)
    entity("心理文章", *article, 160)
    entity("通知公告", *notice, 160)
    entity("操作日志", *log, 160)

    # Minimal attributes, placed outside the main relationship lanes.
    attach_attrs(*user, [("用户编号", 90, 330), ("用户名", 210, 300), ("角色", 90, 455), ("账号状态", 210, 610)])
    attach_attrs(*counselor, [("专业方向", 405, 88), ("职称", 520, 72), ("在线状态", 645, 88)])
    attach_attrs(*appointment, [("预约时间", 820, 72), ("预约状态", 950, 88)])
    attach_attrs(*scale, [("量表名称", 405, 565), ("量表类型", 520, 595)])
    attach_attrs(*record, [("得分", 825, 565), ("结果等级", 950, 575)])
    attach_attrs(*chat, [("消息内容", 395, 835), ("消息时间", 555, 860)])
    attach_attrs(*review, [("评分", 825, 835), ("评价内容", 970, 845)])
    attach_attrs(*article, [("文章标题", 1460, 180), ("发布状态", 1470, 285)])
    attach_attrs(*notice, [("通知标题", 1480, 455), ("目标角色", 1480, 555)])
    attach_attrs(*log, [("操作模块", 1468, 705), ("操作详情", 1468, 800)])

    # Main relationships in three clean horizontal lanes.
    rel("拥有", 365, 300)
    line(user[0] + 55, user[1] - 45, 325, 323, "1", 292, 352)
    line(405, 276, counselor[0] - 85, counselor[1] + 20, "0..1", 452, 245)

    rel("预约", 690, 190)
    line(counselor[0] + 85, counselor[1], 634, 190, "1", 628, 168)
    line(746, 190, appointment[0] - 80, appointment[1], "N", 775, 168)
    rel("发起", 535, 315)
    line(user[0] + 70, user[1] - 30, 480, 335, "1", 375, 377)
    line(590, 295, appointment[0] - 70, appointment[1] + 30, "N", 705, 265)

    rel("配置", 690, 455)
    line(scale[0] + 80, scale[1], 634, 455, "1", 628, 433)
    line(746, 455, record[0] - 80, record[1], "N", 775, 433)
    rel("提交", 365, 455)
    line(user[0] + 75, user[1], 309, 455, "1", 295, 433)
    line(421, 455, scale[0] - 80, scale[1], "N", 447, 433)
    # Direct user-to-record participation, routed above the scale lane to avoid crossing.
    rel("产生", 690, 365)
    line(user[0] + 75, user[1] - 10, 634, 365, "1", 430, 382)
    line(746, 365, record[0] - 70, record[1] - 30, "N", 775, 340)

    rel("发送/接收", 365, 720, 145)
    line(user[0] + 60, user[1] + 45, 300, 690, "1", 286, 625)
    line(438, 720, chat[0] - 80, chat[1], "N", 462, 697)

    rel("评价", 690, 720)
    line(user[0] + 72, user[1] + 30, 634, 720, "1", 470, 640)
    line(746, 720, review[0] - 80, review[1], "N", 775, 697)
    rel("被评价", 690, 610, 128)
    line(counselor[0] + 50, counselor[1] + 35, 640, 610, "1", 610, 405)
    line(740, 635, review[0] - 45, review[1] - 32, "N", 790, 655)

    # Management entities on the right, connected from user with separate lanes.
    rel("维护", 1110, 260)
    line(user[0] + 75, user[1] - 35, 1054, 260, "1", 760, 290)
    line(1166, 260, article[0] - 80, article[1], "N", 1190, 238)

    rel("发布", 1110, 505)
    line(user[0] + 75, user[1] + 5, 1054, 505, "1", 760, 480)
    line(1166, 505, notice[0] - 80, notice[1], "N", 1190, 483)

    rel("记录", 1110, 750)
    line(user[0] + 75, user[1] + 40, 1054, 750, "1", 760, 680)
    line(1166, 750, log[0] - 80, log[1], "N", 1190, 728)

    text("注：为保证论文插图清晰，本图仅展示核心实体、关键属性和主要联系；完整字段以数据库表结构为准。", W // 2, H - 34, 22)
    add("</svg>")
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(OUT.resolve())


if __name__ == "__main__":
    main()
