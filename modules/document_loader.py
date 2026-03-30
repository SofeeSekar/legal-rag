import pdfplumber
import docx
import os

def load_document(file_path: str) -> list[dict]:
    """Load a document and return list of {text, page, source} dicts."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return _load_pdf(file_path)
    elif ext == ".docx":
        return _load_docx(file_path)
    elif ext == ".txt":
        return _load_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def _load_pdf(file_path: str) -> list[dict]:
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages.append({"text": text, "page": i + 1, "source": os.path.basename(file_path)})
    return pages

def _load_docx(file_path: str) -> list[dict]:
    doc = docx.Document(file_path)
    chunks = []
    current_chunk = []
    chunk_num = 1
    for para in doc.paragraphs:
        if para.text.strip():
            current_chunk.append(para.text.strip())
        if len(current_chunk) >= 10:
            chunks.append({
                "text": "\n".join(current_chunk),
                "page": chunk_num,
                "source": os.path.basename(file_path)
            })
            current_chunk = []
            chunk_num += 1
    if current_chunk:
        chunks.append({"text": "\n".join(current_chunk), "page": chunk_num, "source": os.path.basename(file_path)})
    return chunks

def _load_txt(file_path: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    lines = text.split("\n")
    chunks, current, chunk_num = [], [], 1
    for line in lines:
        current.append(line)
        if len(current) >= 50:
            chunks.append({"text": "\n".join(current), "page": chunk_num, "source": os.path.basename(file_path)})
            current = []
            chunk_num += 1
    if current:
        chunks.append({"text": "\n".join(current), "page": chunk_num, "source": os.path.basename(file_path)})
    return chunks

def chunk_pages(pages: list[dict], chunk_size: int = 500, overlap: int = 100) -> list[dict]:
    """Split page texts into overlapping chunks for better retrieval."""
    chunks = []
    for page in pages:
        text = page["text"]
        words = text.split()
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk_text = " ".join(words[start:end])
            chunks.append({"text": chunk_text, "page": page["page"], "source": page["source"]})
            start += chunk_size - overlap
    return chunks
