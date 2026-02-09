"""
PaddleOCR Text Detection Script

Performs Optical Character Recognition using PaddleOCR framework.
Reads text from an image and optionally saves results with bounding boxes.

Usage:
    python PaddleOCR.py <image_path> [output_path] [font_path]
"""

from paddleocr import PaddleOCR
import sys
import os
import cv2
import matplotlib.pyplot as plt
import numpy as np

def draw_boxes_on_image(image, boxes, txts, scores):
    """Draw bounding boxes and text on image.

    Args:
        image: Input image
        boxes: List of bounding box coordinates
        txts: List of detected text
        scores: List of confidence scores

    Returns:
        Image with drawn boxes and text
    """
    im_show = image.copy()
    for box, txt, score in zip(boxes, txts, scores):
        box = np.array(box).astype(int)
        cv2.polylines(im_show, [box], True, (0, 255, 0), 2)
        cv2.putText(im_show, f"{txt} ({score:.2f})",
                   tuple(box[0]), cv2.FONT_HERSHEY_SIMPLEX,
                   0.5, (0, 255, 0), 1)
    return im_show

def save_ocr(img_path, out_path, result, font):
    """Save OCR results with bounding boxes to output image.

    Args:
        img_path (str): Path to input image
        out_path (str): Path to output directory
        result (dict): OCR detection result dictionary
        font (str): Path to font file for text rendering
    """
    save_path = os.path.join(out_path, os.path.basename(img_path) + '_output.png')

    image = cv2.imread(img_path)

    if image is None:
        print(f"Error: Could not read image: {img_path}")
        return

    if not isinstance(result, dict) or 'rec_polys' not in result:
        print("Invalid result format for saving OCR visualization")
        return

    boxes = result.get('rec_polys', [])
    txts = result.get('rec_texts', [])
    scores = result.get('rec_scores', [])

    im_show = draw_boxes_on_image(image, boxes, txts, scores)

    cv2.imwrite(save_path, im_show)
    print(f"Output saved to: {save_path}")

def main():
    """Main function for PaddleOCR text detection."""
    if len(sys.argv) < 2:
        print("Usage: python PaddleOCR.py <image_path> [output_path] [font_path]")
        sys.exit(1)

    filename = sys.argv[1]

    # Validate image file exists
    if not os.path.exists(filename):
        print(f"Error: Image file not found: {filename}")
        sys.exit(1)

    try:
        # Initialize PaddleOCR
        ocr = PaddleOCR(lang='en')

        # Perform OCR
        result = ocr.predict(filename)

        # Print results
        if result and isinstance(result, list) and len(result) > 0:
            result_data = result[0]
            if isinstance(result_data, dict) and 'rec_texts' in result_data:
                texts = result_data.get('rec_texts', [])
                scores = result_data.get('rec_scores', [])
                print("Detected text:")
                for text, score in zip(texts, scores):
                    print(f"  - {text} (confidence: {score:.2f})")
            else:
                print("No text detected in image")
        else:
            print("No text detected in image")

        # Save results if output path provided
        if len(sys.argv) >= 3:
            out_path = sys.argv[2]
            font_path = sys.argv[3] if len(sys.argv) >= 4 else None
            if not os.path.exists(out_path):
                os.makedirs(out_path)
            if result and isinstance(result, list) and len(result) > 0:
                save_ocr(filename, out_path, result[0], font_path)

    except Exception as e:
        print(f"Error during OCR processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
