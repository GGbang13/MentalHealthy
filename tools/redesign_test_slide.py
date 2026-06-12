from __future__ import annotations

import os
import posixpath
import re
import shutil
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

for prefix, uri in NS.items():
    ET.register_namespace("" if prefix == "rel" else prefix, uri)

EMU = 914400
PT = 100
FONT = "Microsoft YaHei"


def q(prefix: str, tag: str) -> str:
    return f"{{{NS[prefix]}}}{tag}"


def emu(v: float) -> str:
    return str(round(v * EMU))


def next_shape_id(root: ET.Element) -> int:
    ids = []
    for c_nv_pr in root.findall(".//p:cNvPr", NS):
        value = c_nv_pr.get("id")
        if value and value.isdigit():
            ids.append(int(value))
    return max(ids, default=1) + 1


def xfrm_box(sp: ET.Element) -> tuple[int, int, int, int] | None:
    xfrm = sp.find(".//a:xfrm", NS)
    if xfrm is None:
        return None
    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    if off is None or ext is None:
        return None
    return tuple(map(int, (off.get("x"), off.get("y"), ext.get("cx"), ext.get("cy"))))


def set_box(sp: ET.Element, x: float, y: float, w: float, h: float) -> None:
    xfrm = sp.find(".//a:xfrm", NS)
    if xfrm is None:
        return
    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    if off is not None:
        off.set("x", emu(x))
        off.set("y", emu(y))
    if ext is not None:
        ext.set("cx", emu(w))
        ext.set("cy", emu(h))


def shape_text(sp: ET.Element) -> str:
    return "".join(t.text or "" for t in sp.findall(".//a:t", NS)).strip()


def remove_left_old_table(root: ET.Element) -> None:
    sp_tree = root.find(".//p:spTree", NS)
    for sp in list(sp_tree.findall("p:sp", NS)):
        box = xfrm_box(sp)
        if box is None:
            continue
        x, y, cx, cy = box
        xi, yi, wi, hi = x / EMU, y / EMU, cx / EMU, cy / EMU
        txt = shape_text(sp)
        keep = "测试与验证" in txt or re.fullmatch(r"\d{1,2}", txt or "")
        if not keep and xi < 7.75 and yi > 1.25 and yi < 6.75:
            sp_tree.remove(sp)


def add_shape(root: ET.Element, shape_id: int, name: str, x: float, y: float, w: float, h: float, fill: str, line: str = "D9E5EA", round_rect: bool = False) -> None:
    sp_tree = root.find(".//p:spTree", NS)
    sp = ET.SubElement(sp_tree, q("p", "sp"))
    nv = ET.SubElement(sp, q("p", "nvSpPr"))
    ET.SubElement(nv, q("p", "cNvPr"), {"id": str(shape_id), "name": name})
    ET.SubElement(nv, q("p", "cNvSpPr"))
    ET.SubElement(nv, q("p", "nvPr"))
    sp_pr = ET.SubElement(sp, q("p", "spPr"))
    xfrm = ET.SubElement(sp_pr, q("a", "xfrm"))
    ET.SubElement(xfrm, q("a", "off"), {"x": emu(x), "y": emu(y)})
    ET.SubElement(xfrm, q("a", "ext"), {"cx": emu(w), "cy": emu(h)})
    geom = ET.SubElement(sp_pr, q("a", "prstGeom"), {"prst": "roundRect" if round_rect else "rect"})
    ET.SubElement(geom, q("a", "avLst"))
    solid = ET.SubElement(sp_pr, q("a", "solidFill"))
    ET.SubElement(solid, q("a", "srgbClr"), {"val": fill})
    ln = ET.SubElement(sp_pr, q("a", "ln"), {"w": "6350"})
    ln_fill = ET.SubElement(ln, q("a", "solidFill"))
    ET.SubElement(ln_fill, q("a", "srgbClr"), {"val": line})


