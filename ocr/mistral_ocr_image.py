import base64
import os
import sys
from mistralai import Mistral

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key=api_key)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

image_path = sys.argv[1]
base64_image = encode_image(image_path)

response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "image_url",
        "image_url": f"data:image/png;base64,{base64_image}" 
    },
    # table_format=None,
    include_image_base64=False
)
print(response.pages[0])
#print(response.pages[0].markdown)
