from rag.retriever import retrieve
from rag.prompt_builder import build_prompt

question = "Can I return my keyboard after three weeks?"

chunks = retrieve(question)

prompt = build_prompt(question, chunks)

print(prompt)