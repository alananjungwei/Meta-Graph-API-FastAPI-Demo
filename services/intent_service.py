from openai import OpenAI

from services.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def detect_intent(message: str) -> str:
    """
    Classify the user's intent into one category.
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
                    "You are an intent classifier.\n"
                    "Return ONLY one of these labels:\n\n"
                    "- greeting\n"
                    "- product_question\n"
                    "- technical_support\n"
                    "- refund\n"
                    "- complaint\n"
                    "- order_status\n"
                    "- other\n\n"
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

    print("========== INTENT RESPONSE ==========")
    print(response)
    print("=====================================")

    print("OUTPUT TEXT:")
    print(repr(response.output_text))

    return response.output_text.strip().lower()