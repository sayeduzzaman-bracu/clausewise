import os
import streamlit as st
from dotenv import load_dotenv

from config import GEMINI_MODEL
from pipeline import load_all_sections_from_uploads, run_retrieval
from answerer import generate_answer
from evaluator import evaluate_answer
from contradiction_checker import find_contradictions
from decision_engine import generate_decision_analysis

load_dotenv()

st.set_page_config(page_title="ClauseWise", page_icon="📄", layout="wide")

LANGUAGES = {
    "English": {
        "code": "en",
        "title": "📄 ClauseWise",
        "caption": "Document Intelligence with QA, Evaluation, Contradiction Detection, and Decision Insights",
        "upload_header": "Upload Documents",
        "upload_label": "Upload TXT files",
        "upload_help": "Only .txt files are supported right now.",
        "top_sections": "Top sections",
        "process_files": "Process Files",
        "upload_first": "Upload files first.",
        "processing": "Processing files...",
        "loaded_sections": "Loaded {count} sections.",
        "file_report": "File Processing Report",
        "ask_tab": "Ask Questions",
        "view_tab": "View Sections",
        "contradictions_tab": "Contradictions",
        "insights_tab": "Insights / Decisions",
        "process_first": "Upload and process documents first.",
        "ask_question": "Ask a question",
        "answer": "Answer",
        "evaluation": "Evaluation",
        "retrieved_sections": "Retrieved Sections",
        "not_found": "The information was not found in the uploaded documents.",
        "low_relevance": "The uploaded files do not appear relevant enough to answer this confidently.",
        "generating_answer": "Generating answer...",
        "evaluating_answer": "Evaluating answer...",
        "all_sections": "All Parsed Sections",
        "no_sections": "No sections loaded yet.",
        "no_contradictions": "No contradictions detected.",
        "found_contradictions": "Found {count} possible contradiction(s).",
        "document_1": "Document 1",
        "document_2": "Document 2",
        "numbers": "Numbers",
        "decision_analysis": "Decision-Oriented Analysis",
        "decision_desc": "Generate key findings, risks, and recommendations from the loaded documents.",
        "generate_insights": "Generate Insights",
        "generating_insights": "Generating decision analysis...",
        "missing_api": "Missing GEMINI_API_KEY. Add it to .env locally or Streamlit secrets in cloud.",
        "language": "Language",
        "no_valid_sections": "No usable sections were found in the uploaded files.",
    },
    "Svenska": {
        "code": "sv",
        "title": "📄 ClauseWise",
        "caption": "Dokumentintelligens med QA, utvärdering, motsägelsedetektering och beslutsinsikter",
        "upload_header": "Ladda upp dokument",
        "upload_label": "Ladda upp TXT-filer",
        "upload_help": "Endast .txt stöds just nu.",
        "top_sections": "Antal toppsektioner",
        "process_files": "Bearbeta filer",
        "upload_first": "Ladda upp filer först.",
        "processing": "Bearbetar filer...",
        "loaded_sections": "Laddade {count} sektioner.",
        "file_report": "Filbearbetningsrapport",
        "ask_tab": "Ställ frågor",
        "view_tab": "Visa sektioner",
        "contradictions_tab": "Motsägelser",
        "insights_tab": "Insikter / Beslut",
        "process_first": "Ladda upp och bearbeta dokument först.",
        "ask_question": "Ställ en fråga",
        "answer": "Svar",
        "evaluation": "Utvärdering",
        "retrieved_sections": "Hämtade sektioner",
        "not_found": "Informationen hittades inte i de uppladdade dokumenten.",
        "low_relevance": "De uppladdade filerna verkar inte vara tillräckligt relevanta för att besvara frågan säkert.",
        "generating_answer": "Genererar svar...",
        "evaluating_answer": "Utvärderar svar...",
        "all_sections": "Alla tolkade sektioner",
        "no_sections": "Inga sektioner har laddats ännu.",
        "no_contradictions": "Inga motsägelser upptäcktes.",
        "found_contradictions": "Hittade {count} möjlig(a) motsägelse(r).",
        "document_1": "Dokument 1",
        "document_2": "Dokument 2",
        "numbers": "Siffror",
        "decision_analysis": "Beslutsorienterad analys",
        "decision_desc": "Generera nyckelfynd, risker och rekommendationer från de uppladdade dokumenten.",
        "generate_insights": "Generera insikter",
        "generating_insights": "Genererar beslutsanalys...",
        "missing_api": "GEMINI_API_KEY saknas. Lägg till den i .env lokalt eller i Streamlit secrets i molnet.",
        "language": "Språk",
        "no_valid_sections": "Inga användbara sektioner hittades i de uppladdade filerna.",
    }
}

# API KEY
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

if not api_key:
    st.error("Missing GEMINI_API_KEY. Add it to .env locally or Streamlit secrets in cloud.")
    st.stop()

# Session state
if "sections" not in st.session_state:
    st.session_state.sections = []
