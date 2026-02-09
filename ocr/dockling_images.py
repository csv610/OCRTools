
from pathlib import Path
from docling.document_converter import DocumentConverter
from docling_core.types.doc import PictureItem, TableItem

def extract_images_from_any_document(input_doc_path, output_dir):
    input_doc_path = Path(input_doc_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    doc_converter = DocumentConverter()  # Supports all formats by default
    conv_res = doc_converter.convert(input_doc_path)
    doc_filename = conv_res.input.file.stem

    table_counter = 0
    picture_counter = 0
    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, TableItem):
            table_counter += 1
            img_path = output_dir / f"{doc_filename}-table-{table_counter}.png"
            element.get_image(conv_res.document).save(img_path, "PNG")
        if isinstance(element, PictureItem):
            picture_counter += 1
            img_path = output_dir / f"img-{picture_counter}.png"
            element.get_image(conv_res.document).save(img_path, "PNG")

# Example usage:
import sys
extract_images_from_any_document(sys.argv[1], "pdf_images")
