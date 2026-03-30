# ⚖️ LexRAG — Legal Document AI Assistant

A RAG (Retrieval-Augmented Generation) app built for law firms to analyse legal documents with AI — fully local vector storage, powered by Hugging Face's free inference API.

---

## Features

| Feature | Description |
|---|---|
| 💬 **Q&A** | Ask questions about uploaded documents and get cited answers |
| 🚨 **Risk Detection** | Automatically flags HIGH / MEDIUM / LOW risk clauses in contracts |
| 🔍 **Document Comparison** | Side-by-side comparison of two documents with gap and conflict analysis |

---

## Tech Stack

- **UI** — Streamlit
- **LLM** — Hugging Face Inference API (Qwen2.5-7B-Instruct, free)
- **Embeddings** — Sentence Transformers (all-MiniLM-L6-v2, runs locally)
- **Vector Store** — ChromaDB (local, persistent)
- **Document Parsing** — pdfplumber (PDF), python-docx (DOCX), plain text

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/SofeeSekar/legal-rag.git
cd legal-rag
```

### 2. Create a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get a free Hugging Face token
1. Sign up at [huggingface.co](https://huggingface.co) (free, no credit card)
2. Go to **Settings → Access Tokens → New Token** (Read access)
3. Copy the token

### 5. Create your `.env` file
```bash
cp .env.example .env
```
Then open `.env` and add your token:
```
HF_TOKEN=hf_your_token_here
```

### 6. Run the app
```bash
.venv\Scripts\streamlit run app.py   # Windows
streamlit run app.py                 # Mac/Linux
```

Open your browser at **http://localhost:8501**

---

## Usage

1. **Upload documents** using the sidebar (PDF, DOCX, or TXT)
2. Documents are indexed automatically and stored locally
3. Use the three tabs:
   - **Q&A** — ask anything about your documents
   - **Risk Detection** — select a contract and scan for risky clauses
   - **Compare Documents** — select two documents to compare

---

## Privacy

- All document embeddings are stored **locally** on your machine
- Only the query + relevant text chunks are sent to Hugging Face for inference
- Your `.env` file and vector database are excluded from version control
