import fitz  # PyMuPDF
import ollama
import io
from PIL import Image
import sys
import os

def convert_pdf_to_images(pdf_path):
    """Yield one PNG byte stream per page (streaming, no large memory use)."""
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        pix = doc[page_num].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        yield page_num + 1, buf.getvalue()

def load_image_as_bytes(image_path):
    img = Image.open(image_path).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def query_llm_with_image(image_bytes, model="gemma3:27b-cloud", prompt=None):
    if prompt is None:
        prompt = "Extract all readable text from this image and format it as structured Markdown. Do not trucate or make things up"

    response = ollama.chat(
        model=model,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [image_bytes]
        }],
        options={
            "temperature": 0.1,   # ✅ added
            'num_predict': 8000,  # max output tokens
            'num_ctx': 8192       # context window
        }
    )
    return response["message"]["content"]

def extract_to_markdown(input_path, output_file="output.md", prompt=None):
    ext = os.path.splitext(input_path)[1].lower()

    with open(output_file, "w", encoding="utf-8") as md_file:

        # ---- PDF CASE ----
        if ext == ".pdf":
            for page_number, image_bytes in convert_pdf_to_images(input_path):
                print(f"Processing page {page_number}...")
                try:
                    markdown = query_llm_with_image(image_bytes, prompt=prompt)
                    md_file.write(f"\n\n## Page {page_number}\n\n")
                    md_file.write(markdown)
                except Exception as e:
                    print(f"Error processing page {page_number}: {e}")
                    md_file.write(f"\n\n## Page {page_number} (Error)\n\n")
                    md_file.write("_Error extracting content from this page._")

        # ---- IMAGE CASE ----
        else:
            print("Processing image...")
            try:
                image_bytes = load_image_as_bytes(input_path)
                markdown = query_llm_with_image(image_bytes, prompt=prompt)
                md_file.write(markdown)
            except Exception as e:
                print(f"Error processing image: {e}")
                md_file.write("_Error extracting content from this image._")

    print(f"\nDone! Markdown saved to {output_file}")

# -----------------------------
# Usage
# -----------------------------
if __name__ == '__main__':

    input_path = sys.argv[1]
    out_path = "output.md"

    prompt = (
        "Extract all readable text and text chunks from this image "
        "and format it as structured Markdown. "
        "Look in the entire image always and try to retrieve all text!"
    )

    extract_to_markdown(input_path, output_file=out_path, prompt=prompt)

