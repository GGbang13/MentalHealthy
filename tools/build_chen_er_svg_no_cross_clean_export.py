from __future__ import annotations

import importlib.util
from pathlib import Path


BASE_SCRIPT = Path("tools/build_chen_er_svg_no_cross.py")
OUT = Path("docs/thesis-assets/project-er-chen-no-cross-pure.svg")


def main() -> None:
    spec = importlib.util.spec_from_file_location("no_cross", BASE_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    original_out = mod.OUT
    original_w = mod.W
    original_h = mod.H
    mod.OUT = OUT
    mod.parts.clear()

    # Rebuild the same diagram without title, section labels and notes by
    # copying only the drawing core. The canvas is cropped to the graph area.
    mod.W, mod.H = 1800, 1120
    mod.add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{mod.W}" height="{mod.H}" viewBox="0 0 {mod.W} {mod.H}">')
    mod.add('<rect width="100%" height="100%" fill="#fff"/>')

    rows = [
        (105, "用户", "拥有", "咨询师资料", ("用户编号", "角色"), ("专业方向", "在线状态"), "1", "0..1"),
        (260, "用户", "预约", "预约记录", ("用户编号", "用户名"), ("预约时间", "预约状态"), "1", "N"),
        (415, "咨询师资料", "接收", "预约记录", ("咨询师编号", "专业方向"), ("预约编号", "预约状态"), "1", "N"),
        (570, "用户", "提交", "测评记录", ("用户编号", "用户名"), ("得分", "结果等级"), "1", "N"),
        (725, "测评量表", "生成", "测评记录", ("量表名称", "量表类型"), ("记录编号", "风险概率"), "1", "N"),
        (880, "用户", "发送/接收", "聊天消息", ("用户编号", "角色"), ("消息内容", "消息时间"), "1", "N"),
        (1035, "用户", "评价", "咨询评价", ("用户编号", "用户名"), ("评分", "评价内容"), "1", "N"),
    ]
    for args in rows:
        mod.row(*args)

    right_rows = [
        (190, "用户", "维护", "心理文章", ("用户编号", "管理员"), ("文章标题", "发布状态"), "1", "N"),
        (415, "用户", "发布", "通知公告", ("用户编号", "管理员"), ("通知标题", "目标角色"), "1", "N"),
        (640, "用户", "产生", "操作日志", ("用户编号", "用户名"), ("操作模块", "操作详情"), "1", "N"),
        (865, "咨询师资料", "被评价", "咨询评价", ("咨询师编号", "专业方向"), ("评分", "评价内容"), "1", "N"),
    ]
    for y, left, relation, right, l_attrs, r_attrs, lc, rc in right_rows:
        lx, dx, rx = 1140, 1360, 1580
        mod.entity(left, lx, y)
        mod.rel(relation, dx, y)
        mod.entity(right, rx, y)
        mod.line(lx + 75, y, dx - 50, y, lc, lx + 125, y - 18)
        mod.line(dx + 50, y, rx - 75, y, rc, rx - 125, y - 18)
        mod.attr_pair(lx, y, list(l_attrs), "top")
        mod.attr_pair(rx, y, list(r_attrs), "bottom")

    mod.add("</svg>")
    OUT.write_text("\n".join(mod.parts), encoding="utf-8")

    mod.OUT = original_out
    mod.W = original_w
    mod.H = original_h
    print(OUT.resolve())


if __name__ == "__main__":
    main()
