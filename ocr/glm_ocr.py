import sys

from ollama import chat


def main():
    path = sys.argv[1]

    response = chat(
        model="glm-ocr",
        stream=False,
        messages=[
            {
                "role": "user",
                "content": (
                    "Extract the text from the image. "
                    "Do not repeat content. Stop when finished."
                ),
                "images": [path],
            }
        ],
        options={
            "temperature": 0.00
        },
    )

    raw = response["message"]["content"]
    print(raw)


if __name__ == "__main__":
    main()
