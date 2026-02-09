"""
EasyOCR Text Detection Script

Performs Optical Character Recognition using EasyOCR framework.
Reads text from an image and displays bounding boxes around detected text regions.

Usage:
    python EasyOCR.py <image_path>
"""

import easyocr
import argparse
import sys
import cv2
import os
import math
import json

class TextDetection:
    """Class to perform Optical Character Recognition using EasyOCR."""

    def __init__(self, languages=['en']):
        """Initialize the EasyOCR reader with specified languages."""
        self.reader = easyocr.Reader(languages)

    def detect_text(self, image_path):
        """Perform text detection on the given image."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        return self.reader.readtext(image_path)

    def save_results_to_json(self, results, output_path):
        """Save OCR results to a JSON file."""
        data = []
        for i, detection in enumerate(results):
            data.append({
                "id": i,
                "box": detection[0],
                "text": detection[1]
            })

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def merge_boxes(self, results, gap=1):
        """Merge bounding boxes if the minimum distance between them is less than gap."""
        if not results:
            return []

        def get_dist(box1, box2):
            """Calculate the minimum distance between two axis-aligned rectangles."""
            b1_x1 = min(p[0] for p in box1)
            b1_y1 = min(p[1] for p in box1)
            b1_x2 = max(p[0] for p in box1)
            b1_y2 = max(p[1] for p in box1)

            b2_x1 = min(p[0] for p in box2)
            b2_y1 = min(p[1] for p in box2)
            b2_x2 = max(p[0] for p in box2)
            b2_y2 = max(p[1] for p in box2)

            dx = max(0, b1_x1 - b2_x2, b2_x1 - b1_x2)
            dy = max(0, b1_y1 - b2_y2, b2_y1 - b1_y2)

            return math.sqrt(dx*dx + dy*dy)

        n = len(results)
        adj = [[] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if get_dist(results[i][0], results[j][0]) < gap:
                    adj[i].append(j)
                    adj[j].append(i)

        visited = [False] * n
        merged_results = []
        for i in range(n):
            if not visited[i]:
                component = []
                stack = [i]
                visited[i] = True
                while stack:
                    u = stack.pop()
                    component.append(u)
                    for v in adj[u]:
                        if not visited[v]:
                            visited[v] = True
                            stack.append(v)

                # Sort component by y then x for logical text flow
                component.sort(key=lambda idx: (results[idx][0][0][1], results[idx][0][0][0]))

                all_boxes = [results[idx][0] for idx in component]
                all_texts = [results[idx][1] for idx in component]
                all_confidences = [results[idx][2] if len(results[idx]) > 2 else 1.0 for idx in component]

                min_x = min(p[0] for box in all_boxes for p in box)
                max_x = max(p[0] for box in all_boxes for p in box)
                min_y = min(p[1] for box in all_boxes for p in box)
                max_y = max(p[1] for box in all_boxes for p in box)

                new_box = [[min_x, min_y], [max_x, min_y], [max_x, max_y], [min_x, max_y]]
                new_text = " ".join(all_texts)
                avg_confidence = sum(all_confidences) / len(all_confidences)

                merged_results.append([new_box, new_text, avg_confidence])

        return merged_results

    def get_annotated_image(self, image_path, results):
        """Draw bounding boxes and text on the image and return it."""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")

        for detection in results:
            p0 = tuple(map(int, detection[0][0]))
            p1 = tuple(map(int, detection[0][2]))
            text = detection[1]
            cv2.rectangle(img, p0, p1, (0, 255, 0), 2)
            # Optionally add text labeling on the image
#            cv2.putText(img, text, (p0[0], p0[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        return img

    def visualize_results(self, image_path, results):
        """Display the annotated image."""
        for detection in results:
            conf = detection[2] if len(detection) > 2 else 0.0
            print(f"[{conf:.2f}] {detection[1]}")

        img = self.get_annotated_image(image_path, results)
        cv2.imshow("Text Detection - EasyOCR", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def main():
    """Main function for EasyOCR text detection."""
    parser = argparse.ArgumentParser(description="EasyOCR Text Detection Script")
    parser.add_argument("image_path", help="Path to the image file")
    parser.add_argument("--output", help="Path to save the JSON results")
    parser.add_argument("--gap", type=int, default=1, help="Minimum distance between boxes to merge (default: 10)")
    parser.add_argument("--langs", nargs="+", default=["en"], help="Languages for OCR (default: en)")
    
    args = parser.parse_args()

    try:
        detector = TextDetection(languages=args.langs)
        results = detector.detect_text(args.image_path)

        if args.gap > 0:
            results = detector.merge_boxes(results, gap=args.gap)
            
        if args.output:
            detector.save_results_to_json(results, args.output)
            print(f"Results saved to {args.output}")

        detector.visualize_results(args.image_path, results)

    except Exception as e:
        print(f"Error during OCR processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
