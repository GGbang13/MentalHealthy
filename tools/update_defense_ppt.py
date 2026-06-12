from __future__ import annotations

import os
import re
import shutil
import zipfile
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "vt": "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes",
}

for prefix, uri in NS.items():
    ET.register_namespace("" if prefix == "ct" else prefix, uri)


EMU = 914400
PT = 100
W_IN = 13.333
H_IN = 7.5


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


def add_text_box(
    root: ET.Element,
    shape_id: int,
    name: str,
    text: str,
    x: float,
    y: float,
    w: float,
    h: float,
    font_size: int = 16,
    color: str = "17324D",
    bold: bool = False,
    fill: str | None = None,
    line: str | None = None,
    margin: float = 0.08,
) -> None:
    sp_tree = root.find(".//p:spTree", NS)
    if sp_tree is None:
        raise RuntimeError("slide spTree not found")

    sp = ET.SubElement(sp_tree, q("p", "sp"))
    nv = ET.SubElement(sp, q("p", "nvSpPr"))
    ET.SubElement(nv, q("p", "cNvPr"), {"id": str(shape_id), "name": name})
    ET.SubElement(nv, q("p", "cNvSpPr"), {"txBox": "1"})
    ET.SubElement(nv, q("p", "nvPr"))

    sp_pr = ET.SubElement(sp, q("p", "spPr"))
    xfrm = ET.SubElement(sp_pr, q("a", "xfrm"))
    ET.SubElement(xfrm, q("a", "off"), {"x": emu(x), "y": emu(y)})
    ET.SubElement(xfrm, q("a", "ext"), {"cx": emu(w), "cy": emu(h)})
    prst = ET.SubElement(sp_pr, q("a", "prstGeom"), {"prst": "rect"})
    ET.SubElement(prst, q("a", "avLst"))
    if fill:
        solid = ET.SubElement(sp_pr, q("a", "solidFill"))
        ET.SubElement(solid, q("a", "srgbClr"), {"val": fill})
    else:
        ET.SubElement(sp_pr, q("a", "noFill"))
    if line:
        ln = ET.SubElement(sp_pr, q("a", "ln"), {"w": "6350"})
        solid = ET.SubElement(ln, q("a", "solidFill"))
        ET.SubElement(solid, q("a", "srgbClr"), {"val": line})
    else:
        ET.SubElement(sp_pr, q("a", "ln")).append(ET.Element(q("a", "noFill")))

    tx = ET.SubElement(sp, q("p", "txBody"))
    ET.SubElement(
        tx,
        q("a", "bodyPr"),
        {
            "wrap": "square",
            "lIns": emu(margin),
            "rIns": emu(margin),
            "tIns": emu(margin),
            "bIns": emu(margin),
        },
    )
    ET.SubElement(tx, q("a", "lstStyle"))
    for i, line_text in enumerate(text.split("\n")):
        p = ET.SubElement(tx, q("a", "p"))
        if i:
            p_pr = ET.SubElement(p, q("a", "pPr"))
            p_pr.set("marL", "0")
        r = ET.SubElement(p, q("a", "r"))
        r_pr_attrs = {"lang": "zh-CN", "sz": str(font_size * PT)}
        if bold:
            r_pr_attrs["b"] = "1"
        r_pr = ET.SubElement(r, q("a", "rPr"), r_pr_attrs)
        solid = ET.SubElement(r_pr, q("a", "solidFill"))
        ET.SubElement(solid, q("a", "srgbClr"), {"val": color})
        ET.SubElement(r_pr, q("a", "latin"), {"typeface": "Microsoft YaHei"})
        ET.SubElement(r_pr, q("a", "ea"), {"typeface": "Microsoft YaHei"})
        ET.SubElement(r, q("a", "t")).text = line_text
        ET.SubElement(p, q("a", "endParaRPr"), {"lang": "zh-CN", "sz": str(font_size * PT)})


