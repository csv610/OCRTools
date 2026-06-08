import pytest

from ocr.easy_ocr import TextDetection


class TestTextDetection:
    def test_init_default_languages(self):
        detector = TextDetection()
        assert detector.reader is not None

    def test_init_custom_languages(self):
        detector = TextDetection(languages=["en", "fr"])
        assert detector.reader is not None

    def test_detect_text_file_not_found(self):
        detector = TextDetection()
        with pytest.raises(FileNotFoundError, match="not found"):
            detector.detect_text("/nonexistent/image.png")

    def test_merge_boxes_empty(self):
        detector = TextDetection()
        result = detector.merge_boxes([], gap=1)
        assert result == []

    def test_merge_boxes_single(self):
        detector = TextDetection()
        boxes = [([[[0, 0], [10, 0], [10, 10], [0, 10]]], "hello", 0.9)]
        result = detector.merge_boxes(boxes, gap=1)
        assert len(result) == 1
        assert result[0][1] == "hello"
