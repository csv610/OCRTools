import sys

import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor

PROMPTS = {
    "ocr": "OCR:",
    "table": "Table Recognition:",
    "formula": "Formula Recognition:",
    "chart": "Chart Recognition:",
}


def main():
    image_path = sys.argv[1]
    model_path = "PaddlePaddle/PaddleOCR-VL"
    task = "ocr"

    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    image = Image.open(image_path).convert("RGB")

    model = AutoModelForCausalLM.from_pretrained(
        model_path, trust_remote_code=True, torch_dtype=torch.bfloat16
    ).to(DEVICE).eval()
    processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)

    messages = [
        {"role": "user",
         "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": PROMPTS[task]},
            ]
        }
    ]
    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt"
    ).to(DEVICE)

    outputs = model.generate(**inputs, max_new_tokens=1024)
    outputs = processor.batch_decode(outputs, skip_special_tokens=True)[0]
    print(outputs)


if __name__ == "__main__":
    main()
