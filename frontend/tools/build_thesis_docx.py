from __future__ import annotations

import html
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "thesis-draft.md"
OUTPUT = ROOT / "毕业论文初稿-按附件6-2模板-格式修正版.docx"
TEMPLATE = Path(r"d:\桌面\毕业相关\附件6-2：毕业论文&开题报告模板.docx")

STYLE_BODY = "7"
STYLE_TOC1 = "13"
STYLE_TOC2 = "15"
STYLE_TOC3 = "8"
STYLE_CHAPTER = "34"
STYLE_SECTION = "16"
STYLE_SUBSECTION = "4"


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def cn_font_run(text: str, bold: bool = False, size: int = 24, east_asia: str = "宋体", ascii_font: str = "Times New Roman") -> str:
    bold_xml = "<w:b/>" if bold else ""
    return (
        "<w:r><w:rPr>"
        f'<w:rFonts w:ascii="{ascii_font}" w:hAnsi="{ascii_font}" w:eastAsia="{east_asia}"/>'
        f"{bold_xml}<w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/>"
        "</w:rPr>"
        f"<w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r>"
    )


def paragraph(
    text: str = "",
    style: str | None = None,
    align: str | None = None,
    bold: bool = False,
    size: int = 24,
    first_line: bool = True,
    east_asia: str = "宋体",
    ascii_font: str = "Times New Roman",
    use_template_spacing: bool = False,
) -> str:
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if align:
        ppr.append(f'<w:jc w:val="{align}"/>')
    if first_line and not style:
        ppr.append('<w:ind w:firstLine="480"/>')
    if not use_template_spacing:
        ppr.append('<w:spacing w:line="360" w:lineRule="auto" w:before="0" w:after="0"/>')
    ppr_xml = f"<w:pPr>{''.join(ppr)}</w:pPr>" if ppr else ""
    return f"<w:p>{ppr_xml}{cn_font_run(text, bold=bold, size=size, east_asia=east_asia, ascii_font=ascii_font)}</w:p>"


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def heading(text: str, level: int) -> str:
    if level == 1:
        return paragraph(text, style=STYLE_CHAPTER, first_line=False, use_template_spacing=True)
    if level == 2:
        return paragraph(text, style=STYLE_SECTION, first_line=False, use_template_spacing=True)
    return paragraph(text, style=STYLE_SUBSECTION, first_line=False, use_template_spacing=True)


def body_paragraph(text: str = "") -> str:
    return paragraph(text, style=STYLE_BODY, first_line=False, size=24, use_template_spacing=True)


def toc_paragraph(text: str) -> str:
    if re.match(r"^\d+\.\d+\.\d+", text):
        style = STYLE_TOC3
    elif re.match(r"^\d+\.\d+", text):
        style = STYLE_TOC2
    else:
        style = STYLE_TOC1
    return paragraph(text, style=style, first_line=False, size=24, use_template_spacing=True)


def parse_markdown(md: str) -> list[str]:
    parts: list[str] = []
    lines = md.splitlines()
    in_toc = False
    for raw in lines:
        line = raw.strip()
        if not line:
            parts.append(paragraph("", first_line=False))
            continue
        if line.startswith("# "):
            parts.append(paragraph(line[2:], align="center", bold=True, size=44, first_line=False, east_asia="黑体"))
            continue
        if line.startswith("## "):
            title = line[3:]
            if re.match(r"^[1-7] ", title):
                in_toc = False
            if re.match(r"^[1-7] ", title):
                parts.append(page_break())
                parts.append(heading(title, 1))
            elif title in {"摘要", "Abstract", "目录", "致谢", "浙大宁波理工学院本科毕业论文（设计）承诺书"}:
                parts.append(page_break())
                if title == "Abstract":
                    parts.append(paragraph(title, align="center", bold=True, size=44, first_line=False, east_asia="Times New Roman"))
                else:
                    parts.append(paragraph(title, align="center", bold=True, size=44, first_line=False, east_asia="黑体"))
                in_toc = title == "目录"
            else:
                parts.append(heading(title, 1))
            continue
        if line.startswith("### "):
            in_toc = False
            parts.append(heading(line[4:], 2))
            continue
        if in_toc:
            parts.append(toc_paragraph(line))
            continue
        if re.match(r"^\[\d+\]", line):
            parts.append(body_paragraph(line))
            continue
        if re.match(r"^\d+\. ", line):
            parts.append(body_paragraph(line))
            continue
        if line.startswith("关键词") or line.startswith("Keywords"):
            parts.append(paragraph(line, first_line=False, size=24, bold=True))
            continue
        if line.startswith("Keyword"):
            parts.append(paragraph(line, first_line=False, size=24, bold=True, ascii_font="Times New Roman", east_asia="Times New Roman"))
            continue
        if line.startswith("题    目") or line.startswith("姓    名") or line.startswith("学    号") or line.startswith("专业班级") or line.startswith("指导教师") or line.startswith("学    院") or line.startswith("日    期"):
            parts.append(paragraph(line, align="center", size=28, first_line=False))
            continue
        parts.append(body_paragraph(line))
    return parts


