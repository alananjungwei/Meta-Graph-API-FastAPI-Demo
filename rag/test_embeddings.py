from loader import load_documents
from chunker import chunk_documents
from embeddings import generate_embeddings

documents = load_documents()

chunks = chunk_documents(documents)

embedded_chunks = generate_embeddings(chunks)

print(f"Created embeddings for {len(embedded_chunks)} chunks.\n")

print(embedded_chunks[0]["filename"])
print(embedded_chunks[0]["chunk_id"])
print(embedded_chunks[0]["text"])

print("\nEmbedding length:")
print(len(embedded_chunks[0]["embedding"]))