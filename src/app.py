import os
import streamlit as st
from dotenv import load_dotenv

from src.config import GEMINI_MODEL
from src.pipeline import load_all_sections_from_uploads, run_retrieval
from src.answerer import generate_answer
from src.evaluator import evaluate_answer
from src.contradiction_checker import find_contradictions

load_dotenv()

st.set_page_config(page_title="ClauseWise", page_icon="📄", layout="wide")

st.title("📄 ClauseWise")
st.caption("Document Intelligence with QA + Evaluation + Contradiction Detection")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Missing GEMINI_API_KEY in .env")
    st.stop()

if "sections" not in st.session_state:
    st.session_state.sections = []
if "processed" not in st.session_state:
    st.session_state.processed = False

with st.sidebar:
    st.header("Upload Documents")

    uploaded_files = st.file_uploader(
        "Upload TXT files",
        type=["txt"],
        accept_multiple_files=True
    )

    top_k = st.slider("Top sections", 1, 5, 3)

    if st.button("Process Files"):
        if not uploaded_files:
            st.warning("Upload files first")
        else:
            with st.spinner("Processing files..."):
                st.session_state.sections = load_all_sections_from_uploads(uploaded_files)
                st.session_state.processed = True

            st.success(f"Loaded {len(st.session_state.sections)} sections")

tab1, tab2, tab3 = st.tabs(["Ask Questions", "View Sections", "Contradictions"])

# TAB 1 — Ask Questions
with tab1:
    if not st.session_state.processed:
        st.info("Upload and process documents first.")
    else:
        query = st.text_input("Ask a question")

        if query:
            results = run_retrieval(query, st.session_state.sections, top_k=top_k)

            if not results:
                st.subheader("Svar")
                st.write("Informationen hittades inte i dokumenten.")
            else:
                with st.spinner("Generating answer..."):
                    answer = generate_answer(
                        query=query,
                        sections=results,
                        api_key=api_key,
                        model_name=GEMINI_MODEL,
                    )

                with st.spinner("Evaluating answer..."):
                    evaluation = evaluate_answer(
                        query=query,
                        answer=answer,
                        sections=results,
                        api_key=api_key,
                        model_name=GEMINI_MODEL,
                    )

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.subheader("Svar")
                    st.text(answer)

                with col2:
                    st.subheader("Utvärdering")
                    st.text(evaluation)

                st.subheader("Retrieved Sections")
                for sec in results:
                    with st.expander(f"{sec['doc_name']} | {sec['full_section_title']} | Score: {sec['score']}"):
                        st.write(sec["text"])

# TAB 2 — View Sections
with tab2:
    if not st.session_state.sections:
        st.info("No sections loaded yet.")
    else:
        st.subheader("All Parsed Sections")
        for sec in st.session_state.sections:
            with st.expander(f"{sec['doc_name']} | {sec['full_section_title']}"):
                st.write(sec["text"])

# TAB 3 — Contradictions
with tab3:
    if not st.session_state.sections:
        st.info("No sections loaded yet.")
    else:
        contradictions = find_contradictions(st.session_state.sections)

        if not contradictions:
            st.success("No contradictions detected.")
        else:
            st.warning(f"Found {len(contradictions)} possible contradiction(s).")

            for c in contradictions:
                with st.expander(f"{c['section_id']} | {c['doc1']} vs {c['doc2']}"):
                    st.write(f"**Document 1:** {c['doc1']}")
                    st.write(c["text1"])

                    st.write("---")

                    st.write(f"**Document 2:** {c['doc2']}")
                    st.write(c["text2"])

                    st.write("---")
                    st.write(f"**Numbers:** {c['numbers1']} vs {c['numbers2']}")
