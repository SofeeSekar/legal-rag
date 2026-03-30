from modules import llm_client

SYSTEM = """You are a legal document analyst.
When given document content, produce a concise structured summary:

**Document Type:** (e.g. Employment Contract, NDA, Service Agreement, etc.)
**Parties Involved:** (who are the parties)
**Key Purpose:** (1-2 sentences on what this document is about)
**Main Terms:** (bullet points of the most important clauses)
**Important Dates/Deadlines:** (if any)
**Red Flags:** (anything that immediately stands out as unusual or important)

Be concise and professional."""

def summarise(chunks: list[dict]) -> str:
    """Generate a summary from document chunks."""
    # Use first ~2000 words for summary
    text = "\n\n".join(c["text"] for c in chunks[:10])
    if len(text) > 4000:
        text = text[:4000] + "\n...[truncated]"
    return llm_client.ask(SYSTEM, f"Document content:\n\n{text}", max_tokens=1024)