def styles_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:line="360" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/><w:sz w:val="24"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:qFormat/>
    <w:pPr><w:jc w:val="center"/><w:spacing w:line="360" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="黑体"/><w:b/><w:sz w:val="44"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="MajorTitle">
    <w:name w:val="MajorTitle"/>
    <w:qFormat/>
    <w:pPr><w:jc w:val="center"/><w:spacing w:line="360" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="黑体"/><w:b/><w:sz w:val="44"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:keepNext/><w:jc w:val="center"/><w:spacing w:before="240" w:after="120" w:line="360" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="黑体"/><w:b/><w:sz w:val="32"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:keepNext/><w:spacing w:before="180" w:after="80" w:line="360" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="黑体"/><w:b/><w:sz w:val="30"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading3">
    <w:name w:val="heading 3"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:keepNext/><w:spacing w:before="120" w:after="60" w:line="360" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="黑体"/><w:b/><w:sz w:val="28"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Reference">
    <w:name w:val="Reference"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:spacing w:line="360" w:lineRule="auto"/><w:ind w:hanging="360"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/><w:sz w:val="24"/></w:rPr>
  </w:style>
</w:styles>'''


def content_types_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
  <Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
</Types>'''


def rels_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''


def document_rels_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
</Relationships>'''


def footer_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:p>
    <w:pPr><w:jc w:val="center"/></w:pPr>
    <w:r><w:fldChar w:fldCharType="begin"/></w:r>
    <w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>
    <w:r><w:fldChar w:fldCharType="separate"/></w:r>
    <w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/><w:sz w:val="20"/></w:rPr><w:t>1</w:t></w:r>
    <w:r><w:fldChar w:fldCharType="end"/></w:r>
  </w:p>
</w:ftr>'''


def settings_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:updateFields w:val="true"/>
</w:settings>'''


def template_section_properties() -> str:
    if not TEMPLATE.exists():
        return (
            "<w:sectPr>"
            '<w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>'
            '<w:cols w:space="425"/>'
            '<w:docGrid w:type="lines" w:linePitch="312"/>'
            "</w:sectPr>"
        )
    with zipfile.ZipFile(TEMPLATE) as zf:
        xml = zf.read("word/document.xml").decode("utf-8")
    match = re.search(r"<w:sectPr[\s\S]*?</w:sectPr>", xml)
    if match:
        return match.group(0)
    return ""


def document_xml(body: str) -> str:
    sect = template_section_properties()
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<w:body>{body}{sect}</w:body></w:document>"
    )


def main() -> None:
    md = SOURCE.read_text(encoding="utf-8")
    body = "".join(parse_markdown(md))
    if TEMPLATE.exists():
        with zipfile.ZipFile(TEMPLATE, "r") as src, zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as docx:
            for item in src.infolist():
                if item.filename == "word/document.xml":
                    docx.writestr(item, document_xml(body))
                else:
                    docx.writestr(item, src.read(item.filename))
    else:
        with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as docx:
            docx.writestr("[Content_Types].xml", content_types_xml())
            docx.writestr("_rels/.rels", rels_xml())
            docx.writestr("word/_rels/document.xml.rels", document_rels_xml())
            docx.writestr("word/document.xml", document_xml(body))
            docx.writestr("word/styles.xml", styles_xml())
            docx.writestr("word/settings.xml", settings_xml())
            docx.writestr("word/footer1.xml", footer_xml())
    print(OUTPUT)
    verify_output(OUTPUT)


def verify_output(path: Path) -> None:
    import xml.etree.ElementTree as ET

    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
        style_names = set(zf.namelist())
    wanted_prefixes = (
        "1  绪论1",
        "1.1  研究背景",
        "2  系统需求分析",
        "1  绪论",
        "1.1  研究背景与意义",
        "1 绪论",
        "1.1 研究背景与意义",
        "2 系统需求分析",
        "随着高校心理",
    )
    samples: list[tuple[str, str]] = []
    for para in root.findall(".//w:p", ns):
        text = "".join(t.text or "" for t in para.findall(".//w:t", ns)).strip()
        if not text:
            continue
        style = para.find("./w:pPr/w:pStyle", ns)
        style_id = style.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val") if style is not None else ""
        if text in {"目录", "摘要", "Abstract"} or text.startswith(wanted_prefixes):
            samples.append((style_id, text[:50]))
    print("verify:has_styles", "word/styles.xml" in style_names)
    print("verify:samples")
    for style_id, text in samples[:12]:
        print(f"{style_id}\t{text}")


if __name__ == "__main__":
    main()
