"""
TrOCR (Transformer-based OCR) Text Detection Script

Performs Optical Character Recognition using Microsoft's Transformer-based OCR model.
Works particularly well with handwritten text.

Usage:
    python TrOCR.py <image_path>
"""

from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import requests
from PIL import Image
import sys
import os

def main():
    """Main function for TrOCR text detection."""
    if len(sys.argv) != 2:
        print("Usage: python TrOCR.py <image_path>")
        sys.exit(1)

    filename = sys.argv[1]

    # Validate image file exists
    if not os.path.exists(filename):
        print(f"Error: Image file not found: {filename}")
        sys.exit(1)

    try:
        # Load pre-trained TrOCR model and processor
        print("Loading TrOCR model (this may take a moment on first run)...")
        processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
        model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

        # Open and prepare image
        image = Image.open(filename).convert("RGB")

        # Process image and generate text
        pixel_values = processor(image, return_tensors="pt").pixel_values
        generated_ids = model.generate(pixel_values)

        # Decode results
        text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        print("Detected text:")
        print(text)

    except FileNotFoundError:
        print(f"Error: Image file not found: {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during OCR processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
