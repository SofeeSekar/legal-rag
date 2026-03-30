import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

from modules import document_loader, vector_store, qa, risk_detector, comparator

st.set_page_config(page_title="LexRAG — Legal Document AI", page_icon="⚖️", layout="wide")

# ── Sidebar: Document Management ─────────────────────────────────────────────
with st.sidebar:
    st.title("⚖️ LexRAG")
    st.caption("Legal Document Intelligence")
    st.divider()

    st.subheader("Upload Documents")
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
                st.info(f"Already indexed: {uf.name}")
                continue
            with st.spinner(f"Indexing {uf.name}…"):
                suffix = os.path.splitext(uf.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uf.read())
                    tmp_path = tmp.name
                try:
                    pages = document_loader.load_document(tmp_path)
                    chunks = document_loader.chunk_pages(pages)
                    vector_store.add_document(chunks, doc_id=doc_id)
                    st.success(f"Indexed: {uf.name} ({len(chunks)} chunks)")
                except Exception as e:
                    st.error(f"Failed to index {uf.name}: {e}")
                finally:
                    os.unlink(tmp_path)

    st.divider()
    st.subheader("Indexed Documents")
    docs = vector_store.list_documents()
    if docs:
        for doc in docs:
            col1, col2 = st.columns([4, 1])
            col1.markdown(f"📄 `{doc}`")
            if col2.button("🗑️", key=f"del_{doc}", help=f"Delete {doc}"):
                vector_store.delete_document(doc)
                st.rerun()
    else:
        st.caption("No documents indexed yet.")

# ── Main Area: Feature Tabs ───────────────────────────────────────────────────
st.title("Legal Document AI Assistant")

if not docs:
    st.info("Upload legal documents using the sidebar to get started.")
    st.stop()

tab_qa, tab_risk, tab_compare = st.tabs(["💬 Q&A", "🚨 Risk Detection", "🔍 Compare Documents"])

# ── Tab 1: Q&A ────────────────────────────────────────────────────────────────
with tab_qa:
    st.subheader("Ask a Question")
    st.caption("Ask anything about your uploaded documents. Answers include source citations.")

    scope = st.multiselect(
        "Search within (leave empty for all documents):",
        options=docs,
        default=[],
        key="qa_scope"
    )
    question = st.text_input("Your question:", placeholder="What are the termination conditions in the contract?")

    if st.button("Ask", type="primary", key="ask_btn") and question.strip():
        with st.spinner("Retrieving and analysing…"):
            answer, sources = qa.answer(question, doc_ids=scope if scope else None)
        st.markdown("### Answer")
        st.markdown(answer)
        if sources:
            with st.expander("📎 Source Excerpts"):
                for c in sources:
                    st.markdown(f"**{c['source']} — Page {c['page']}** (score: {c['score']:.2f})")
                    st.text(c["text"][:400] + ("…" if len(c["text"]) > 400 else ""))
                    st.divider()

# ── Tab 2: Risk Detection ─────────────────────────────────────────────────────
with tab_risk:
    st.subheader("Contract Risk Analysis")
    st.caption("Automatically flags risky, unusual, or one-sided clauses in contracts.")

    risk_docs = st.multiselect(
        "Select document(s) to analyse:",
        options=docs,
        default=docs[:1] if docs else [],
        key="risk_docs"
    )

    if st.button("Analyse Risks", type="primary", key="risk_btn"):
        if not risk_docs:
            st.warning("Select at least one document.")
        else:
            with st.spinner("Running risk analysis… (this may take a moment)"):
                report = risk_detector.detect_risks(doc_ids=risk_docs)
            st.markdown("### Risk Report")
            st.markdown(report)

# ── Tab 3: Document Comparison ────────────────────────────────────────────────
with tab_compare:
    st.subheader("Compare Two Documents")
    st.caption("Side-by-side legal comparison: differences, missing clauses, and recommendations.")

    if len(docs) < 2:
        st.warning("Upload at least two documents to use comparison.")
    else:
        col_a, col_b = st.columns(2)
        doc_a = col_a.selectbox("Document A:", options=docs, key="doc_a")
        doc_b = col_b.selectbox("Document B:", options=[d for d in docs if d != doc_a], key="doc_b")

        if st.button("Compare", type="primary", key="compare_btn"):
            with st.spinner("Comparing documents… (this may take a moment)"):
                report = comparator.compare(doc_a, doc_b)
            st.markdown("### Comparison Report")
            st.markdown(report)
