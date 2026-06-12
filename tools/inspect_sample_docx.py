from __future__ import annotations

import os
import shutil
import zipfile
from xml.etree import ElementTree as ET


SAMPLE_PATH = (
    "d:\\桌面\\毕业相关\\《毕业设计》相关材料\\格式合格样本（开题报告、论文）\\"
    "格式合格样本\\论文-格式合格样本.docx"
)
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def main() -> None:
    tmp_dir = os.path.join("tools", "_tmp_sample_inspect")
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir, ignore_errors=True)
    os.makedirs(tmp_dir, exist_ok=True)

    copied = os.path.join(tmp_dir, "sample.docx")
    shutil.copyfile(SAMPLE_PATH, copied)
    extracted = os.path.join(tmp_dir, "extract")
    with zipfile.ZipFile(copied) as archive:
        archive.extractall(extracted)

    tree = ET.parse(os.path.join(extracted, "word", "document.xml"))
    root = tree.getroot()
    body = root.find("w:body", NS)
    if body is None:
        raise RuntimeError("document.xml body missing")

    for index, para in enumerate(body.findall("w:p", NS), 1):
        texts = "".join(text.text or "" for text in para.findall(".//w:t", NS)).strip()
        if not texts:
            continue
        style = para.find("w:pPr/w:pStyle", NS)
        style_id = style.attrib.get(f"{{{NS['w']}}}val", "") if style is not None else ""
        print(f"{index:03d}|{style_id}|{texts}")
        if index >= 180:
            break


if __name__ == "__main__":
    main()
