from rag.retriever import retrieve

query = "Can I return my keyboard after three weeks?"

print(f"\nUser Query: {query}")

results = retrieve(query)

print(f"\nRetrieved {len(results)} relevant chunks.")

print("=" * 70)

for i, chunk in enumerate(results, start=1):

    print(f"\nResult {i}")

    print(f"Source File    : {chunk['filename']}")
    print(f"Chunk ID       : {chunk['chunk_id']}")
    print(f"Vector Distance: {chunk['distance']:.4f}")

    print("\nContent:")
    print(chunk["text"])

    print("=" * 70)