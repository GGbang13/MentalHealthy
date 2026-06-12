from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import re


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "project_current_function_tree_review.docx"
OUT = ROOT / "project_current-1_功能图修改版.docx"
TARGET = "media/image8.png"

# 约 6.3 英寸宽，按新版功能图 2400:1320 的比例设置高度。
CX = 5760720
CY = 3168400


def main():
    with ZipFile(SRC, "r") as zin:
        rels = zin.read("word/_rels/document.xml.rels").decode("utf-8")
        rid_match = re.search(r'Id="([^"]+)"[^>]+Target="' + re.escape(TARGET) + r'"', rels)
        if not rid_match:
            raise RuntimeError("未找到功能图对应关系")
        rid = rid_match.group(1)

        with ZipFile(OUT, "w", ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    xml = data.decode("utf-8")

                    def repl(match):
                        block = match.group(0)
                        if rid not in block:
                            return block
                        block = re.sub(r'<wp:extent cx="\d+" cy="\d+"', f'<wp:extent cx="{CX}" cy="{CY}"', block, count=1)
                        block = re.sub(r'<a:ext cx="\d+" cy="\d+"', f'<a:ext cx="{CX}" cy="{CY}"', block, count=1)
                        return block

                    xml = re.sub(r"<wp:inline.*?</wp:inline>", repl, xml, flags=re.S)
                    data = xml.encode("utf-8")
                zout.writestr(item, data)
    print(OUT)
    print("function image width adjusted")


if __name__ == "__main__":
    main()
