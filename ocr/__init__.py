from ocr.clean_markdown_tool import clean_markdown
from ocr.easy_ocr import TextDetection
from ocr.merge_broken_words import merge_broken_words
from ocr.mistral_ocr_pdf import MistralOCR
from ocr.unique_words import extract_unique_words

try:
    from ocr.clean_glm_ocr import html_to_markdown
except ImportError:
    html_to_markdown = None

try:
    from ocr.gemma3_ocr import extract_to_markdown
except ImportError:
    extract_to_markdown = None

try:
    from ocr.olm_ocr import LocalOCR
except ImportError:
    LocalOCR = None

__all__ = [
    "MistralOCR",
    "TextDetection",
    "clean_markdown",
    "extract_to_markdown",
    "extract_unique_words",
    "html_to_markdown",
    "merge_broken_words",
    "LocalOCR",
]
