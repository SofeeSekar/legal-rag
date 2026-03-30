from modules import vector_store, llm_client

SYSTEM = """You are a legal document comparison expert.
You will be given excerpts from two legal documents (Document A and Document B).
Compare them thoroughly and produce a structured report:

1. KEY DIFFERENCES — list each material difference with quotes from both docs
2. MISSING CLAUSES — clauses present in one document but absent in the other
3. CONFLICTING TERMS — terms that directly contradict each other
4. RISK ASSESSMENT — which document is more favourable, and why
5. RECOMMENDATIONS — specific actions the lawyer should take

Always cite sources: [Doc A: filename, Page X] or [Doc B: filename, Page X]."""

COMPARISON_QUERIES = [
    "payment terms conditions",
    "termination clause",
    "liability indemnification",
    "intellectual property rights",
    "confidentiality obligations",
    "dispute resolution",
    "warranties representations",
    "obligations responsibilities parties",
]

def compare(doc_id_a: str, doc_id_b: str) -> str:
    """Compare two documents and return analysis."""
    seen_a, seen_b = set(), set()
    chunks_a, chunks_b = [], []

    for query in COMPARISON_QUERIES:
        for c in vector_store.search(query, n_results=2, doc_ids=[doc_id_a]):
            key = (c["source"], c["page"])
            if key not in seen_a:
                seen_a.add(key)
                chunks_a.append(c)
        for c in vector_store.search(query, n_results=2, doc_ids=[doc_id_b]):
            key = (c["source"], c["page"])
            if key not in seen_b:
                seen_b.add(key)
                chunks_b.append(c)

    if not chunks_a or not chunks_b:
        return "Could not retrieve content from one or both documents."

    context_a = "\n\n".join(f"[Doc A: {c['source']}, Page {c['page']}]\n{c['text']}" for c in chunks_a)
    context_b = "\n\n".join(f"[Doc B: {c['source']}, Page {c['page']}]\n{c['text']}" for c in chunks_b)

    user_prompt = f"DOCUMENT A EXCERPTS:\n\n{context_a}\n\n{'='*60}\n\nDOCUMENT B EXCERPTS:\n\n{context_b}"
    return llm_client.ask(SYSTEM, user_prompt, max_tokens=8192)