def add_rule(root: ET.Element, shape_id: int, x: float, y: float, w: float, color: str = "2E8B7B") -> None:
    sp_tree = root.find(".//p:spTree", NS)
    sp = ET.SubElement(sp_tree, q("p", "sp"))
    nv = ET.SubElement(sp, q("p", "nvSpPr"))
    ET.SubElement(nv, q("p", "cNvPr"), {"id": str(shape_id), "name": "目录页分隔线"})
    ET.SubElement(nv, q("p", "cNvSpPr"))
    ET.SubElement(nv, q("p", "nvPr"))
    sp_pr = ET.SubElement(sp, q("p", "spPr"))
    xfrm = ET.SubElement(sp_pr, q("a", "xfrm"))
    ET.SubElement(xfrm, q("a", "off"), {"x": emu(x), "y": emu(y)})
    ET.SubElement(xfrm, q("a", "ext"), {"cx": emu(w), "cy": emu(0.03)})
    geom = ET.SubElement(sp_pr, q("a", "prstGeom"), {"prst": "rect"})
    ET.SubElement(geom, q("a", "avLst"))
    solid = ET.SubElement(sp_pr, q("a", "solidFill"))
    ET.SubElement(solid, q("a", "srgbClr"), {"val": color})
    ET.SubElement(sp_pr, q("a", "ln")).append(ET.Element(q("a", "noFill")))


def build_agenda_slide(layout_rel: str) -> tuple[ET.Element, ET.Element]:
    root = ET.Element(q("p", "sld"))
    c_sld = ET.SubElement(root, q("p", "cSld"))
    bg = ET.SubElement(c_sld, q("p", "bg"))
    bg_pr = ET.SubElement(bg, q("p", "bgPr"))
    fill = ET.SubElement(bg_pr, q("a", "solidFill"))
    ET.SubElement(fill, q("a", "srgbClr"), {"val": "F7FAFC"})
    sp_tree = ET.SubElement(c_sld, q("p", "spTree"))
    nv_grp = ET.SubElement(sp_tree, q("p", "nvGrpSpPr"))
    ET.SubElement(nv_grp, q("p", "cNvPr"), {"id": "1", "name": ""})
    ET.SubElement(nv_grp, q("p", "cNvGrpSpPr"))
    ET.SubElement(nv_grp, q("p", "nvPr"))
    grp_pr = ET.SubElement(sp_tree, q("p", "grpSpPr"))
    xfrm = ET.SubElement(grp_pr, q("a", "xfrm"))
    for tag in ("off", "chOff"):
        ET.SubElement(xfrm, q("a", tag), {"x": "0", "y": "0"})
    for tag in ("ext", "chExt"):
        ET.SubElement(xfrm, q("a", tag), {"cx": emu(W_IN), "cy": emu(H_IN)})

    sid = 2
    add_text_box(root, sid, "目录页标签", "汇报目录", 0.72, 0.52, 2.0, 0.28, 12, "2E8B7B", True)
    sid += 1
    add_text_box(root, sid, "目录页标题", "答辩内容安排", 0.72, 0.95, 5.8, 0.55, 30, "102A43", True)
    sid += 1
    add_text_box(root, sid, "目录页说明", "按照“背景需求—系统设计—核心实现—测试展示—总结展望”的顺序展开。", 0.75, 1.58, 8.7, 0.38, 15, "62748A")
    sid += 1
    add_rule(root, sid, 0.72, 2.13, 11.9)
    sid += 1

    items = [
        ("01", "研究背景与需求分析", "说明课题来源、三类角色需求与业务闭环。"),
        ("02", "系统设计与技术路线", "介绍前后端分离架构、数据库设计和技术选型。"),
        ("03", "核心功能实现", "重点讲认证权限、心理测评、预约咨询与在线聊天。"),
        ("04", "系统展示与测试验证", "展示主要页面，并说明功能、权限和异常测试结果。"),
        ("05", "成果总结与未来展望", "总结完成情况，说明原型系统的不足和改进方向。"),
    ]
    for i, (num, title, desc) in enumerate(items):
        y = 2.5 + i * 0.78
        add_text_box(root, sid, f"目录序号{num}", num, 0.88, y, 0.72, 0.36, 15, "2E8B7B", True)
        sid += 1
        add_text_box(root, sid, f"目录标题{num}", title, 1.65, y - 0.02, 3.2, 0.34, 17, "17324D", True)
        sid += 1
        add_text_box(root, sid, f"目录说明{num}", desc, 5.05, y, 6.65, 0.34, 13, "62748A")
        sid += 1

    add_text_box(root, sid, "目录页页码", "03", 12.12, 7.02, 0.5, 0.22, 9, "62748A")

    clr = ET.SubElement(root, q("p", "clrMapOvr"))
    ET.SubElement(clr, q("a", "masterClrMapping"))

    rels = ET.Element(q("rel", "Relationships"))
    ET.SubElement(
        rels,
        q("rel", "Relationship"),
        {
            "Id": "rId1",
            "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout",
            "Target": layout_rel,
        },
    )
    return root, rels


