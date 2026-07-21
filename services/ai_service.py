from openai import OpenAI

from services.config import OPENAI_API_KEY

client = OpenAI(
    api_key=OPENAI_API_KEY
)


def generate_reply(user_message: str):

    response = client.responses.create(
        model="gpt-5-mini",
        input=[
            {
                "role": "system",
                "content": (
                    "You are a friendly AI assistant. "
                    "Reply politely and keep answers under 80 words."
                ),
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        max_output_tokens=500,
    )

    print("========== OPENAI RESPONSE ==========")
    print(response)
    print("=====================================")

    print("OUTPUT TEXT:")
    print(repr(response.output_text))

    return response.output_text