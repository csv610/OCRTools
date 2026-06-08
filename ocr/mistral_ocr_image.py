import base64
import os
import sys

from mistralai import Mistral


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def main():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("Error: MISTRAL_API_KEY environment variable is not set.")
        sys.exit(1)

    client = Mistral(api_key=api_key)

    image_path = sys.argv[1]
    base64_image = encode_image(image_path)

    response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "image_url",
            "image_url": f"data:image/png;base64,{base64_image}"
        },
        include_image_base64=False
    )
    print(response.pages[0])


if __name__ == "__main__":
    main()