def update_core_slides(base: Path) -> None:
    additions = {
        8: (
            "说明：登录成功后，前端保存 token 与角色信息；页面跳转由路由守卫控制，接口安全由 Spring Security 与 JWT 过滤器兜底，形成前后端双层权限控制。",
            8.15,
            5.42,
            3.9,
            0.92,
        ),
        9: (
            "说明：测评记录不仅保存分数，还保存风险概率、等级、分析文本和主要影响因素；模型不可用时自动回退，保证系统演示和部署稳定性。",
            7.35,
            5.52,
            4.32,
            0.74,
        ),
        10: (
            "说明：预约模块负责状态流转，聊天模块负责沟通留痕。消息先写入数据库，再通过 WebSocket 推送给在线双方；即使实时连接异常，也能通过历史记录恢复上下文。",
            1.2,
            6.05,
            10.9,
            0.58,
        ),
    }
    for idx, (text, x, y, w, h) in additions.items():
        slide_path = base / "ppt" / "slides" / f"slide{idx}.xml"
        root = ET.parse(slide_path).getroot()
        if any((node.text or "").startswith("说明：") for node in root.findall(".//a:t", NS)):
            continue
        sid = next_shape_id(root)
        add_text_box(root, sid, "核心说明文字", text, x, y, w, h, 12, "17324D", False, "EAF5F2", "D9E5EA", 0.07)
        ET.ElementTree(root).write(slide_path, encoding="utf-8", xml_declaration=True)


def slide_contains(base: Path, needle: str) -> bool:
    for slide_path in (base / "ppt" / "slides").glob("slide*.xml"):
        root = ET.parse(slide_path).getroot()
        text = "".join(node.text or "" for node in root.findall(".//a:t", NS))
        if needle in text:
            return True
    return False


def add_agenda(base: Path) -> None:
    if slide_contains(base, "答辩内容安排"):
        return

    slides_dir = base / "ppt" / "slides"
    slide_nums = sorted(
        int(re.search(r"slide(\d+)\.xml", p.name).group(1))
        for p in slides_dir.glob("slide*.xml")
        if re.search(r"slide(\d+)\.xml", p.name)
    )
    new_num = max(slide_nums) + 1

    rels_template = ET.parse(slides_dir / "_rels" / "slide3.xml.rels").getroot()
    layout_target = "../slideLayouts/slideLayout1.xml"
    for rel in rels_template:
        if rel.get("Type", "").endswith("/slideLayout"):
            layout_target = rel.get("Target", layout_target)
            break

    agenda_root, agenda_rels = build_agenda_slide(layout_target)
    ET.ElementTree(agenda_root).write(slides_dir / f"slide{new_num}.xml", encoding="utf-8", xml_declaration=True)
    rels_out = slides_dir / "_rels" / f"slide{new_num}.xml.rels"
    ET.ElementTree(agenda_rels).write(rels_out, encoding="utf-8", xml_declaration=True)

    content_path = base / "[Content_Types].xml"
    content = ET.parse(content_path)
    content_root = content.getroot()
    part_name = f"/ppt/slides/slide{new_num}.xml"
    if not any(node.get("PartName") == part_name for node in content_root.findall("ct:Override", NS)):
        ET.SubElement(
            content_root,
            q("ct", "Override"),
            {
                "PartName": part_name,
                "ContentType": "application/vnd.openxmlformats-officedocument.presentationml.slide+xml",
            },
        )
    content.write(content_path, encoding="utf-8", xml_declaration=True)

    pres_path = base / "ppt" / "presentation.xml"
    pres = ET.parse(pres_path)
    pres_root = pres.getroot()
    slide_id_list = pres_root.find("p:sldIdLst", NS)
    existing_ids = [int(node.get("id")) for node in slide_id_list.findall("p:sldId", NS)]

    pres_rels_path = base / "ppt" / "_rels" / "presentation.xml.rels"
    pres_rels = ET.parse(pres_rels_path)
    pres_rels_root = pres_rels.getroot()
    rids = []
    for rel in pres_rels_root:
        rid = rel.get("Id", "")
        if rid.startswith("rId") and rid[3:].isdigit():
            rids.append(int(rid[3:]))
    new_rid = f"rId{max(rids, default=1) + 1}"
    ET.SubElement(
        pres_rels_root,
        q("rel", "Relationship"),
        {
            "Id": new_rid,
            "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide",
            "Target": f"slides/slide{new_num}.xml",
        },
    )

    new_slide = ET.Element(q("p", "sldId"), {"id": str(max(existing_ids) + 1), q("r", "id"): new_rid})
    slide_id_list.insert(2, new_slide)
    pres.write(pres_path, encoding="utf-8", xml_declaration=True)
    pres_rels.write(pres_rels_path, encoding="utf-8", xml_declaration=True)

    app_path = base / "docProps" / "app.xml"
    if app_path.exists():
        app = ET.parse(app_path)
        slides = app.getroot().find("{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}Slides")
        if slides is not None and slides.text and slides.text.isdigit():
            slides.text = str(int(slides.text) + 1)
            app.write(app_path, encoding="utf-8", xml_declaration=True)


