import os

from dotenv import load_dotenv
from openai import OpenAI

from rag.retriever import retrieve

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def answer_question(user_question: str):

    chunks = retrieve(user_question)

    context = "\n\n".join(
        chunk["text"]
        for chunk in chunks
    )

    system_prompt = f"""
You are NovaTech Electronics' AI customer support assistant.

Answer ONLY using the provided company information.

If the information is unavailable,
say you cannot find it in the knowledge base.

Company Information:

{context}
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_question,
            },
        ],
    )

    return response.choices[0].message.content