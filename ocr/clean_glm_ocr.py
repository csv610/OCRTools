
from ollama import chat
import sys
import pathlib
import html
import re
from PIL import Image
import io


# -------------------------------------------------
# Minimal HTML → Markdown (tables + text)
# Standard library only
# -------------------------------------------------

def strip_tags(text: str) -> str:
    """Remove all HTML tags."""
    return re.sub(r"<[^>]+>", "", text)


def extract_tables(html_text: str) -> list[str]:
    """Extract <table>...</table> blocks."""
    return re.findall(r"<table.*?>.*?</table>", html_text, flags=re.S | re.I)


def table_html_to_markdown(table_html: str) -> str:
    rows = re.findall(r"<tr.*?>.*?</tr>", table_html, flags=re.S | re.I)
    table = []

    for row in rows:
        cells = re.findall(r"<t[hd].*?>.*?</t[hd]>", row, flags=re.S | re.I)
        clean_cells = [
            html.unescape(strip_tags(cell)).strip()
            for cell in cells
        ]
        table.append(clean_cells)

    if not table:
        return ""

    max_cols = max(len(r) for r in table)
    table = [r + [""] * (max_cols - len(r)) for r in table]

    md = []
    md.append("| " + " | ".join(table[0]) + " |")
    md.append("| " + " | ".join(["---"] * max_cols) + " |")

    for row in table[1:]:
        md.append("| " + " | ".join(row) + " |")

    return "\n".join(md)


def html_to_markdown(html_text: str) -> str:
    html_text = html.unescape(html_text)

    tables = extract_tables(html_text)
    blocks = []

    for table in tables:
        blocks.append(table_html_to_markdown(table))
        html_text = html_text.replace(table, "")

    # Remaining plain text
    text = strip_tags(html_text).strip()
    if text:
        blocks.append(text)

    return "\n\n".join(blocks).strip()


# -------------------------------------------------
# Main
# -------------------------------------------------

def get_image(image_path):
    img = Image.open(image_path).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def main():
    image_path = sys.argv[1]
    img_bytes  = get_image(image_path)

    response = chat(
        model="glm-ocr",
        messages=[
            {
                "role": "user",
                "content": "Extract content from the image.",
                "images": [img_bytes],
            }
        ],
    )

    raw = response.message.content
    print(raw)
    clean_md = html_to_markdown(raw)

    print(clean_md)


if __name__ == "__main__":
    main()

