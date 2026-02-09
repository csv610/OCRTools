import re
import sys
import os

def clean_markdown(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pass 0: Ensure image blocks are on separate lines
    content = re.sub(r'(!\[.*?\]\(.*?\))', r'\n\1\n', content)

    # Pass 1: Handle line breaks and joins based on full stops
    lines = content.splitlines()
    temp_lines = []
    if lines:
        current = lines[0]
        for i in range(1, len(lines)):
            # For analysis, ignore trailing brackets [..] or (..)
            analysis_line = re.sub(r'\s*[\[\(].*?[\]\)]\s*$', '', current.strip())
            
            # If current line does NOT end with a full stop, join with next line
            # BUT: Do not join if current or next line contains an image block
            has_image_current = bool(re.search(r'!\[.*?\]\(.*?\)', current))
            has_image_next = bool(re.search(r'!\[.*?\]\(.*?\)', lines[i]))

            if not analysis_line.endswith('.') and not has_image_current and not has_image_next:
                current = current.rstrip() + " " + lines[i].lstrip()
            else:
                temp_lines.append(current)
                current = lines[i]
        temp_lines.append(current)

    # Rule 1: If line contains a word in small letters after full stop, break the line.
    intermediate_text = "\n".join(temp_lines)
    intermediate_text = re.sub(r'\.\s+([a-z])', r'.\n\1', intermediate_text)
    
    # Pass 2: Handle small letter starts and all-lowercase lines
    lines = intermediate_text.splitlines()
    final_output = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            final_output.append("")
            continue

        # Skip Rule 3 and 4 if the line contains an image block
        if re.search(r'!\[.*?\]\(.*?\)', stripped):
            final_output.append(line)
            continue

        # Rule 3: Line starting with small letters (until first capital letter) -> split
        if re.match(r'^[a-z]', stripped):
            capital_match = re.search(r'[A-Z]', stripped)
            if capital_match:
                split_point = capital_match.start()
                first_part = stripped[:split_point].strip()
                second_part = stripped[split_point:].strip()
                
                # Analysis: ignore trailing brackets for lowercase check
                analysis_first = re.sub(r'\s*[\[\(].*?[\]\)]\s*$', '', first_part)
                if analysis_first.islower():
                    if final_output and final_output[-1] != "":
                        final_output.append("")
                    final_output.append(f"## {first_part}")
                else:
                    final_output.append(first_part)
                
                final_output.append(second_part)
                continue

        # Rule 4: Line with all smaller letters -> add ## prefix
        # Analysis: ignore trailing brackets for lowercase check
        analysis_line = re.sub(r'\s*[\[\(].*?[\]\)]\s*$', '', stripped)
        if analysis_line.islower():
            if final_output and final_output[-1] != "":
                final_output.append("")
            final_output.append(f"## {stripped}")
        else:
            final_output.append(line)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(final_output))

if __name__ == "__main__":
    # If no argument, it will look for input.md
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.md"
    output_file = "cleaned_markdown.md"
    clean_markdown(input_file, output_file)
