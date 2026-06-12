from __future__ import annotations

import copy
import os
import re
import shutil
import zipfile
from dataclasses import dataclass
from typing import Iterable
from xml.etree import ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", W_NS)
NS = {"w": W_NS}

TEMPLATE_PATH = "D:\\桌面\\毕业相关\\附件6-2：毕业论文&开题报告模板.docx"
SOURCE_MD = "frontend\\docs\\thesis-draft.md"
OUTPUT_DOCX = "毕业论文初稿-按附件6-2模板.docx"
DEFAULT_DATE = "2026 年 5 月 1 日"


@dataclass
class Block:
    kind: str
    level: int
    text: str


def qn(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def make_run(text: str, *, bold: bool = False) -> ET.Element:
    run = ET.Element(qn("r"))
    if bold:
        rpr = ET.SubElement(run, qn("rPr"))
        ET.SubElement(rpr, qn("b"))
        ET.SubElement(rpr, qn("bCs"))
    t = ET.SubElement(run, qn("t"))
    if text.startswith(" ") or text.endswith(" ") or "  " in text:
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return run


def make_paragraph(
    text: str = "",
    *,
    style: str | None = None,
    align: str | None = None,
    bold: bool = False,
    first_line: int | None = None,
    font_size_half_points: int | None = None,
    num_id: int | None = None,
    ilvl: int | None = None,
) -> ET.Element:
    para = ET.Element(qn("p"))
    ppr = None
    if any(value is not None for value in (style, align, first_line, font_size_half_points, num_id, ilvl)):
        ppr = ET.SubElement(para, qn("pPr"))
        if style is not None:
            pstyle = ET.SubElement(ppr, qn("pStyle"))
            pstyle.set(qn("val"), style)
        if num_id is not None and ilvl is not None:
            numpr = ET.SubElement(ppr, qn("numPr"))
            ilvl_el = ET.SubElement(numpr, qn("ilvl"))
            ilvl_el.set(qn("val"), str(ilvl))
            numid_el = ET.SubElement(numpr, qn("numId"))
            numid_el.set(qn("val"), str(num_id))
        if first_line is not None:
            ind = ET.SubElement(ppr, qn("ind"))
            ind.set(qn("firstLine"), str(first_line))
        if align is not None:
            jc = ET.SubElement(ppr, qn("jc"))
            jc.set(qn("val"), align)
        if font_size_half_points is not None:
            rpr = ET.SubElement(ppr, qn("rPr"))
            sz = ET.SubElement(rpr, qn("sz"))
            sz.set(qn("val"), str(font_size_half_points))
            sz_cs = ET.SubElement(rpr, qn("szCs"))
            sz_cs.set(qn("val"), str(font_size_half_points))
    if text:
        para.append(make_run(text, bold=bold))
    return para


def make_page_break() -> ET.Element:
    para = ET.Element(qn("p"))
    run = ET.SubElement(para, qn("r"))
    br = ET.SubElement(run, qn("br"))
    br.set(qn("type"), "page")
    return para


def make_toc_field() -> ET.Element:
    para = ET.Element(qn("p"))
    begin_run = ET.SubElement(para, qn("r"))
    begin = ET.SubElement(begin_run, qn("fldChar"))
    begin.set(qn("fldCharType"), "begin")

    instr_run = ET.SubElement(para, qn("r"))
    instr = ET.SubElement(instr_run, qn("instrText"))
    instr.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    instr.text = ' TOC \\o "1-3" \\h \\z \\u '

    separate_run = ET.SubElement(para, qn("r"))
    separate = ET.SubElement(separate_run, qn("fldChar"))
    separate.set(qn("fldCharType"), "separate")

    hint_run = ET.SubElement(para, qn("r"))
    hint_text = ET.SubElement(hint_run, qn("t"))
    hint_text.text = "右键目录后选择“更新域”，即可生成目录。"

    end_run = ET.SubElement(para, qn("r"))
    end = ET.SubElement(end_run, qn("fldChar"))
    end.set(qn("fldCharType"), "end")
    return para


def make_page_footer() -> ET.Element:
    footer = ET.Element(qn("ftr"))
    para = ET.SubElement(footer, qn("p"))
    ppr = ET.SubElement(para, qn("pPr"))
    pstyle = ET.SubElement(ppr, qn("pStyle"))
    pstyle.set(qn("val"), "11")
    jc = ET.SubElement(ppr, qn("jc"))
    jc.set(qn("val"), "center")

    begin_run = ET.SubElement(para, qn("r"))
    begin = ET.SubElement(begin_run, qn("fldChar"))
    begin.set(qn("fldCharType"), "begin")

    instr_run = ET.SubElement(para, qn("r"))
    instr = ET.SubElement(instr_run, qn("instrText"))
    instr.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    instr.text = " PAGE "

    separate_run = ET.SubElement(para, qn("r"))
    separate = ET.SubElement(separate_run, qn("fldChar"))
    separate.set(qn("fldCharType"), "separate")

    page_run = ET.SubElement(para, qn("r"))
    page_text = ET.SubElement(page_run, qn("t"))
    page_text.text = "1"

    end_run = ET.SubElement(para, qn("r"))
    end = ET.SubElement(end_run, qn("fldChar"))
    end.set(qn("fldCharType"), "end")
    return footer


def load_markdown_blocks(path: str) -> list[Block]:
    with open(path, "r", encoding="utf-8") as file:
        lines = file.read().splitlines()

    blocks: list[Block] = []
    current: list[str] = []

    def flush_paragraph() -> None:
        nonlocal current
        if current:
            blocks.append(Block("paragraph", 0, " ".join(current).strip()))
            current = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading_match:
            flush_paragraph()
            blocks.append(Block("heading", len(heading_match.group(1)), heading_match.group(2).strip()))
            continue

        if re.match(r"^(\[\d+\]|\d+[.)、．]|\d+\s*[）])\s*", stripped):
            flush_paragraph()
            blocks.append(Block("paragraph", 0, stripped))
            continue

        current.append(stripped)

    flush_paragraph()
    return blocks


def strip_heading_prefix(text: str) -> str:
    text = re.sub(r"^第\s*\d+\s*章\s*", "", text)
    text = re.sub(r"^\d+(?:\.\d+){0,3}\s*", "", text)
    return text.strip()


def split_thesis_sections(blocks: Iterable[Block]) -> dict[str, list[Block]]:
    sections = {"abstract_zh": [], "abstract_en": [], "main": [], "references": []}
    target = "ignore"
    for block in blocks:
        if block.kind == "heading" and block.level == 1:
            continue
        if block.kind == "heading" and block.level == 2:
            title = block.text.strip()
            if title == "摘要":
                target = "abstract_zh"
                continue
            if title == "Abstract":
                target = "abstract_en"
                continue
            if title in {"参考文献", "7 参考文献"}:
                target = "references"
                sections[target].append(block)
                continue
            if title == "使用说明":
                target = "ignore"
                continue
            if target == "references":
                target = "main"
        if target != "ignore":
            sections[target].append(block)
    return sections


def title_from_blocks(blocks: Iterable[Block]) -> str:
    for block in blocks:
        if block.kind == "heading" and block.level == 1:
            return block.text.strip()
    raise RuntimeError("No H1 title found in markdown source")


def chunk_title(text: str, width: int = 18) -> list[str]:
    return [text[i : i + width] for i in range(0, len(text), width)]


def build_cover(title: str) -> list[ET.Element]:
    elements: list[ET.Element] = [
        make_paragraph("公开论文", align="center"),
        make_paragraph(),
        make_paragraph("毕业论文（设计）", style="10"),
        make_paragraph(),
    ]
    for line in chunk_title(title):
        elements.append(make_paragraph(line, style="9"))
    elements.extend(
        [
            make_paragraph(),
            make_paragraph("题    目    " + title, align="center", first_line=0),
            make_paragraph("姓    名              [待填写]", align="center", first_line=0),
            make_paragraph("学    号              [待填写]", align="center", first_line=0),
            make_paragraph("专业班级          [待填写]", align="center", first_line=0),
            make_paragraph("指导教师          [待填写]", align="center", first_line=0),
            make_paragraph("学    院              [待填写]", align="center", first_line=0),
            make_paragraph("日    期          " + DEFAULT_DATE, align="center", first_line=0),
            make_page_break(),
        ]
    )
    return elements


def build_commitment() -> list[ET.Element]:
    items = [
        "1.本人郑重承诺所呈交的毕业论文（设计），是在指导教师的指导下严格按照学校和学院有关规定完成的。",
        "2.本人在毕业论文（设计）中引用他人的观点和参考资料均加以注释和说明。",
        "3.与我一同工作过的同学对本研究所做的任何贡献均已在论文中做了明确说明并表示谢意。",
        "4.本人承诺在毕业论文（设计）工作过程中没有抄袭他人研究成果和伪造数据等行为。",
        "5.若本人在毕业论文（设计）中有任何侵犯知识产权的行为，由本人承担相应的法律责任。",
        "6.本人完全了解学校有权保留并向有关部门或机构送交本论文（设计）复印件和电子文档，允许本论文（设计）被查阅和借阅。",
    ]
    elements = [make_paragraph("浙大宁波理工学院本科毕业论文（设计）承诺书", style="28")]
    for item in items:
        elements.append(make_paragraph(item, style="29"))
    elements.extend(
        [
            make_paragraph(),
            make_paragraph("作者签名：________________        日期：______________", style="7", align="center", first_line=0),
            make_page_break(),
        ]
    )
    return elements


def build_acknowledgement() -> list[ET.Element]:
    paragraphs = [
        "致谢",
        "本课题从选题、实现到论文撰写，得到了指导教师和学院老师的持续帮助。由于本版为毕业论文初稿，文中相关致谢对象与表述仍可根据实际指导过程进一步完善。",
        "在项目开发过程中，我围绕心理健康服务平台完成了前端页面构建、后端接口设计、数据库建模以及 CatBoost 风险预测模块接入。老师们在需求梳理、系统结构设计和论文写作规范方面给予了大量指导，使我能够较为完整地完成本次毕业设计工作。",
        "同时，感谢同学与朋友在项目调试、资料查阅和论文修改过程中的支持与建议。感谢家人给予的理解和鼓励，使我能够专注完成毕业设计任务。",
    ]
    elements = [make_paragraph(paragraphs[0], style="9")]
    for text in paragraphs[1:]:
        elements.append(make_paragraph(text, style="7"))
    elements.append(make_page_break())
    return elements


def build_abstract(title: str, zh_blocks: list[Block], en_blocks: list[Block]) -> list[ET.Element]:
    elements = [make_paragraph("摘要", style="9")]
    for block in zh_blocks:
        if block.kind == "paragraph":
            elements.append(make_paragraph(block.text, style="7"))
    elements.append(make_page_break())
    elements.append(make_paragraph("Abstract", style="31"))
    for block in en_blocks:
        if block.kind == "paragraph":
            elements.append(make_paragraph(block.text, style="7"))
    elements.append(make_page_break())
    elements.append(make_paragraph("目录", style="22"))
    elements.append(make_toc_field())
    elements.append(make_page_break())
    return elements


def build_main_content(blocks: list[Block]) -> list[ET.Element]:
    elements: list[ET.Element] = []
    for block in blocks:
        if block.kind == "heading":
            clean = strip_heading_prefix(block.text)
            if block.level == 2:
                elements.append(make_paragraph(clean, style="2", num_id=4, ilvl=0))
            elif block.level == 3:
                elements.append(make_paragraph(clean, style="3", num_id=4, ilvl=1))
            elif block.level == 4:
                elements.append(make_paragraph(clean, style="4", num_id=4, ilvl=2))
            else:
                elements.append(make_paragraph(clean, style="5", num_id=4, ilvl=3))
        else:
            elements.append(make_paragraph(block.text, style="7"))
    return elements


def build_references(blocks: list[Block]) -> list[ET.Element]:
    elements: list[ET.Element] = []
    for index, block in enumerate(blocks):
        if block.kind == "heading":
            if index == 0:
                elements.append(make_paragraph(strip_heading_prefix(block.text), style="2", num_id=4, ilvl=0))
            continue
        ref_text = re.sub(r"^\[\d+\]\s*", "", block.text).strip()
        elements.append(make_paragraph(ref_text, style="7"))
    return elements


def replace_document_body(output_docx: str, new_body_elements: list[ET.Element]) -> None:
    temp_dir = os.path.join("tools", "_tmp_docx_build")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
    os.makedirs(temp_dir, exist_ok=True)

    copied = os.path.join(temp_dir, "sample.docx")
    shutil.copyfile(TEMPLATE_PATH, copied)
    extract_dir = os.path.join(temp_dir, "extract")
    with zipfile.ZipFile(copied) as archive:
        archive.extractall(extract_dir)

    document_path = os.path.join(extract_dir, "word", "document.xml")
    tree = ET.parse(document_path)
    root = tree.getroot()
    body = root.find("w:body", NS)
    if body is None:
        raise RuntimeError("document body missing in sample docx")

    sect_pr = body.find("w:sectPr", NS)
    if sect_pr is None:
        raise RuntimeError("section properties missing in sample docx")
    sect_copy = copy.deepcopy(sect_pr)

    for child in list(body):
        body.remove(child)
    for element in new_body_elements:
        body.append(element)
    body.append(sect_copy)

    tree.write(document_path, encoding="utf-8", xml_declaration=True)

    footer_xml = ET.ElementTree(make_page_footer())
    word_dir = os.path.join(extract_dir, "word")
    for file_name in os.listdir(word_dir):
        if re.fullmatch(r"footer\d+\.xml", file_name):
            footer_xml.write(os.path.join(word_dir, file_name), encoding="utf-8", xml_declaration=True)

    if os.path.exists(output_docx):
        os.remove(output_docx)
    with zipfile.ZipFile(output_docx, "w", zipfile.ZIP_DEFLATED) as archive:
        for folder, _, files in os.walk(extract_dir):
            for file_name in files:
                full_path = os.path.join(folder, file_name)
                relative_path = os.path.relpath(full_path, extract_dir)
                archive.write(full_path, relative_path)


def main() -> None:
    blocks = load_markdown_blocks(SOURCE_MD)
    title = title_from_blocks(blocks)
    sections = split_thesis_sections(blocks)

    body_elements: list[ET.Element] = []
    body_elements.extend(build_cover(title))
    body_elements.extend(build_commitment())
    body_elements.extend(build_acknowledgement())
    body_elements.extend(build_abstract(title, sections["abstract_zh"], sections["abstract_en"]))
    body_elements.extend(build_main_content(sections["main"]))
    body_elements.extend(build_references(sections["references"]))

    replace_document_body(OUTPUT_DOCX, body_elements)
    print(OUTPUT_DOCX)


if __name__ == "__main__":
    main()