def add_text(root: ET.Element, shape_id: int, name: str, value: str, x: float, y: float, w: float, h: float, size: int, color: str = "17324D", bold: bool = False, align: str = "left") -> None:
    sp_tree = root.find(".//p:spTree", NS)
    sp = ET.SubElement(sp_tree, q("p", "sp"))
    nv = ET.SubElement(sp, q("p", "nvSpPr"))
    ET.SubElement(nv, q("p", "cNvPr"), {"id": str(shape_id), "name": name})
    ET.SubElement(nv, q("p", "cNvSpPr"), {"txBox": "1"})
    ET.SubElement(nv, q("p", "nvPr"))
    sp_pr = ET.SubElement(sp, q("p", "spPr"))
    xfrm = ET.SubElement(sp_pr, q("a", "xfrm"))
    ET.SubElement(xfrm, q("a", "off"), {"x": emu(x), "y": emu(y)})
    ET.SubElement(xfrm, q("a", "ext"), {"cx": emu(w), "cy": emu(h)})
    geom = ET.SubElement(sp_pr, q("a", "prstGeom"), {"prst": "rect"})
    ET.SubElement(geom, q("a", "avLst"))
    ET.SubElement(sp_pr, q("a", "noFill"))
    ET.SubElement(sp_pr, q("a", "ln")).append(ET.Element(q("a", "noFill")))
    tx = ET.SubElement(sp, q("p", "txBody"))
    ET.SubElement(tx, q("a", "bodyPr"), {"wrap": "square", "lIns": emu(0.03), "rIns": emu(0.03), "tIns": emu(0.02), "bIns": emu(0.02)})
    ET.SubElement(tx, q("a", "lstStyle"))
    p = ET.SubElement(tx, q("a", "p"))
    ET.SubElement(p, q("a", "pPr"), {"algn": align})
    r = ET.SubElement(p, q("a", "r"))
    attrs = {"lang": "zh-CN", "sz": str(size * PT)}
    if bold:
        attrs["b"] = "1"
    r_pr = ET.SubElement(r, q("a", "rPr"), attrs)
    solid = ET.SubElement(r_pr, q("a", "solidFill"))
    ET.SubElement(solid, q("a", "srgbClr"), {"val": color})
    ET.SubElement(r_pr, q("a", "latin"), {"typeface": FONT})
    ET.SubElement(r_pr, q("a", "ea"), {"typeface": FONT})
    ET.SubElement(r, q("a", "t")).text = value
    ET.SubElement(p, q("a", "endParaRPr"), {"lang": "zh-CN", "sz": str(size * PT)})


