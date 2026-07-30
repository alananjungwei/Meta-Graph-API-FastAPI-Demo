import os

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

chroma_client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = chroma_client.get_collection(
    name="knowledge_base"
)


def retrieve(query: str, n_results: int = 3):
    """
    Retrieve the most relevant chunks for a user query.

    Returns:
        List of dictionaries.
    """

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query,
    )

    query_embedding = response.data[0].embedding

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    retrieved_chunks = []

    documents = results["documents"][0]
    metadata = results["metadatas"][0]
    distances = results["distances"][0]

    for document, meta, distance in zip(
        documents,
        metadata,
        distances,
    ):

        retrieved_chunks.append(
            {
                "text": document,
                "filename": meta["filename"],
                "chunk_id": meta["chunk_id"],
                "distance": distance,
            }
        )

    return retrieved_chunks