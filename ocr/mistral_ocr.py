import argparse
import base64
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from mistralai import Mistral

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

# Configure logging
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# File handler only
log_file = 'mistral_ocr.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

# Constants
OCR_MODEL = "mistral-ocr-latest"

class MistralOCR:
    """
    A class to handle OCR processing using the Mistral API.
    """
    def __init__(self):
        """
        Initializes the MistralOCR client by retrieving the API key.

        Raises:
            ValueError: If MISTRAL_API_KEY environment variable is not set.
        """
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY environment variable is not set.")
        self.client = Mistral(api_key=api_key)
        logger.info("MistralOCR client initialized successfully")

    def _validate_pdf_path(self, pdf_path: str) -> bool:
        """
        Validates that the PDF path is valid and the file exists.

        Args:
            pdf_path (str): The path to the PDF file.

        Returns:
            bool: True if valid, False otherwise.
        """
        if not os.path.exists(pdf_path):
            logger.error(f"The file '{pdf_path}' was not found.")
            return False

        if not pdf_path.lower().endswith('.pdf'):
            logger.warning(f"File '{pdf_path}' does not have a .pdf extension. Proceeding anyway.")

        return True

    def _encode_pdf(self, pdf_path: str) -> str:
        """
        Encodes a PDF file to a base64 string.

        Args:
            pdf_path (str): The path to the PDF file.

        Returns:
            str: The base64-encoded string of the PDF.

        Raises:
            IOError: If file cannot be read.
        """
        with open(pdf_path, "rb") as pdf_file:
            encoded = base64.b64encode(pdf_file.read()).decode('utf-8')
            logger.info(f"Successfully encoded PDF: {pdf_path}")
            return encoded

    def _get_output_path(self, pdf_path: str, custom_output_dir: Optional[str]) -> Path:
        """
        Determines the output directory path.

        Args:
            pdf_path (str): The path to the input PDF file.
            custom_output_dir (Optional[str]): Custom output directory, if provided.

        Returns:
            Path: The output directory path.
        """
        base_output_dir = Path(__file__).parent.parent / "outputs"

        if custom_output_dir:
            return base_output_dir / custom_output_dir

        pdf_path_obj = Path(pdf_path).resolve()
        return base_output_dir / pdf_path_obj.stem

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
    )
    def _call_ocr_api(self, base64_pdf: str):
        """
        Calls the Mistral OCR API with retry logic.

        Args:
            base64_pdf (str): The base64-encoded PDF content.

        Returns:
            OCR response object.

        Raises:
            Exception: If API call fails after retries.
        """
        logger.info("Calling OCR API...")
        response = self.client.ocr.process(
            model=OCR_MODEL,
            document={
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{base64_pdf}",
            },
            include_image_base64=True,
        )
        logger.info("OCR API call successful")
        return response

    def _save_results(self, output_path: Path, base_filename: str, response) -> bool:
        """
        Saves OCR results (markdown and images) to disk.

        Args:
            output_path (Path): The directory to save files in.
            base_filename (str): The base filename (without extension).
            response: The OCR response object.

        Returns:
            bool: True if successful, False otherwise.

        Raises:
            IOError: If files cannot be written.
        """
        output_path.mkdir(parents=True, exist_ok=True)

        # Write markdown file
        output_filename = output_path / f"{base_filename}.md"
        with open(output_filename, "w", encoding="utf-8") as f:
            for page in response.pages:
                f.write(page.markdown)

        # Save images
        for page in response.pages:
            for image in page.images:
                self._save_image(image, str(output_path))

        logger.info(f"OCR process complete. Output saved to '{output_filename}'")
        return True

    def _save_image(self, image, output_dir: str) -> None:
        """
        Saves a base64-encoded image to a file within the specified directory.

        Args:
            image: The image object from the OCR response.
            output_dir (str): The directory to save the image in.

        Raises:
            IOError: If file cannot be written.
            ValueError: If image data is invalid.
        """
        # Extract base64 data (may be in data URI format or just base64)
        base64_data = image.image_base64
        if isinstance(base64_data, str) and base64_data.startswith("data:"):
            base64_data = base64_data.split(",", 1)[1]

        # Decode and save the image
        image_data = base64.b64decode(base64_data)
        image_path = Path(output_dir) / os.path.basename(image.id)

        image_path.write_bytes(image_data)
        logger.info(f"Successfully saved image: {image.id}")

    def extract(self, pdf_path: str, output_dir: Optional[str] = None) -> bool:
        """
        Processes a PDF document via OCR and saves the results as a markdown file.

        Args:
            pdf_path (str): The path to the input PDF file.
            output_dir (Optional[str]): The directory to save the output files.
                                        If not provided, uses the input PDF's directory
                                        with the filename (without extension) as the subdirectory.

        Returns:
            bool: True if processing was successful, False otherwise.
        """
        if not self._validate_pdf_path(pdf_path):
            return False

        logger.info(f"Processing '{pdf_path}'...")

        try:
            # Encode PDF with retry logic
            base64_pdf = self._encode_pdf(pdf_path)

            # Get output path and base filename
            output_path = self._get_output_path(pdf_path, output_dir)
            base_filename = Path(pdf_path).stem

            # Call OCR API with retry logic
            response = self._call_ocr_api(base64_pdf)

            # Save results with retry logic
            return self._save_results(output_path, base_filename, response)

        except (IOError, OSError) as e:
            logger.error(f"File I/O error after retries: {e}")
            return False
        except Exception as e:
            logger.error(f"An error occurred during OCR processing: {e}")
            return False


def cli():
    """
    Main function for the CLI application.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Process a PDF document using Mistral OCR."
    )
    parser.add_argument(
        "-i", "--pdf-file",
        type=str,
        required=True,
        dest="pdf_file",
        help="The path to the input PDF file."
    )
    parser.add_argument(
        "-d", "--output-dir",
        type=str,
        default=None,
        dest="output_dir",
        help="The directory to save the output files."
    )

    args = parser.parse_args()

    try:
        ocr_processor = MistralOCR()
        success = ocr_processor.extract(args.pdf_file, args.output_dir)

        if success:
            logger.info("Processing completed successfully.")
            return 0
        else:
            logger.error("Processing failed. Please check the logs above for details.")
            return 1

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    cli()
    print( "Completed: " )

