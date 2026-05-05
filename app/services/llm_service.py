from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

LLM_MODEL = "llama-3.1-8b-instant"


def build_prompt(question: str, chunks: list[dict]) -> str:
    """
    Build a RAG prompt by combining the question with retrieved chunks.
    
    The prompt instructs the LLM to:
    1. Answer ONLY from the provided context
    2. Admit when it doesn't know
    3. Be concise and accurate
    """
    # Format chunks into readable context
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Source {i} - Page {chunk['page_number']}]\n{chunk['content']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""You are a helpful assistant that answers questions based strictly on the provided document context.

RULES:
- Answer ONLY using information from the context below
- If the answer is not in the context, say "I don't have enough information in the provided documents to answer this."
- Be concise and accurate
- Do not make up or infer information not present in the context

CONTEXT:
---
{context}
---

QUESTION: {question}

ANSWER:"""

    return prompt


def generate_answer(question: str, chunks: list[dict]) -> dict:
    """
    Send question + retrieved chunks to Groq LLM and get an answer.
    
    Returns dict with answer and metadata.
    """
    if not chunks:
        return {
            "answer": "No relevant documents found to answer your question.",
            "model": LLM_MODEL,
            "tokens_used": 0
        }

    prompt = build_prompt(question, chunks)

    print(f"🤖 Sending to LLM: {LLM_MODEL}")
    print(f"   Chunks used: {len(chunks)}")
    print(f"   Question: {question}")

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a precise document assistant. Answer only from provided context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,      # low temperature = more focused, less creative
        max_tokens=1024,      # max length of answer
    )

    answer = response.choices[0].message.content.strip()
    tokens_used = response.usage.total_tokens

    print(f"✅ Answer generated ({tokens_used} tokens used)")

    return {
        "answer": answer,
        "model": LLM_MODEL,
        "tokens_used": tokens_used
    }