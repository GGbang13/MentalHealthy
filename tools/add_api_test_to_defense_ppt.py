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


def emu(value: float) -> str:
    return str(round(value * EMU))


def next_shape_id(root: ET.Element) -> int:
    ids = []
    for c_nv_pr in root.findall(".//p:cNvPr", NS):
        value = c_nv_pr.get("id")
        if value and value.isdigit():
            ids.append(int(value))
    return max(ids, default=1) + 1


def add_rect(root: ET.Element, shape_id: int, name: str, x: float, y: float, w: float, h: float, fill: str, line: str) -> None:
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
    geom = ET.SubElement(sp_pr, q("a", "prstGeom"), {"prst": "roundRect"})
    ET.SubElement(geom, q("a", "avLst"))
    solid = ET.SubElement(sp_pr, q("a", "solidFill"))
    ET.SubElement(solid, q("a", "srgbClr"), {"val": fill})
    ln = ET.SubElement(sp_pr, q("a", "ln"), {"w": "6350"})
    ln_fill = ET.SubElement(ln, q("a", "solidFill"))
    ET.SubElement(ln_fill, q("a", "srgbClr"), {"val": line})


def add_bar(root: ET.Element, shape_id: int, x: float, y: float, h: float, color: str) -> None:
    sp_tree = root.find(".//p:spTree", NS)
    sp = ET.SubElement(sp_tree, q("p", "sp"))
    nv = ET.SubElement(sp, q("p", "nvSpPr"))
    ET.SubElement(nv, q("p", "cNvPr"), {"id": str(shape_id), "name": "接口测试强调条"})
    ET.SubElement(nv, q("p", "cNvSpPr"))
    ET.SubElement(nv, q("p", "nvPr"))
    sp_pr = ET.SubElement(sp, q("p", "spPr"))
    xfrm = ET.SubElement(sp_pr, q("a", "xfrm"))
    ET.SubElement(xfrm, q("a", "off"), {"x": emu(x), "y": emu(y)})
    ET.SubElement(xfrm, q("a", "ext"), {"cx": emu(0.08), "cy": emu(h)})
    geom = ET.SubElement(sp_pr, q("a", "prstGeom"), {"prst": "rect"})
    ET.SubElement(geom, q("a", "avLst"))
    solid = ET.SubElement(sp_pr, q("a", "solidFill"))
    ET.SubElement(solid, q("a", "srgbClr"), {"val": color})
    ET.SubElement(sp_pr, q("a", "ln")).append(ET.Element(q("a", "noFill")))


def add_text(root: ET.Element, shape_id: int, name: str, value: str, x: float, y: float, w: float, h: float, size: int, color: str, bold: bool = False) -> None:
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
    ET.SubElement(tx, q("a", "bodyPr"), {"wrap": "square", "lIns": emu(0.03), "rIns": emu(0.03), "tIns": emu(0.03), "bIns": emu(0.03)})
    ET.SubElement(tx, q("a", "lstStyle"))
    p = ET.SubElement(tx, q("a", "p"))
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


def find_test_slide(base: Path) -> Path:
    pres = ET.parse(base / "ppt" / "presentation.xml").getroot()
    rels = ET.parse(base / "ppt" / "_rels" / "presentation.xml.rels").getroot()
    relmap = {rel.get("Id"): rel.get("Target") for rel in rels}
    for sid in pres.find("p:sldIdLst", NS):
        rid = sid.get(q("r", "id"))
        target = posixpath.normpath("ppt/" + relmap[rid])
        slide_path = base / target
        root = ET.parse(slide_path).getroot()
        text = "".join(node.text or "" for node in root.findall(".//a:t", NS))
        if "测试与验证" in text:
            return slide_path
    raise RuntimeError("测试与验证 slide not found")


def update_slide(slide_path: Path) -> None:
    tree = ET.parse(slide_path)
    root = tree.getroot()
    all_text = "".join(node.text or "" for node in root.findall(".//a:t", NS))
    if "接口测试" in all_text:
        return

    for node in root.findall(".//a:t", NS):
        if node.text == "测试与验证：覆盖主流程与边界行为":
            node.text = "测试与验证：覆盖主流程、接口与边界行为"

    sid = next_shape_id(root)
    add_rect(root, sid, "接口测试卡片背景", 8.08, 5.42, 4.0, 0.82, "FFFFFF", "DCE8EA")
    sid += 1
    add_bar(root, sid, 8.08, 5.42, 0.82, "DDAA45")
    sid += 1
    add_text(root, sid, "接口测试标题", "接口测试", 8.32, 5.55, 1.45, 0.24, 14, "17324D", True)
    sid += 1
    add_text(
        root,
        sid,
        "接口测试说明",
        "验证登录认证、测评提交、预约流转、聊天发送、文章通知等 REST API 的返回结构、状态码与异常提示。",
        8.32,
        5.87,
        3.45,
        0.26,
        10,
        "62748A",
    )
    tree.write(slide_path, encoding="utf-8", xml_declaration=True)


def main() -> None:
    ppt_dir = Path(os.environ.get("PPT_DIR", "答辩材料"))
    candidates = [p for p in ppt_dir.glob("*.pptx") if p.stat().st_size > 1_000_000 and "修改前备份" not in p.name and not p.name.startswith("~$")]
    ppt_path = max(candidates, key=lambda p: p.stat().st_mtime)

    backup = ppt_path.with_name(ppt_path.stem + "-接口测试修改前备份.pptx")
    if not backup.exists():
        shutil.copy2(ppt_path, backup)

    with TemporaryDirectory(prefix="ppt_api_test_") as tmp:
        tmp_dir = Path(tmp)
        with zipfile.ZipFile(ppt_path) as zf:
            zf.extractall(tmp_dir)
        update_slide(find_test_slide(tmp_dir))
        tmp_ppt = ppt_path.with_suffix(".tmp.pptx")
        with zipfile.ZipFile(tmp_ppt, "w", zipfile.ZIP_DEFLATED) as out:
            for file in sorted(tmp_dir.rglob("*")):
                if file.is_file():
                    out.write(file, file.relative_to(tmp_dir).as_posix())
        shutil.move(tmp_ppt, ppt_path)

    print(f"updated={ppt_path}")
    print(f"backup={backup}")


if __name__ == "__main__":
    main()
