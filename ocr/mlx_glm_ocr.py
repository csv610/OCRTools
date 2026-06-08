import sys

from mlx_vlm import generate, load
from mlx_vlm.prompt_utils import apply_chat_template


def main():
    model, processor = load("mlx-community/GLM-OCR-bf16")

    prompt = "Text Recognition:"
    formatted_prompt = apply_chat_template(processor, model.config, prompt, num_images=1)

    filename = sys.argv[1]

    result = generate(
        model,
        processor,
        formatted_prompt,
        image=[filename],
        max_tokens=2000,
    )
    print(result.text)


if __name__ == "__main__":
    main()
