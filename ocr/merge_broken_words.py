import re
import sys
from pathlib import Path

def merge_broken_words(text: str) -> str:
    text = re.sub(r'-\s*\n\s*([a-z])', r'\1', text)
    text = re.sub(r'\n+', ' ', text)
    return text

def process_file(input_path: str, output_path: str):
    text = Path(input_path).read_text(encoding="utf-8")
    cleaned = merge_broken_words(text)
    Path(output_path).write_text(cleaned, encoding="utf-8")

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    process_file(input_file, output_file)

