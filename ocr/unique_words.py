import re
import sys
from pathlib import Path

def extract_unique_words(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z]+", text)
    return {word.lower() for word in words}

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    text = Path(input_file).read_text(encoding="utf-8", errors="ignore")
    unique_words = extract_unique_words(text)

    with open(output_file, "w", encoding="utf-8") as f:
        for word in sorted(unique_words):
            f.write(word + "\n")

