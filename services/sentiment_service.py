from openai import OpenAI

from services.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def detect_sentiment(message: str) -> str:
    """
    Classify the sentiment of the user's message.
    """

    response = client.responses.create(
        model="gpt-5-mini",
        reasoning={
        "effort": "minimal"
        },
        input=[
            {
                "role": "system",
                "content": (
                    "You are a sentiment classifier.\n"
                    "Return ONLY one of these labels:\n\n"
                    "- positive\n"
                    "- neutral\n"
                    "- negative\n\n"
                    "Do not explain your answer."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        max_output_tokens=20,
    )

    print("========== SENTIMENT RESPONSE ==========")
    print(response)
    print("========================================")

    print("OUTPUT TEXT:")
    print(repr(response.output_text))

    return response.output_text.strip().lower()