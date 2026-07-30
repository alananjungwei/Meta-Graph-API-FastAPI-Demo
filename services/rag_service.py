import os

from dotenv import load_dotenv
from openai import OpenAI

from rag.prompt_builder import build_prompt
from rag.retriever import retrieve

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_reply(
    sender_id: str,
    text: str,
    intent: str,
    sentiment: str,
) -> str:
    """
    Retrieve relevant knowledge base chunks, build a grounded prompt,
    and generate an AI response.
    """

    chunks = retrieve(text)


    system_prompt = build_prompt(chunks)

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": text,
            },
        ],
    )

    return response.choices[0].message.content