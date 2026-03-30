import streamlit as st
import os, tempfile
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)

from modules import document_loader, vector_store, qa, risk_detector, comparator, summarizer, exporter

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LexRAG — Legal AI Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Dark legal theme */
[data-testid="stAppViewContainer"] { background: #0d0d1a; }
[data-testid="stSidebar"] { background: #080812 !important; border-right: 1px solid #1e1e3a; }
[data-testid="stSidebar"] * { color: #c8c8e8 !important; }

/* Header */
.lex-header {
    background: linear-gradient(135deg, #1a1a3e 0%, #0d0d1a 100%);
    border: 1px solid #2a2a5a; border-radius: 16px;
    padding: 28px 32px; margin-bottom: 24px;
    display: flex; align-items: center; gap: 20px;
}
.lex-logo { font-size: 2.5rem; }
.lex-title { color: #ffffff; font-size: 1.8rem; font-weight: 800; margin: 0; }
.lex-subtitle { color: #8888bb; font-size: 0.9rem; margin: 4px 0 0 0; }

/* Cards */
.doc-card {
    background: #12122a; border: 1px solid #2a2a5a;
    border-radius: 12px; padding: 16px; margin-bottom: 12px;
}
.doc-card h4 { color: #a0a0ff; margin: 0 0 6px 0; font-size: 0.9rem; }
.doc-card p  { color: #6666aa; margin: 0; font-size: 0.8rem; }

/* Chat messages */
.chat-user {
    background: linear-gradient(135deg, #1e1e4a, #1a1a3e);
    border: 1px solid #3a3a7a; border-radius: 12px 12px 4px 12px;
    padding: 14px 18px; margin: 8px 0; color: #e0e0ff;
    margin-left: 20%;
}
.chat-ai {
    background: #12122a; border: 1px solid #2a2a5a;
    border-radius: 12px 12px 12px 4px;
    padding: 14px 18px; margin: 8px 0; color: #c8c8e8;
    margin-right: 20%;
}
.chat-label { font-size: 0.72rem; font-weight: 700; letter-spacing: 1px; margin-bottom: 6px; }
.chat-label.user { color: #7070ff; text-align: right; }
.chat-label.ai   { color: #5555aa; }

/* Risk badges */
.risk-high   { background:#3a0a0a; border:1px solid #aa2222; color:#ff6666; padding:4px 12px; border-radius:20px; font-size:0.78rem; font-weight:700; }
.risk-medium { background:#3a2a0a; border:1px solid #aa7722; color:#ffaa44; padding:4px 12px; border-radius:20px; font-size:0.78rem; font-weight:700; }
.risk-low    { background:#0a2a1a; border:1px solid #227744; color:#44cc88; padding:4px 12px; border-radius:20px; font-size:0.78rem; font-weight:700; }

/* Summary card */
.summary-card {
    background: #0f0f24; border: 1px solid #2a2a5a;
    border-left: 4px solid #5555ff; border-radius: 12px;
    padding: 20px; margin: 12px 0; color: #c8c8e8; line-height: 1.8;
}

/* Metric cards */
.metric-row { display: flex; gap: 12px; margin-bottom: 20px; }
.metric-card {
    flex: 1; background: #12122a; border: 1px solid #2a2a5a;
    border-radius: 10px; padding: 14px; text-align: center;
}
.metric-num { font-size: 1.6rem; font-weight: 800; color: #7070ff; display: block; }
.metric-lbl { font-size: 0.72rem; color: #6666aa; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #4444cc, #6666ff) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #224422, #336633) !important;
    color: #88ff88 !important; border: 1px solid #336633 !important;
    border-radius: 8px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: #12122a; border-radius: 10px; padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px !important; color: #8888bb !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg,#3333aa,#5555cc) !important; color:white !important; }

/* Expander */
[data-testid="stExpander"] { background: #12122a; border: 1px solid #2a2a5a; border-radius: 10px; }

/* Input */
.stTextInput input, .stTextArea textarea {
    background: #12122a !important; border: 1px solid #2a2a5a !important;
    color: #e0e0ff !important; border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="lex-header">
  <div class="lex-logo">⚖️</div>
  <div>
    <p class="lex-title">LexRAG</p>
    <p class="lex-subtitle">AI-Powered Legal Document Assistant · Private & Secure</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── INIT SESSION STATE ─────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "doc_summaries" not in st.session_state:
    st.session_state.doc_summaries = {}

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Upload Documents")
    uploaded_files = st.file_uploader(
        "PDF, DOCX, or TXT",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        for uf in uploaded_files:
            doc_id = uf.name
            if vector_store.document_exists(doc_id):
                st.info(f"✓ Already indexed: {uf.name}", icon="📄")
                continue
            with st.spinner(f"Indexing & summarising {uf.name}…"):
                suffix = os.path.splitext(uf.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uf.read())
                    tmp_path = tmp.name
                try:
                    pages = document_loader.load_document(tmp_path)
                    chunks = document_loader.chunk_pages(pages)
                    vector_store.add_document(chunks, doc_id=doc_id)
                    # Auto-summarise
                    summary = summarizer.summarise(chunks)
                    st.session_state.doc_summaries[doc_id] = summary
                    st.success(f"✓ Indexed: {uf.name}")
                except Exception as e:
                    st.error(f"Failed: {e}")
                finally:
                    os.unlink(tmp_path)

    st.markdown("---")
    st.markdown("### 📚 Indexed Documents")
    docs = vector_store.list_documents()
    if docs:
        for doc in docs:
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"📄 `{doc}`")
            if c2.button("✕", key=f"del_{doc}", help=f"Delete {doc}"):
                vector_store.delete_document(doc)
                if doc in st.session_state.doc_summaries:
                    del st.session_state.doc_summaries[doc]
                st.rerun()

        # Metrics
        st.markdown("---")
        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-card"><span class="metric-num">{len(docs)}</span><span class="metric-lbl">Documents</span></div>
          <div class="metric-card"><span class="metric-num">{len(st.session_state.chat_history)}</span><span class="metric-lbl">Messages</span></div>
        </div>""", unsafe_allow_html=True)

        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
    else:
        st.caption("No documents indexed yet. Upload files above.")

# ── MAIN CONTENT ──────────────────────────────────────────────────────────────
docs = vector_store.list_documents()
if not docs:
    st.markdown("""
    <div style='text-align:center; padding: 80px 20px; color: #6666aa;'>
        <div style='font-size: 4rem; margin-bottom: 20px;'>📂</div>
        <h2 style='color: #8888cc;'>Upload your first document</h2>
        <p>Drag and drop PDF, DOCX or TXT files into the sidebar to get started.</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

tab_chat, tab_summary, tab_risk, tab_compare = st.tabs([
    "💬 Chat with Documents",
    "📋 Document Summaries",
    "🚨 Risk Detection",
    "🔍 Compare Documents"
])

# ── TAB 1: CHAT ───────────────────────────────────────────────────────────────
with tab_chat:
    # Scope selector
    scope = st.multiselect(
        "Search within (leave empty for all):",
        options=docs, default=[],
        placeholder="All documents…"
    )

    # Chat history display
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div style='text-align:center; padding:40px; color:#5555aa;'>
                <div style='font-size:2rem;'>💬</div>
                <p>Ask anything about your documents.<br/>
                <small>e.g. "What are the termination conditions?" · "Who are the parties?" · "What is the payment schedule?"</small></p>
            </div>""", unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class='chat-label user'>YOU</div>
                <div class='chat-user'>{msg['content']}</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='chat-label ai'>⚖️ LEXRAG</div>
                <div class='chat-ai'>{msg['content']}</div>""", unsafe_allow_html=True)

    # Input
    col_q, col_btn = st.columns([6, 1])
    with col_q:
        question = st.text_input("Ask a question:", placeholder="e.g. What are the termination conditions?", label_visibility="collapsed")
    with col_btn:
        ask_btn = st.button("Ask →", type="primary", use_container_width=True)

    if ask_btn and question.strip():
        with st.spinner("Thinking…"):
            answer, sources = qa.answer(question, doc_ids=scope if scope else None)
        st.session_state.chat_history.append({"role": "user", "content": question})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

        if sources:
            with st.expander("📎 View Source Excerpts"):
                for c in sources:
                    st.markdown(f"**{c['source']} — Page {c['page']}** (relevance: {c['score']:.0%})")
                    st.caption(c["text"][:400] + ("…" if len(c["text"]) > 400 else ""))
                    st.divider()
        st.rerun()

    # Export chat
    if st.session_state.chat_history:
        st.markdown("---")
        col_pdf, col_word = st.columns(2)
        chat_text = "\n\n".join(
            f"{'Q' if m['role']=='user' else 'A'}: {m['content']}"
            for m in st.session_state.chat_history
        )
        sections = [{"title": "Q&A Conversation", "content": chat_text}]
        with col_pdf:
            pdf_bytes = exporter.export_pdf("Legal Document Q&A Session", sections)
            st.download_button("⬇️ Export Chat as PDF", pdf_bytes, "lexrag_chat.pdf", "application/pdf", use_container_width=True)
        with col_word:
            word_bytes = exporter.export_word("Legal Document Q&A Session", sections)
            st.download_button("⬇️ Export Chat as Word", word_bytes, "lexrag_chat.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

# ── TAB 2: SUMMARIES ──────────────────────────────────────────────────────────
with tab_summary:
    st.markdown("#### Auto-generated document summaries")
    if not st.session_state.doc_summaries:
        st.info("Summaries are generated automatically when you upload documents. Re-upload your documents to get summaries.")
    for doc_id, summary in st.session_state.doc_summaries.items():
        st.markdown(f"**📄 {doc_id}**")
        st.markdown(f"<div class='summary-card'>{summary}</div>", unsafe_allow_html=True)
        col_pdf, col_word = st.columns([1, 1])
        sections = [{"title": f"Summary: {doc_id}", "content": summary}]
        with col_pdf:
            pdf_bytes = exporter.export_pdf(f"Document Summary: {doc_id}", sections)
            st.download_button("⬇️ PDF", pdf_bytes, f"summary_{doc_id}.pdf", "application/pdf", key=f"pdf_{doc_id}")
        with col_word:
            word_bytes = exporter.export_word(f"Document Summary: {doc_id}", sections)
            st.download_button("⬇️ Word", word_bytes, f"summary_{doc_id}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"word_{doc_id}")
        st.markdown("---")

    # Manual re-summarise
    st.markdown("#### Re-summarise a document")
    sel = st.selectbox("Select document:", options=docs, key="sum_sel")
    if st.button("Generate Summary", type="primary"):
        with st.spinner("Summarising…"):
            from modules import vector_store as vs
            chunks = vs.search("summary overview purpose parties", n_results=10, doc_ids=[sel])
            summary = summarizer.summarise(chunks)
            st.session_state.doc_summaries[sel] = summary
        st.rerun()

# ── TAB 3: RISK DETECTION ─────────────────────────────────────────────────────
with tab_risk:
    st.markdown("#### Contract Risk Analysis")
    st.caption("Automatically scans for HIGH / MEDIUM / LOW risk clauses.")
    risk_docs = st.multiselect("Select document(s):", options=docs, default=docs[:1], key="risk_docs")

    if st.button("🔍 Run Risk Analysis", type="primary"):
        if not risk_docs:
            st.warning("Select at least one document.")
        else:
            with st.spinner("Scanning for risks… (this may take 20-30 seconds)"):
                report = risk_detector.detect_risks(doc_ids=risk_docs)
            st.session_state["risk_report"] = report

    if "risk_report" in st.session_state:
        st.markdown(st.session_state["risk_report"])
        st.markdown("---")
        col_pdf, col_word = st.columns(2)
        sections = [{"title": "Risk Analysis Report", "content": st.session_state["risk_report"]}]
        with col_pdf:
            pdf_bytes = exporter.export_pdf("Contract Risk Report", sections)
            st.download_button("⬇️ Export as PDF", pdf_bytes, "risk_report.pdf", "application/pdf", use_container_width=True)
        with col_word:
            word_bytes = exporter.export_word("Contract Risk Report", sections)
            st.download_button("⬇️ Export as Word", word_bytes, "risk_report.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

# ── TAB 4: COMPARE ────────────────────────────────────────────────────────────
with tab_compare:
    st.markdown("#### Compare Two Documents")
    st.caption("Side-by-side comparison — differences, missing clauses, conflicts, and recommendations.")
    if len(docs) < 2:
        st.warning("Upload at least two documents to use comparison.")
    else:
        col_a, col_b = st.columns(2)
        doc_a = col_a.selectbox("Document A:", options=docs, key="doc_a")
        doc_b = col_b.selectbox("Document B:", options=[d for d in docs if d != doc_a], key="doc_b")

        if st.button("🔍 Compare Documents", type="primary"):
            with st.spinner("Comparing… (this may take 30 seconds)"):
                report = comparator.compare(doc_a, doc_b)
            st.session_state["compare_report"] = report

        if "compare_report" in st.session_state:
            st.markdown(st.session_state["compare_report"])
            st.markdown("---")
            col_pdf, col_word = st.columns(2)
            sections = [{"title": f"Comparison: {doc_a} vs {doc_b}", "content": st.session_state["compare_report"]}]
            with col_pdf:
                pdf_bytes = exporter.export_pdf("Document Comparison Report", sections)
                st.download_button("⬇️ Export as PDF", pdf_bytes, "comparison_report.pdf", "application/pdf", use_container_width=True)
            with col_word:
                word_bytes = exporter.export_word("Document Comparison Report", sections)
                st.download_button("⬇️ Export as Word", word_bytes, "comparison_report.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
