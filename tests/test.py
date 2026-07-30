from rag.loader import load_documents
from rag.chunker import chunk_documents

documents = load_documents()

chunks = chunk_documents(documents)

print(f"Loaded {len(documents)} documents.")
print(f"Created {len(chunks)} chunks.\n")

for chunk in chunks[:5]:
    print(chunk)
    print("-" * 60)