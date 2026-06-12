from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "project_current_expanded_for_image.docx"
OUT = ROOT / "project_current-1_功能图修改版.docx"
NEW_IMAGE = ROOT / "docs" / "thesis-assets" / "project-system-function.png"
TARGET = "word/media/image8.png"


def main():
    new_data = NEW_IMAGE.read_bytes()
    with ZipFile(SRC, "r") as zin, ZipFile(OUT, "w", ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == TARGET:
                data = new_data
            zout.writestr(item, data)
    print(OUT)
    print(f"replaced {TARGET}")


if __name__ == "__main__":
    main()
