from __future__ import annotations

from pathlib import Path


W, H = 1900, 1320
OUT = Path("docs/thesis-assets/project-er-chen-no-cross.svg")
FONT = "Microsoft YaHei, SimSun, Arial, sans-serif"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


parts: list[str] = []


def add(raw: str) -> None:
    parts.append(raw)


def text(s: str, x: int, y: int, size: int = 22, weight: int = 400, anchor: str = "middle") -> None:
    add(
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="middle" '
        f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="#111">{esc(s)}</text>'
    )


def line(x1: int, y1: int, x2: int, y2: int, label: str = "", lx: int | None = None, ly: int | None = None) -> None:
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#222" stroke-width="2"/>')
    if label:
        text(label, lx if lx is not None else (x1 + x2) // 2, ly if ly is not None else (y1 + y2) // 2 - 14, 18)


def entity(name: str, x: int, y: int, w: int = 150, h: int = 58) -> None:
    add(f'<rect x="{x - w/2:.1f}" y="{y - h/2:.1f}" width="{w}" height="{h}" fill="#fff" stroke="#222" stroke-width="2"/>')
    text(name, x, y, 22, 500)


def attr(name: str, x: int, y: int, w: int = 118, h: int = 48) -> None:
    add(f'<ellipse cx="{x}" cy="{y}" rx="{w/2:.1f}" ry="{h/2:.1f}" fill="#fff" stroke="#666" stroke-width="2"/>')
    text(name, x, y, 18)


def attr_connector(ax: int, ay: int, ex: int, ey: int, side: str) -> None:
    # Connect ellipse boundary to rectangle boundary, so the line does not pass
    # through either the attribute oval or the entity rectangle.
    rx, ry = 59, 24
    ew, eh = 75, 29
    if side == "top":
        line(ax, ay + ry, ex, ey - eh)
    elif side == "bottom":
        line(ax, ay - ry, ex, ey + eh)
    elif side == "left":
        line(ax + rx, ay, ex - ew, ey)
    else:
        line(ax - rx, ay, ex + ew, ey)


def rel(name: str, x: int, y: int, w: int = 100, h: int = 62) -> None:
    pts = f"{x},{y - h/2:.1f} {x + w/2:.1f},{y} {x},{y + h/2:.1f} {x - w/2:.1f},{y}"
    add(f'<polygon points="{pts}" fill="#fff" stroke="#222" stroke-width="2"/>')
    text(name, x, y, 20)


def attr_pair(entity_x: int, entity_y: int, attrs: list[str], side: str) -> None:
    if side == "top":
        positions = [(entity_x - 70, entity_y - 82), (entity_x + 70, entity_y - 82)]
    elif side == "bottom":
        positions = [(entity_x - 70, entity_y + 82), (entity_x + 70, entity_y + 82)]
    elif side == "left":
        positions = [(entity_x - 150, entity_y - 30), (entity_x - 150, entity_y + 30)]
    else:
        positions = [(entity_x + 150, entity_y - 30), (entity_x + 150, entity_y + 30)]
    for name, (ax, ay) in zip(attrs, positions):
        attr(name, ax, ay)
        attr_connector(ax, ay, entity_x, entity_y, side)


def row(
    y: int,
    left: str,
    relation: str,
    right: str,
    left_card: tuple[str, str],
    right_card: tuple[str, str],
    l_cardinality: str = "1",
    r_cardinality: str = "N",
) -> None:
    lx, rx, dx = 270, 710, 490
    entity(left, lx, y)
    rel(relation, dx, y)
    entity(right, rx, y)
    line(lx + 75, y, dx - 50, y, l_cardinality, lx + 125, y - 18)
    line(dx + 50, y, rx - 75, y, r_cardinality, rx - 125, y - 18)
    attr_pair(lx, y, list(left_card), "left")
    attr_pair(rx, y, list(right_card), "right")


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    add('<rect width="100%" height="100%" fill="#fff"/>')
    text("心理健康服务平台 ER 图（无交叉线版）", W // 2, 42, 34, 700)

    # Left block: core user-facing business rows. Every row is independent and horizontal.
    rows = [
        (145, "用户", "拥有", "咨询师资料", ("用户编号", "角色"), ("专业方向", "在线状态"), "1", "0..1"),
        (300, "用户", "预约", "预约记录", ("用户编号", "用户名"), ("预约时间", "预约状态"), "1", "N"),
        (455, "咨询师资料", "接收", "预约记录", ("咨询师编号", "专业方向"), ("预约编号", "预约状态"), "1", "N"),
        (610, "用户", "提交", "测评记录", ("用户编号", "用户名"), ("得分", "结果等级"), "1", "N"),
        (765, "测评量表", "生成", "测评记录", ("量表名称", "量表类型"), ("记录编号", "风险概率"), "1", "N"),
        (920, "用户", "发送/接收", "聊天消息", ("用户编号", "角色"), ("消息内容", "消息时间"), "1", "N"),
        (1075, "用户", "评价", "咨询评价", ("用户编号", "用户名"), ("评分", "评价内容"), "1", "N"),
    ]
    for args in rows:
        row(*args)

    # Right block: management and audit rows, separated to avoid any crossing with core rows.
    right_rows = [
        (230, "用户", "维护", "心理文章", ("用户编号", "管理员"), ("文章标题", "发布状态"), "1", "N"),
        (455, "用户", "发布", "通知公告", ("用户编号", "管理员"), ("通知标题", "目标角色"), "1", "N"),
        (680, "用户", "产生", "操作日志", ("用户编号", "用户名"), ("操作模块", "操作详情"), "1", "N"),
        (905, "咨询师资料", "被评价", "咨询评价", ("咨询师编号", "专业方向"), ("评分", "评价内容"), "1", "N"),
    ]
    for y, left, relation, right, l_attrs, r_attrs, lc, rc in right_rows:
        lx, dx, rx = 1140, 1360, 1580
        entity(left, lx, y)
        rel(relation, dx, y)
        entity(right, rx, y)
        line(lx + 75, y, dx - 50, y, lc, lx + 125, y - 18)
        line(dx + 50, y, rx - 75, y, rc, rx - 125, y - 18)
        attr_pair(lx, y, list(l_attrs), "top")
        attr_pair(rx, y, list(r_attrs), "bottom")

    # Section labels and note.
    add('<line x1="980" y1="105" x2="980" y2="1140" stroke="#999" stroke-width="2" stroke-dasharray="8 8"/>')
    text("核心业务关系", 490, 90, 24, 700)
    text("后台管理关系", 1360, 90, 24, 700)
    text(
        "注：为满足无交叉线要求，图中“用户、咨询师资料、预约记录、测评记录、咨询评价”等实体在不同业务关系中重复绘制；语义上均对应同一数据库表。",
        W // 2,
        H - 52,
        22,
    )
    text("完整字段以数据库表结构为准，本图展示主要实体、关键属性和核心联系。", W // 2, H - 22, 20)
    add("</svg>")
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(OUT.resolve())


if __name__ == "__main__":
    main()
