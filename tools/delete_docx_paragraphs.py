from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from docx_reference_merge import NS, body_paragraphs


ET.register_namespace("w", NS["w"])


def delete_paragraphs(src: Path, dst: Path, indices: set[int]) -> None:
    with zipfile.ZipFile(src, "r") as zin:
        files = {name: zin.read(name) for name in zin.namelist()}
    root = ET.fromstring(files["word/document.xml"])
    body = root.find("w:body", NS)
    if body is None:
        raise RuntimeError("document body not found")
    paras = body_paragraphs(root)
    for idx in sorted(indices, reverse=True):
        if 0 <= idx < len(paras):
            body.remove(paras[idx])
    files["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in files.items():
            zout.writestr(name, data)
    print(f"deleted {len(indices)} paragraphs")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=Path)
    parser.add_argument("dst", type=Path)
    parser.add_argument("indices", nargs="+", type=int)
    args = parser.parse_args()
    delete_paragraphs(args.src, args.dst, set(args.indices))


if __name__ == "__main__":
    main()
