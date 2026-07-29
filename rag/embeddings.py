from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_embeddings(chunks):
    """
    Generate embeddings for each text chunk.

    Args:
        chunks (list): List of chunk dictionaries.

    Returns:
        list: Chunk dictionaries with embeddings added.
    """

    embedded_chunks = []

    for chunk in chunks:

        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=chunk["text"],
        )

        embedding = response.data[0].embedding

        embedded_chunks.append(
            {
                **chunk,
                "embedding": embedding,
            }
        )

    return embedded_chunks