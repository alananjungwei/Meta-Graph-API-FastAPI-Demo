from openai import OpenAI

from services.config import OPENAI_API_KEY

conversation_memory = {}

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_reply(sender_id: str, text: str):
    """
    Generate an AI reply while remembering previous messages
    from the same Messenger user.
    """

    # Get (or create) this user's conversation history
    history = conversation_memory.setdefault(sender_id, [])

    # Add the latest user message
    history.append(
        {
            "role": "user",
            "content": text,
        }
    )

    # Generate a response
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
            *history,
        ],
        max_output_tokens=500,
    )

    print("========== OPENAI RESPONSE ==========")
    print(response)
    print("=====================================")

    reply = response.output_text

    if not reply or not reply.strip():
        reply = "Sorry, I couldn't generate a response."

    print("OUTPUT TEXT:")
    print(repr(reply))

    # Save the assistant's reply
    history.append(
        {
            "role": "assistant",
            "content": reply,
        }
    )

    print("\n========== CONVERSATION MEMORY ==========")
    for message in history:
        print(message)
    print("=========================================\n")

    return reply