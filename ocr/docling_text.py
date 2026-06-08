import sys
from pathlib import Path

from docling.document_converter import DocumentConverter


def main():
    source = sys.argv[1]
    converter = DocumentConverter()
    doc = converter.convert(source).document
    output_path = Path(source).with_suffix("").with_suffix(".md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(doc.export_to_markdown())
    print(f"Markdown written to: {output_path}")


if __name__ == "__main__":
    main()
