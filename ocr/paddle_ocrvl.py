
from PIL import Image
import torch
import sys
from transformers import AutoModelForCausalLM, AutoProcessor

image_path = sys.argv[1]

model_path = "PaddlePaddle/PaddleOCR-VL"
task = "ocr" # Options: 'ocr' | 'table' | 'chart' | 'formula'
# ------------------

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

PROMPTS = {
    "ocr": "OCR:",
    "table": "Table Recognition:",
    "formula": "Formula Recognition:",
    "chart": "Chart Recognition:",
}

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
print( "Debug ...", DEVICE)
inputs = processor.apply_chat_template(
    messages, 
    tokenize=True, 
    add_generation_prompt=True, 	
    return_dict=True,
    return_tensors="pt"
).to(DEVICE)
print( "Debug ...")

outputs = model.generate(**inputs, max_new_tokens=1024)
print( "Debug ...")
outputs = processor.batch_decode(outputs, skip_special_tokens=True)[0]
print( "Debug ...")
print(outputs)

