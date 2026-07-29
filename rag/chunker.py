from typing import List


def chunk_documents(documents: List[dict]) -> List[dict]:
    """
    Split each document into paragraph-based chunks.

    Args:
        documents: List of documents returned by loader.py

    Returns:
        List of chunk dictionaries.
    """

    chunks = []

    for document in documents:

        paragraphs = [
            paragraph.strip()
            for paragraph in document["content"].split("\n\n")
            if paragraph.strip()
        ]

        for chunk_id, paragraph in enumerate(paragraphs):

            chunks.append(
                {
                    "filename": document["filename"],
                    "chunk_id": chunk_id,
                    "text": paragraph,
                }
            )

    return chunks