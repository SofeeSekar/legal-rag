from modules import vector_store, llm_client

SYSTEM = """You are a precise legal assistant for a law firm.
Answer questions using ONLY the provided document excerpts.
Always cite your sources like: [Source: filename, Page X]
If the answer is not in the excerpts, say so clearly — do not guess.
Flag any legal ambiguities or risks you notice in passing."""

def answer(question: str, doc_ids: list[str] | None = None) -> tuple[str, list[dict]]:
    """Return (answer, source_chunks)."""
    chunks = vector_store.search(question, n_results=6, doc_ids=doc_ids)
    if not chunks:
        return "No relevant content found. Please upload documents first.", []

    context = "\n\n".join(
        f"[Source: {c['source']}, Page {c['page']}]\n{c['text']}"
        for c in chunks
    )
    user_prompt = f"Document excerpts:\n\n{context}\n\n---\nQuestion: {question}"
    answer_text = llm_client.ask(SYSTEM, user_prompt)
    return answer_text, chunks