def slide_order(base: Path) -> list[int]:
    pres = ET.parse(base / "ppt" / "presentation.xml")
    pres_rels = ET.parse(base / "ppt" / "_rels" / "presentation.xml.rels")
    relmap = {rel.get("Id"): rel.get("Target") for rel in pres_rels.getroot()}
    order = []
    for sid in pres.getroot().find("p:sldIdLst", NS):
        rid = sid.get(q("r", "id"))
        target = relmap.get(rid, "")
        match = re.search(r"slide(\d+)\.xml", target)
        if match:
            order.append(int(match.group(1)))
    return order


def set_single_text_by_shape_name(root: ET.Element, shape_name: str, value: str) -> None:
    for sp in root.findall(".//p:sp", NS):
        c_nv_pr = sp.find("./p:nvSpPr/p:cNvPr", NS)
        if c_nv_pr is None or c_nv_pr.get("name") != shape_name:
            continue
        text_nodes = sp.findall(".//a:t", NS)
        if text_nodes:
            text_nodes[0].text = value


def update_footer_numbers(base: Path) -> None:
    for visual_idx, slide_num in enumerate(slide_order(base), 1):
        if visual_idx == 1:
            continue
        slide_path = base / "ppt" / "slides" / f"slide{slide_num}.xml"
        tree = ET.parse(slide_path)
        root = tree.getroot()
        target_text = str(visual_idx).zfill(2)
        changed = False
        for sp in root.findall(".//p:sp", NS):
            c_nv_pr = sp.find("./p:nvSpPr/p:cNvPr", NS)
            shape_name = c_nv_pr.get("name") if c_nv_pr is not None else ""
            if shape_name.startswith("目录序号"):
                continue
            text_nodes = sp.findall(".//a:t", NS)
            joined = "".join(node.text or "" for node in text_nodes).strip()
            if len(text_nodes) == 1 and re.fullmatch(r"\d{1,2}", joined):
                text_nodes[0].text = target_text
                changed = True
        if "答辩内容安排" in "".join(node.text or "" for node in root.findall(".//a:t", NS)):
            for i in range(1, 6):
                set_single_text_by_shape_name(root, f"目录序号{i:02d}", f"{i:02d}")
            set_single_text_by_shape_name(root, "目录页页码", target_text)
            changed = True
        if changed:
            tree.write(slide_path, encoding="utf-8", xml_declaration=True)


def repack(src_dir: Path, dest: Path) -> None:
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as out:
        for file in sorted(src_dir.rglob("*")):
            if file.is_file():
                out.write(file, file.relative_to(src_dir).as_posix())


def main() -> None:
    ppt_dir = Path(os.environ.get("PPT_DIR", "答辩材料"))
    candidates = [path for path in ppt_dir.glob("*.pptx") if "修改前备份" not in path.stem]
    if not candidates:
        raise RuntimeError(f"no target pptx found in {ppt_dir}")
    ppt_path = max(candidates, key=lambda path: path.stat().st_mtime)
    backup_path = ppt_path.with_name(ppt_path.stem + "-修改前备份.pptx")
    if not backup_path.exists():
        shutil.copy2(ppt_path, backup_path)

    with TemporaryDirectory(prefix="defense_ppt_") as tmp:
        tmp_dir = Path(tmp)
        with zipfile.ZipFile(ppt_path) as zf:
            zf.extractall(tmp_dir)
        add_agenda(tmp_dir)
        update_core_slides(tmp_dir)
        update_footer_numbers(tmp_dir)
        repack(tmp_dir, ppt_path)

    print(f"updated={ppt_path}")
    print(f"backup={backup_path}")


if __name__ == "__main__":
    main()
