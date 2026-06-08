import os
from unittest.mock import MagicMock, patch

import pytest

from ocr.mistral_ocr_pdf import MistralOCR


class TestMistralOCR:
    def test_init_missing_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="MISTRAL_API_KEY"):
                MistralOCR()

    def test_init_with_api_key(self):
        with patch.dict(os.environ, {"MISTRAL_API_KEY": "test-key"}, clear=True):
            ocr = MistralOCR()
            assert ocr.client is not None

    def test_validate_pdf_path_missing(self):
        with patch.dict(os.environ, {"MISTRAL_API_KEY": "test-key"}, clear=True):
            ocr = MistralOCR()
            result = ocr._validate_pdf_path("/nonexistent/file.pdf")
            assert result is False

    def test_validate_pdf_path_valid(self, tmp_path):
        pdf = tmp_path / "test.pdf"
        pdf.write_text("fake content")
        with patch.dict(os.environ, {"MISTRAL_API_KEY": "test-key"}, clear=True):
            ocr = MistralOCR()
            result = ocr._validate_pdf_path(str(pdf))
            assert result is True

    @patch.object(MistralOCR, "_encode_pdf")
    def test_extract_io_error(self, mock_encode, tmp_path):
        mock_encode.side_effect = IOError("Simulated I/O error")
        pdf = tmp_path / "test.pdf"
        pdf.write_text("fake")
        with patch.dict(os.environ, {"MISTRAL_API_KEY": "test-key"}, clear=True):
            ocr = MistralOCR()
            result = ocr.extract(str(pdf))
            assert result is False

    def test_get_output_path_default(self, tmp_path):
        pdf = tmp_path / "test.pdf"
        pdf.write_text("fake")
        with patch.dict(os.environ, {"MISTRAL_API_KEY": "test-key"}, clear=True):
            ocr = MistralOCR()
            output_path = ocr._get_output_path(str(pdf), None)
            assert "test" in str(output_path)

    def test_get_output_path_custom(self, tmp_path):
        pdf = tmp_path / "test.pdf"
        pdf.write_text("fake")
        with patch.dict(os.environ, {"MISTRAL_API_KEY": "test-key"}, clear=True):
            ocr = MistralOCR()
            output_path = ocr._get_output_path(str(pdf), "custom_dir")
            assert "custom_dir" in str(output_path)
