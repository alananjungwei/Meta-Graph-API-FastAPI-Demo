from loader import load_documents


documents = load_documents()

for document in documents:

    print(document["filename"])

    print(document["content"][:100])

    print("-" * 50)