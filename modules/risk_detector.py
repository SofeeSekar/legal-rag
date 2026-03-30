from modules import vector_store, llm_client

SYSTEM = """You are a senior legal risk analyst at a law firm.
Analyse the provided contract excerpts for risky, unusual, or one-sided clauses.

For each risk found, output a block in this exact format:
---
RISK LEVEL: [HIGH / MEDIUM / LOW]
CLAUSE: "<exact quote or paraphrase>"
SOURCE: [filename, Page X]
ISSUE: <what makes this risky>
RECOMMENDATION: <what the lawyer should do>
---

After listing all risks, write a brief overall assessment.
If no risks are found, say so clearly."""

RISK_QUERIES = [
    "termination clause penalty early exit",
    "liability indemnification limitation damages",
    "payment delay interest penalty default",
    "intellectual property ownership assignment",
    "non-compete non-solicitation restrictions",
    "dispute resolution arbitration jurisdiction",
    "confidentiality obligations breach penalty",
    "force majeure exceptions obligations",
    "warranty disclaimer limitation",
    "auto-renewal lock-in period",
]

def detect_risks(doc_ids: list[str]) -> str:
    """Retrieve relevant chunks and analyse for legal risks."""
    seen, chunks = set(), []
    for query in RISK_QUERIES:
        for c in vector_store.search(query, n_results=3, doc_ids=doc_ids):
            key = (c["source"], c["page"])
            if key not in seen:
                seen.add(key)
                chunks.append(c)

    if not chunks:
        return "No document content found. Please upload a contract first."

    context = "\n\n".join(
        f"[Source: {c['source']}, Page {c['page']}]\n{c['text']}"
        for c in chunks
    )
    user_prompt = f"Contract excerpts to analyse:\n\n{context}"
    return llm_client.ask(SYSTEM, user_prompt, max_tokens=8192)
