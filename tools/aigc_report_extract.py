from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def qn(name: str) -> str:
    prefix, tag = name.split(":")
    return f"{{{NS[prefix]}}}{tag}"


def para_runs(p: ET.Element) -> list[dict]:
    runs = []
    for r in p.findall("w:r", NS):
        texts = []
        for node in r.iter():
            if node.tag == qn("w:t") and node.text:
                texts.append(node.text)
            elif node.tag == qn("w:tab"):
                texts.append("\t")
        text = "".join(texts)
        if not text:
            continue
        rpr = r.find("w:rPr", NS)
        color = None
        highlight = None
        shading = None
        if rpr is not None:
            c = rpr.find("w:color", NS)
            if c is not None:
                color = c.get(qn("w:val"))
            h = rpr.find("w:highlight", NS)
            if h is not None:
                highlight = h.get(qn("w:val"))
            shd = rpr.find("w:shd", NS)
            if shd is not None:
                shading = shd.get(qn("w:fill"))
        marked = False
        if color and color.upper() not in {"000000", "AUTO"}:
            marked = True
        if highlight and highlight.lower() not in {"none"}:
            marked = True
        if shading and shading.upper() not in {"FFFFFF", "AUTO"}:
            marked = True
        runs.append({"text": text, "color": color, "highlight": highlight, "shading": shading, "marked": marked})
    return runs


def para_text(p: ET.Element) -> str:
    return "".join(run["text"] for run in para_runs(p))


def normalize(text: str) -> str:
    text = re.sub(r"\[[0-9,\-，]+\]", "", text)
    text = re.sub(r"\s+", "", text)
    return text


def extract(docx: Path) -> list[dict]:
    with zipfile.ZipFile(docx) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    body = root.find("w:body", NS)
    out = []
    for i, p in enumerate(body.findall("w:p", NS) if body is not None else []):
        runs = para_runs(p)
        text = "".join(r["text"] for r in runs)
        marked_text = "".join(r["text"] for r in runs if r["marked"])
        marked_chars = sum(len(r["text"]) for r in runs if r["marked"])
        out.append(
            {
                "idx": i,
                "text": text,
                "marked_text": marked_text,
                "marked_chars": marked_chars,
                "chars": len(text),
                "marked_ratio": (marked_chars / len(text)) if text else 0,
                "norm": normalize(text),
            }
        )
    return out


def map_report(report_docx: Path, source_docx: Path, out_json: Path) -> None:
    report = extract(report_docx)
    source = extract(source_docx)
    source_by_norm = {item["norm"]: item for item in source if item["norm"]}
    mapped = []
    for item in report:
        if item["marked_chars"] <= 0 or len(item["text"].strip()) < 15:
            continue
        src = source_by_norm.get(item["norm"])
        mapped.append(
            {
                "report_idx": item["idx"],
                "source_idx": src["idx"] if src else None,
                "marked_ratio": round(item["marked_ratio"], 3),
                "marked_chars": item["marked_chars"],
                "text": item["text"],
                "marked_text": item["marked_text"],
            }
        )
    out_json.write_text(json.dumps(mapped, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"marked paragraphs: {len(mapped)}")
    print(f"mapped to source: {sum(1 for x in mapped if x['source_idx'] is not None)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    map_report(args.report, args.source, args.out)


if __name__ == "__main__":
    main()
