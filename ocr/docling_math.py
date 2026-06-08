#!/usr/bin/env python3
"""
Docling Math Formula Extractor
Extracts mathematical formulas from PDFs as LaTeX using Docling's formula enrichment.
Handles import correctly and saves results to JSON.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

try:
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption, InputFormat
    from docling_core.types.doc import FormulaItem
    print("Docling imported successfully.")
except ImportError as e:
    print(f"Import error: {e}")
    print("Install with: pip install docling[vlm] docling-core")
    sys.exit(1)


def extract_formulas(pdf_path: str) -> List[Dict[str, Any]]:
    """Convert PDF and extract formulas."""
    pdf_path_obj = Path(pdf_path)
    if not pdf_path_obj.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Configure pipeline for formula enrichment
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_formula_enrichment = True

    # Create converter
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )

    # Convert document
    result = converter.convert(str(pdf_path_obj))
    doc = result.document

    # Extract all FormulaItem objects
    formulas = []
    for item, _ in doc.iterate_items():
        if isinstance(item, FormulaItem):
            formulas.append({
                "latex": item.text,
                "bbox": item.bbox.dict() if item.bbox else None,  # Bounding box if available
                "page": getattr(item, 'page_index', None)
            })

    return formulas


def main():
    parser = argparse.ArgumentParser(description="Extract math formulas from PDF as LaTeX.")
    parser.add_argument("pdf_path", help="Path to input PDF file")
    parser.add_argument("-o", "--output", help="Output JSON file (default: formulas.json)")
    args = parser.parse_args()

    try:
        formulas = extract_formulas(args.pdf_path)
        print(f"Extracted {len(formulas)} formulas.")

        # Print to console
        for i, f in enumerate(formulas, 1):
            print(f"\nFormula {i}:")
            print(f"  LaTeX: {f['latex']}")
            if f['bbox']:
                print(f"  BBox: {f['bbox']}")

        # Save to JSON
        output_file = args.output or "formulas.json"
        with open(output_file, "w") as f:
            json.dump(formulas, f, indent=2)
        print(f"\nSaved to {output_file}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