def add_matrix(root: ET.Element) -> None:
    sid = next_shape_id(root)
    add_shape(root, sid, "测试矩阵背景", 0.68, 1.58, 6.9, 4.85, "FFFFFF", "DCE8EA", True)
    sid += 1
    add_text(root, sid, "测试矩阵标题", "测试覆盖矩阵", 0.95, 1.86, 2.2, 0.3, 18, "102A43", True)
    sid += 1
    add_text(root, sid, "测试矩阵说明", "围绕用户、咨询师、管理员三类角色，验证核心流程、接口返回和异常兜底。", 3.05, 1.91, 4.05, 0.22, 11, "62748A")
    sid += 1

    x0, y0 = 0.95, 2.42
    col_w = [1.52, 1.72, 1.72, 1.52]
    row_h = 0.52
    headers = ["测试类型", "覆盖对象", "验证重点", "结果"]
    rows = [
        ["功能测试", "登录、测评、预约、聊天", "主流程是否可用", "通过"],
        ["接口测试", "认证、测评、预约、聊天 API", "状态码、返回结构、异常提示", "通过"],
        ["权限测试", "用户、咨询师、管理员", "未登录拦截与角色隔离", "通过"],
        ["异常测试", "表单、Token、WebSocket", "错误输入与连接异常兜底", "通过"],
    ]
    colors = ["EAF5F2", "F7FAFC"]
    x = x0
    for j, h in enumerate(headers):
        add_shape(root, sid, f"表头{j}", x, y0, col_w[j], row_h, "EAF5F2", "D9E5EA")
        sid += 1
        add_text(root, sid, f"表头文字{j}", h, x + 0.08, y0 + 0.17, col_w[j] - 0.16, 0.18, 10, "2E8B7B", True, "center")
        sid += 1
        x += col_w[j]
    for i, row in enumerate(rows):
        y = y0 + row_h * (i + 1)
        x = x0
        for j, cell in enumerate(row):
            fill = "EAF1F8" if row[0] == "接口测试" else colors[i % 2]
            add_shape(root, sid, f"表格{i}_{j}", x, y, col_w[j], row_h, fill, "D9E5EA")
            sid += 1
            color = "3B6EA8" if row[0] == "接口测试" and j == 0 else "17324D"
            add_text(root, sid, f"表格文字{i}_{j}", cell, x + 0.08, y + 0.16, col_w[j] - 0.16, 0.18, 9, color, row[0] == "接口测试" and j == 0, "center" if j == 3 else "left")
            sid += 1
            x += col_w[j]

    add_shape(root, sid, "测试结论背景", 0.95, 5.38, 6.1, 0.56, "EAF5F2", "CFE6DE", True)
    sid += 1
    add_text(root, sid, "测试结论", "测试结论：核心业务链路可运行，接口返回格式统一，权限与异常场景具备基本兜底能力。", 1.12, 5.58, 5.75, 0.18, 11, "2E8B7B", True, "center")


def find_test_slide(base: Path) -> Path:
    pres = ET.parse(base / "ppt" / "presentation.xml").getroot()
    rels = ET.parse(base / "ppt" / "_rels" / "presentation.xml.rels").getroot()
    relmap = {rel.get("Id"): rel.get("Target") for rel in rels}
    for sid in pres.find("p:sldIdLst", NS):
        rid = sid.get(q("r", "id"))
        target = posixpath.normpath("ppt/" + relmap[rid])
        slide_path = base / target
        root = ET.parse(slide_path).getroot()
        txt = "".join(node.text or "" for node in root.findall(".//a:t", NS))
        if "测试与验证" in txt:
            return slide_path
    raise RuntimeError("test slide not found")


def update_test_slide(slide_path: Path) -> None:
    tree = ET.parse(slide_path)
    root = tree.getroot()
    if "测试覆盖矩阵" in "".join(node.text or "" for node in root.findall(".//a:t", NS)):
        return
    remove_left_old_table(root)
    add_matrix(root)
    tree.write(slide_path, encoding="utf-8", xml_declaration=True)


def main() -> None:
    ppt_dir = Path(os.environ.get("PPT_DIR", "答辩材料"))
    candidates = [
        p
        for p in ppt_dir.glob("*.pptx")
        if p.stat().st_size > 1_000_000
        and not p.name.startswith("~$")
        and ("已添加接口测试" in p.name or ("修改前备份" not in p.name and "接口测试" not in p.name))
    ]
    source = max(candidates, key=lambda p: (1 if "已添加接口测试" in p.name else 0, p.stat().st_mtime))
    dest = ppt_dir / "基于SpringBoot和Vue的心理健康服务平台-毕设答辩-测试页美化版.pptx"

    with TemporaryDirectory(prefix="ppt_test_redesign_") as tmp:
        tmp_dir = Path(tmp)
        with zipfile.ZipFile(source) as zf:
            zf.extractall(tmp_dir)
        update_test_slide(find_test_slide(tmp_dir))
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as out:
            for file in sorted(tmp_dir.rglob("*")):
                if file.is_file():
                    out.write(file, file.relative_to(tmp_dir).as_posix())

    print(f"source={source}")
    print(f"output={dest}")


if __name__ == "__main__":
    main()
