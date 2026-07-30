from retriever import retrieve

results = retrieve(
    "Can I return my keyboard after three weeks?"
)

for i, chunk in enumerate(results, start=1):

    print(f"\nResult {i}")

    print(f"Source: {chunk['filename']}")

    print(f"Chunk: {chunk['chunk_id']}")

    print(f"Distance: {chunk['distance']:.4f}")

    print(chunk["text"])

    print("-" * 60)