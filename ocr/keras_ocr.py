"""
Keras OCR Text Detection Script

Performs Optical Character Recognition using Keras OCR framework.
Reads text from an image and displays bounding boxes around detected text regions.

Usage:
    python KerasOCR.py <image_path>
"""

import matplotlib.pyplot as plt
import keras_ocr
import sys
import cv2
import numpy as np
import os

def main():
    """Main function for Keras OCR text detection."""
    if len(sys.argv) != 2:
        print("Usage: python KerasOCR.py <image_path>")
        sys.exit(1)

    filename = sys.argv[1]

    # Validate image file exists
    if not os.path.exists(filename):
        print(f"Error: Image file not found: {filename}")
        sys.exit(1)

    try:
        # Initialize Keras OCR pipeline
        pipeline = keras_ocr.pipeline.Pipeline()

        # Read image
        image = cv2.imread(filename)

        if image is None:
            print(f"Error: Could not read image: {filename}")
            sys.exit(1)

        # Perform OCR (predictions is a list of (text, box) tuples)
        predictions = pipeline.recognize(images=[image])[0]

        # Extract the bounding boxes and texts
        texts = [prediction[0] for prediction in predictions]
        boxes = [prediction[1] for prediction in predictions]

        print("Detected text:")
        for text in texts:
            print(f"  - {text}")

        # Draw bounding boxes on the image
        for box, text in zip(boxes, texts):
            points = np.array(box, dtype=np.int32)
            points = points.reshape((-1, 1, 2))
            cv2.polylines(image, [points], isClosed=True, color=(0, 0, 255), thickness=2)

            # Find the center of the bounding box
            center_x = int(np.mean(points[:, 0, 0]))
            center_y = int(np.mean(points[:, 0, 1]))

            # Add text labels next to the bounding boxes
            cv2.putText(image, text, (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Display the image with bounding boxes
        cv2.imshow('Text Detection - Keras OCR', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"Error during OCR processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
