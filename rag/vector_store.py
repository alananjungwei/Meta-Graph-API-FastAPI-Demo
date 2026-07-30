import chromadb

client = chromadb.PersistentClient(path="chroma_db")

COLLECTION_NAME = "knowledge_base"

try:
    client.delete_collection(COLLECTION_NAME)
except Exception:
    pass

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


def store_embeddings(embedded_chunks):
    """
    Store embedded chunks in ChromaDB.
    """

    for chunk in embedded_chunks:

        collection.add(
            ids=[
                f"{chunk['filename']}_{chunk['chunk_id']}"
            ],
            embeddings=[
                chunk["embedding"]
            ],
            documents=[
                chunk["text"]
            ],
            metadatas=[
                {
                    "filename": chunk["filename"],
                    "chunk_id": chunk["chunk_id"],
                }
            ]
        )

    print(f"Stored {len(embedded_chunks)} chunks.")