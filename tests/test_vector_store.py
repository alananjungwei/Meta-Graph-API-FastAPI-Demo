from rag.loader import load_documents
from rag.chunker import chunk_documents
from rag.embeddings import generate_embeddings
from rag.vector_store import store_embeddings

documents = load_documents()

chunks = chunk_documents(documents)

embedded_chunks = generate_embeddings(chunks)

store_embeddings(embedded_chunks)