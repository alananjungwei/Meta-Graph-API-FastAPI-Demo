from loader import load_documents
from chunker import chunk_documents
from embeddings import generate_embeddings
from vector_store import store_embeddings

documents = load_documents()

chunks = chunk_documents(documents)

embedded_chunks = generate_embeddings(chunks)

store_embeddings(embedded_chunks)