if "processed" not in st.session_state:
    st.session_state.processed = False
if "decision_analysis" not in st.session_state:
    st.session_state.decision_analysis = None
if "file_reports" not in st.session_state:
    st.session_state.file_reports = []

with st.sidebar:
    language_name = st.radio("Language / Språk", ["English", "Svenska"], index=1)
    T = LANGUAGES[language_name]
    language_code = T["code"]

st.title(T["title"])
st.caption(T["caption"])

with st.sidebar:
    st.header(T["upload_header"])

    uploaded_files = st.file_uploader(
        T["upload_label"],
        type=["txt"],
        accept_multiple_files=True,
        help=T["upload_help"],
    )

    top_k = st.slider(T["top_sections"], 1, 5, 3)

    if st.button(T["process_files"]):
        if not uploaded_files:
            st.warning(T["upload_first"])
        else:
            with st.spinner(T["processing"]):
                sections, file_reports = load_all_sections_from_uploads(uploaded_files)
                st.session_state.sections = sections
                st.session_state.file_reports = file_reports
                st.session_state.processed = True
                st.session_state.decision_analysis = None

            if not sections:
                st.error(T["no_valid_sections"])
            else:
                st.success(T["loaded_sections"].format(count=len(sections)))

    if st.session_state.file_reports:
        st.subheader(T["file_report"])
        for report in st.session_state.file_reports:
            if report["status"] == "processed":
                st.success(f"{report['file_name']} -> {report['message']} ({report['sections_found']} sections)")
            elif report["status"] in {"unsupported", "empty"}:
                st.warning(f"{report['file_name']} -> {report['message']}")
            else:
                st.error(f"{report['file_name']} -> {report['message']}")

tab1, tab2, tab3, tab4 = st.tabs(
    [T["ask_tab"], T["view_tab"], T["contradictions_tab"], T["insights_tab"]]
)

with tab1:
    if not st.session_state.processed:
        st.info(T["process_first"])
    else:
        query = st.text_input(T["ask_question"])

        if query:
            results = run_retrieval(query, st.session_state.sections, top_k=top_k)

            # Relevance guardrail
            if not results:
                st.subheader(T["answer"])
                st.write(T["not_found"])
            elif results[0]["score"] < 8:
                st.subheader(T["answer"])
                st.warning(T["low_relevance"])
            else:
                with st.spinner(T["generating_answer"]):
                    answer = generate_answer(
                        query=query,
                        sections=results,
                        api_key=api_key,
                        model_name=GEMINI_MODEL,
                        language=language_code,
                    )

                with st.spinner(T["evaluating_answer"]):
                    evaluation = evaluate_answer(
                        query=query,
                        answer=answer,
                        sections=results,
                        api_key=api_key,
                        model_name=GEMINI_MODEL,
                        language=language_code,
                    )

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.subheader(T["answer"])
                    st.text(answer)

                with col2:
                    st.subheader(T["evaluation"])
                    st.text(evaluation)

                st.subheader(T["retrieved_sections"])
                for sec in results:
                    with st.expander(f"{sec['doc_name']} | {sec['full_section_title']} | Score: {sec['score']}"):
                        st.write(sec["text"])

with tab2:
    if not st.session_state.sections:
        st.info(T["no_sections"])
    else:
        st.subheader(T["all_sections"])
        for sec in st.session_state.sections:
            with st.expander(f"{sec['doc_name']} | {sec['full_section_title']}"):
                st.write(sec["text"])

with tab3:
    if not st.session_state.sections:
        st.info(T["no_sections"])
    else:
        contradictions = find_contradictions(st.session_state.sections)

        if not contradictions:
            st.success(T["no_contradictions"])
        else:
            st.warning(T["found_contradictions"].format(count=len(contradictions)))

            for c in contradictions:
                with st.expander(f"{c['section_id']} | {c['doc1']} vs {c['doc2']}"):
                    st.write(f"**{T['document_1']}:** {c['doc1']}")
                    st.write(c["text1"])
                    st.write("---")
                    st.write(f"**{T['document_2']}:** {c['doc2']}")
                    st.write(c["text2"])
                    st.write("---")
                    st.write(f"**{T['numbers']}:** {c['numbers1']} vs {c['numbers2']}")

with tab4:
    if not st.session_state.sections:
        st.info(T["no_sections"])
    else:
        st.subheader(T["decision_analysis"])
        st.write(T["decision_desc"])

        if st.button(T["generate_insights"]):
            contradictions = find_contradictions(st.session_state.sections)

            with st.spinner(T["generating_insights"]):
                st.session_state.decision_analysis = generate_decision_analysis(
                    sections=st.session_state.sections,
                    contradictions=contradictions,
                    api_key=api_key,
                    model_name=GEMINI_MODEL,
                    language=language_code,
                )

        if st.session_state.decision_analysis:
            st.text(st.session_state.decision_analysis)
