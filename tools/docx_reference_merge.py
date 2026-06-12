from __future__ import annotations

import argparse
import copy
import difflib
import json
import re
import shutil
import zipfile
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}
ET.register_namespace("w", NS["w"])


REF_RE = re.compile(r"(\[\d+(?:[-,，]\d+)*\])")


def qn(name: str) -> str:
    prefix, tag = name.split(":")
    return f"{{{NS[prefix]}}}{tag}"


def para_text(p: ET.Element) -> str:
    parts: list[str] = []
    for node in p.iter():
        if node.tag == qn("w:t") and node.text:
            parts.append(node.text)
        elif node.tag == qn("w:tab"):
            parts.append("\t")
    return "".join(parts)


def normalize_for_match(text: str) -> str:
    text = re.sub(r"\[[0-9,\-，]+\]", "", text)
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[，。；：、,.!！?？（）()《》“”\"'‘’—-]", "", text)
    return text


def extract_paragraphs(docx: Path) -> list[dict]:
    with zipfile.ZipFile(docx) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    body = root.find("w:body", NS)
    if body is None:
        return []
    paras = []
    for idx, p in enumerate(body.findall("w:p", NS)):
        text = para_text(p)
        paras.append(
            {
                "idx": idx,
                "text": text,
                "norm": normalize_for_match(text),
                "refs": REF_RE.findall(text),
            }
        )
    return paras


def text_nodes(p: ET.Element) -> list[ET.Element]:
    return [node for node in p.iter() if node.tag == qn("w:t")]


