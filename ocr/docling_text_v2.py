import sys
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption


def main():
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_formula_enrichment = True
    pipeline_options.do_table_structure = True
    pipeline_options.do_ocr = False

    converter = DocumentConverter(format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    })

    source = sys.argv[1]
    result = converter.convert(source)
    doc = result.document

    output_path = Path(source).with_suffix("").with_suffix(".md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(doc.export_to_markdown())

    print(f"Markdown written to: {output_path}")


if __name__ == "__main__":
    main()
