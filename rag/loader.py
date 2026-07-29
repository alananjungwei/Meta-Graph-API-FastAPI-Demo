from pathlib import Path


KNOWLEDGE_BASE_PATH = Path("knowledge_base")


def load_documents():
    """
    Load all .txt files from the knowledge base.

    Returns:
        list[dict]
    """

    documents = []

    for file_path in KNOWLEDGE_BASE_PATH.glob("*.txt"):

        with open(file_path, "r", encoding="utf-8") as file:

            documents.append(
                {
                    "filename": file_path.name,
                    "content": file.read(),
                }
            )

    return documents