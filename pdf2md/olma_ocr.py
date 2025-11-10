"""
Local OCR implementation using Qwen2-VL and olmOCR models.

This module provides OCR functionality using open-source vision-language models.
It's designed for local inference and is experimental - requires significant GPU memory.

EXPERIMENTAL: This is a proof-of-concept implementation. For production use,
consider the mistral_ocr.py API-based approach which is more stable and scalable.
"""

import base64
import logging
import urllib.request
from io import BytesIO
from pathlib import Path
from typing import Optional

import torch
from PIL import Image
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration

try:
    from olmocr.data.renderpdf import render_pdf_to_base64png
    from olmocr.prompts import build_finetuning_prompt
    from olmocr.prompts.anchor import get_anchor_text
except ImportError as e:
    raise ImportError(
        "olmocr package not installed. Install with: pip install olmocr"
    ) from e

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class LocalOCR:
    """Local OCR processor using Qwen2-VL and olmOCR models."""

    def __init__(
        self,
        model_name: str = "allenai/olmOCR-7B-0225-preview",
        processor_name: str = "Qwen/Qwen2-VL-7B-Instruct",
        device: Optional[str] = None,
    ) -> None:
        """
        Initialize the LocalOCR processor.

        Args:
            model_name: HuggingFace model ID for the OCR model
            processor_name: HuggingFace model ID for the processor
            device: Device to run inference on ('cuda' or 'cpu').
                   Auto-detects GPU availability if not specified.

        Raises:
            RuntimeError: If model loading fails
        """
        self.model_name = model_name
        self.processor_name = processor_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        logger.info(f"Loading OCR model: {model_name}")
        logger.info(f"Using device: {self.device}")

        try:
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                model_name, torch_dtype=torch.bfloat16
            ).eval()
            self.processor = AutoProcessor.from_pretrained(processor_name)
            self.model.to(self.device)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Failed to initialize OCR model: {e}") from e

    def process_pdf_page(
        self,
        pdf_path: str,
        page_number: int = 1,
        target_image_dim: int = 1024,
        max_tokens: int = 500,
        temperature: float = 0.8,
    ) -> str:
        """
        Process a single PDF page using OCR.

        Args:
            pdf_path: Path to the PDF file
            page_number: Page number to process (1-indexed)
            target_image_dim: Target longest image dimension in pixels
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            OCR text output from the model

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            RuntimeError: If processing fails
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.info(f"Processing {pdf_path}, page {page_number}")

        try:
            # Render page to image
            logger.debug(f"Rendering PDF page {page_number} to image")
            image_base64 = render_pdf_to_base64png(
                str(pdf_path),
                page_number,
                target_longest_image_dim=target_image_dim,
            )

            # Get anchor text for prompt
            logger.debug("Extracting anchor text for prompt")
            anchor_text = get_anchor_text(
                str(pdf_path),
                page_number,
                pdf_engine="pdfreport",
                target_length=4000,
            )

            # Build prompt and messages
            prompt = build_finetuning_prompt(anchor_text)
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                        },
                    ],
                }
            ]

            # Process inputs
            logger.debug("Preparing model inputs")
            text = self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            main_image = Image.open(BytesIO(base64.b64decode(image_base64)))

            inputs = self.processor(
                text=[text],
                images=[main_image],
                padding=True,
                return_tensors="pt",
            )
            inputs = {key: value.to(self.device) for key, value in inputs.items()}

            # Generate output
            logger.debug("Running model inference")
            output = self.model.generate(
                **inputs,
                temperature=temperature,
                max_new_tokens=max_tokens,
                num_return_sequences=1,
                do_sample=True,
            )

            # Decode output
            prompt_length = inputs["input_ids"].shape[1]
            new_tokens = output[:, prompt_length:]
            text_output = self.processor.tokenizer.batch_decode(
                new_tokens, skip_special_tokens=True
            )

            result = text_output[0] if text_output else ""
            logger.info(f"OCR completed for page {page_number}")
            return result

        except Exception as e:
            logger.error(f"Error processing PDF page: {e}")
            raise RuntimeError(f"Failed to process PDF: {e}") from e


def main() -> None:
    """Run the OCR processor on a sample PDF."""
    logger.info("Starting LocalOCR processor")

    try:
        # Initialize processor
        ocr = LocalOCR()

        # Download sample PDF
        sample_pdf = "./paper.pdf"
        logger.info(f"Downloading sample PDF to {sample_pdf}")
        urllib.request.urlretrieve(
            "https://molmo.allenai.org/paper.pdf", sample_pdf
        )

        # Process first page
        result = ocr.process_pdf_page(sample_pdf, page_number=1)
        logger.info(f"OCR Result: {result}")

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
