from typing import List


def build_prompt(chunks: List[dict]) -> str:
    """
    Build a grounded system prompt using the retrieved knowledge base chunks.
    """

    context = "\n\n".join(
        f"""
========================================
Source: {chunk['filename']}
Chunk ID: {chunk['chunk_id']}
========================================

{chunk['text']}
"""
        for chunk in chunks
    )

    system_prompt = f"""
You are NovaTech Electronics' AI customer support assistant.

Use ONLY the information provided in the knowledge base below to answer the customer's question.

If the retrieved knowledge only partially answers the customer's question,
answer using only the available information and clearly explain which
information is missing.

Never invent policies, prices, procedures, or product details that are
not present in the knowledge base.
--------------------

{context}
"""

    return system_prompt