def replace_para_text_keep_style(p: ET.Element, new_text: str) -> None:
    nodes = text_nodes(p)
    if not nodes:
        run = ET.SubElement(p, qn("w:r"))
        node = ET.SubElement(run, qn("w:t"))
        node.text = new_text
        return
    nodes[0].text = new_text
    if new_text[:1].isspace() or new_text[-1:].isspace():
        nodes[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    for node in nodes[1:]:
        node.text = ""


def body_paragraphs(root: ET.Element) -> list[ET.Element]:
    body = root.find("w:body", NS)
    if body is None:
        return []
    return body.findall("w:p", NS)


def find_reference_start(paras: list[dict]) -> int | None:
    for item in paras:
        if item["text"].strip() in {"参考文献", "参考文献：", "References"}:
            return item["idx"]
    for item in paras:
        if "参考文献" in item["text"].strip() and len(item["text"].strip()) <= 10:
            return item["idx"]
    return None


def best_old_match(new_item: dict, old_with_refs: list[dict]) -> tuple[float, dict | None]:
    n = new_item["norm"]
    if not n:
        return 0.0, None
    best_score = 0.0
    best = None
    for old in old_with_refs:
        o = old["norm"]
        if not o:
            continue
        score = difflib.SequenceMatcher(None, n, o).ratio()
        if score > best_score:
            best_score = score
            best = old
    return best_score, best


def graft_references(new_text: str, old_text: str) -> str:
    refs = REF_RE.findall(old_text)
    if not refs:
        return new_text

    candidate = new_text
    for ref in refs:
        if ref in candidate:
            continue
        old_pos = old_text.find(ref)
        before = normalize_for_match(old_text[:old_pos])
        after = normalize_for_match(old_text[old_pos + len(ref) :])

        insert_at = None
        if before:
            anchor = before[-10:]
            compact = normalize_for_match(candidate)
            pos = compact.find(anchor)
            if pos >= 0:
                target_compact_pos = pos + len(anchor)
                count = 0
                for i, ch in enumerate(candidate):
                    if normalize_for_match(ch):
                        count += 1
                    if count >= target_compact_pos:
                        insert_at = i + 1
                        break
        if insert_at is None and after:
            anchor = after[:10]
            compact = normalize_for_match(candidate)
            pos = compact.find(anchor)
            if pos >= 0:
                count = 0
                for i, ch in enumerate(candidate):
                    if normalize_for_match(ch):
                        if count == pos:
                            insert_at = i
                            break
                        count += 1
        if insert_at is None:
            punct = max(candidate.rfind("。"), candidate.rfind("；"), candidate.rfind("，"))
            insert_at = punct if punct >= 0 else len(candidate)
        candidate = candidate[:insert_at] + ref + candidate[insert_at:]
    return candidate


def collect_reference_block(paras: list[ET.Element], extracted: list[dict]) -> list[ET.Element]:
    start = find_reference_start(extracted)
    if start is None:
        return []
    end = len(extracted)
    for item in extracted[start + 1 :]:
        t = item["text"].strip()
        if re.fullmatch(r"附录.*|致谢|声明", t):
            end = item["idx"]
            break
    return [copy.deepcopy(p) for p in paras[start:end]]


def replace_reference_block(root: ET.Element, old_block: list[ET.Element], new_extracted: list[dict]) -> bool:
    if not old_block:
        return False
    body = root.find("w:body", NS)
    if body is None:
        return False
    children = list(body)
    paras = body_paragraphs(root)
    start_idx = find_reference_start(new_extracted)
    if start_idx is None:
        sect_pr = body.find("w:sectPr", NS)
        insert_at = children.index(sect_pr) if sect_pr is not None and sect_pr in children else len(children)
        for offset, p in enumerate(old_block):
            body.insert(insert_at + offset, p)
        return True
    start_para = paras[start_idx]
    child_start = children.index(start_para)
    end_para_idx = len(paras)
    for item in new_extracted[start_idx + 1 :]:
        t = item["text"].strip()
        if re.fullmatch(r"附录.*|致谢|声明", t):
            end_para_idx = item["idx"]
            break
    if end_para_idx < len(paras):
        child_end = children.index(paras[end_para_idx])
    else:
        sect_pr = body.find("w:sectPr", NS)
        child_end = children.index(sect_pr) if sect_pr is not None and sect_pr in children else len(children)
    for child in children[child_start:child_end]:
        body.remove(child)
    for offset, p in enumerate(old_block):
        body.insert(child_start + offset, p)
    return True


def merge(old_docx: Path, new_docx: Path, out_docx: Path, report_json: Path) -> None:
    old_items = extract_paragraphs(old_docx)
    new_items = extract_paragraphs(new_docx)
    old_ref_start = find_reference_start(old_items)
    old_with_refs = [
        item
        for item in old_items
        if item["refs"] and (old_ref_start is None or item["idx"] < old_ref_start)
    ]

    shutil.copyfile(new_docx, out_docx)
    with zipfile.ZipFile(out_docx, "r") as zin:
        files = {name: zin.read(name) for name in zin.namelist()}
    root = ET.fromstring(files["word/document.xml"])
    new_paras_xml = body_paragraphs(root)

    changes: list[dict] = []
    for new_item in new_items:
        if new_item["refs"]:
            continue
        score, old = best_old_match(new_item, old_with_refs)
        if old is None or score < 0.72:
            continue
        merged = graft_references(new_item["text"], old["text"])
        if merged != new_item["text"]:
            replace_para_text_keep_style(new_paras_xml[new_item["idx"]], merged)
            changes.append(
                {
                    "new_idx": new_item["idx"],
                    "old_idx": old["idx"],
                    "score": round(score, 3),
                    "refs": old["refs"],
                    "before": new_item["text"],
                    "after": merged,
                }
            )

    with zipfile.ZipFile(old_docx) as zf:
        old_root = ET.fromstring(zf.read("word/document.xml"))
    old_block = collect_reference_block(body_paragraphs(old_root), old_items)
    replaced_refs = replace_reference_block(root, old_block, extract_paragraphs(new_docx))

    files["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(out_docx, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in files.items():
            zout.writestr(name, data)
    report_json.write_text(
        json.dumps(
            {
                "changed_paragraphs": len(changes),
                "reference_block_replaced": replaced_refs,
                "changes": changes,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", required=True, type=Path)
    parser.add_argument("--new", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    merge(args.old, args.new, args.out, args.report)


if __name__ == "__main__":
    main()
