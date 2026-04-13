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

st.set_page_config(
    page_title="ClauseWise",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

LANGUAGES = {
    "English": {
        "code": "en",
        "title": "ClauseWise AI",
        "hero_subtitle": "Premium document intelligence for grounded answers, contradiction checks, and decision-ready insights.",
        "caption": "Upload documents, ask questions, and turn raw text into structured reasoning.",
        "upload_header": "Workspace",
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
        "insights_tab": "Insights",
        "process_first": "Upload and process documents first.",
        "ask_question": "Ask a question about the uploaded documents",
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
        "decision_analysis": "Decision Intelligence",
        "decision_desc": "Generate key findings, risks, and recommendations from the loaded documents.",
        "generate_insights": "Generate Insights",
        "generating_insights": "Generating decision analysis...",
        "missing_api": "Missing GEMINI_API_KEY. Add it to .env locally or Streamlit secrets in cloud.",
        "language": "Language",
        "no_valid_sections": "No usable sections were found in the uploaded files.",
        "how_to_use": "How it works",
        "how_to_use_text": """
1. Upload one or more TXT files  
2. Click **Process Files**  
3. Ask a question in the first tab  
4. Review contradictions and insights in the other tabs
""",
        "stats_documents": "Processed Files",
        "stats_sections": "Sections",
        "stats_contradictions": "Contradictions",
        "welcome_title": "Smart Document Intelligence",
        "welcome_text": "This app works best with structured text documents. It can still fall back to paragraph chunks when no legal-style sections are found.",
        "ready": "System ready",
        "language_toggle": "Language / Språk",
        "sample_questions": "Sample questions",
        "sample_q1": "What are the payment terms?",
        "sample_q2": "Are there contradictions between the uploaded documents?",
        "sample_q3": "Summarize the key risks.",
    },
    "Svenska": {
        "code": "sv",
        "title": "ClauseWise AI",
        "hero_subtitle": "Premium dokumentintelligens för grundade svar, motsägelsekontroll och beslutsredo insikter.",
        "caption": "Ladda upp dokument, ställ frågor och förvandla rå text till strukturerad analys.",
        "upload_header": "Arbetsyta",
        "upload_label": "Ladda upp TXT-filer",
        "upload_help": "Endast .txt stöds just nu.",
        "top_sections": "Toppsektioner",
        "process_files": "Bearbeta filer",
        "upload_first": "Ladda upp filer först.",
        "processing": "Bearbetar filer...",
        "loaded_sections": "Laddade {count} sektioner.",
        "file_report": "Filbearbetningsrapport",
        "ask_tab": "Ställ frågor",
        "view_tab": "Visa sektioner",
        "contradictions_tab": "Motsägelser",
        "insights_tab": "Insikter",
        "process_first": "Ladda upp och bearbeta dokument först.",
        "ask_question": "Ställ en fråga om de uppladdade dokumenten",
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
        "decision_analysis": "Beslutsintelligens",
        "decision_desc": "Generera nyckelfynd, risker och rekommendationer från de uppladdade dokumenten.",
        "generate_insights": "Generera insikter",
        "generating_insights": "Genererar beslutsanalys...",
        "missing_api": "GEMINI_API_KEY saknas. Lägg till den i .env lokalt eller i Streamlit secrets i molnet.",
        "language": "Språk",
        "no_valid_sections": "Inga användbara sektioner hittades i de uppladdade filerna.",
        "how_to_use": "Så fungerar det",
        "how_to_use_text": """
1. Ladda upp en eller flera TXT-filer  
2. Klicka på **Bearbeta filer**  
3. Ställ en fråga i första fliken  
4. Granska motsägelser och insikter i de andra flikarna
""",
        "stats_documents": "Bearbetade filer",
        "stats_sections": "Sektioner",
        "stats_contradictions": "Motsägelser",
        "welcome_title": "Smart dokumentintelligens",
        "welcome_text": "Appen fungerar bäst med strukturerade textdokument. Den kan också falla tillbaka till styckesindelning när juridiska sektionsrubriker saknas.",
        "ready": "System redo",
        "language_toggle": "Language / Språk",
        "sample_questions": "Exempel på frågor",
        "sample_q1": "Vad är betalningsvillkoren?",
        "sample_q2": "Finns det motsägelser mellan de uppladdade dokumenten?",
        "sample_q3": "Sammanfatta de viktigaste riskerna.",
    }
}


def inject_custom_css():
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
            max-width: 1250px;
        }

        .hero-wrap {
            padding: 1.6rem 1.6rem 1.2rem 1.6rem;
            border-radius: 22px;
            background: linear-gradient(135deg, rgba(76,110,245,0.16), rgba(0,200,151,0.10));
            border: 1px solid rgba(255,255,255,0.10);
            margin-bottom: 1rem;
        }

        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 0.35rem;
        }

        .hero-sub {
            font-size: 1rem;
            opacity: 0.92;
            margin-bottom: 0.25rem;
        }

        .muted {
            opacity: 0.78;
        }

        .glass-card {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 1rem 1rem;
            margin-bottom: 0.85rem;
        }

        .metric-card {
            background: rgba(255,255,255,0.035);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 1rem;
            text-align: center;
        }

        .metric-label {
            font-size: 0.9rem;
            opacity: 0.8;
            margin-bottom: 0.3rem;
        }

        .metric-value {
            font-size: 1.7rem;
            font-weight: 800;
        }

        .section-title {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .answer-box {
            background: rgba(0, 200, 151, 0.08);
            border: 1px solid rgba(0, 200, 151, 0.18);
            border-radius: 18px;
            padding: 1rem;
            white-space: pre-wrap;
            line-height: 1.5;
        }

        .eval-box {
            background: rgba(76, 110, 245, 0.09);
            border: 1px solid rgba(76, 110, 245, 0.18);
            border-radius: 18px;
            padding: 1rem;
            white-space: pre-wrap;
            line-height: 1.45;
        }

        .small-note {
            font-size: 0.92rem;
            opacity: 0.8;
        }

        .sample-chip {
            display: inline-block;
            padding: 0.4rem 0.7rem;
            margin: 0.15rem 0.35rem 0.15rem 0;
            border-radius: 999px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            font-size: 0.88rem;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        [data-testid="stMetricValue"] {
            font-weight: 800;
        }

        .stButton > button {
            border-radius: 12px;
            font-weight: 700;
        }

        .stTextInput > div > div > input {
            border-radius: 12px;
        }

        .stExpander {
            border-radius: 14px !important;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(T):
    st.markdown(
        f"""
        <div class="hero-wrap">
            <div class="hero-title">📄 {T["title"]}</div>
            <div class="hero-sub">{T["hero_subtitle"]}</div>
            <div class="muted">{T["caption"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_panel_title(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def render_answer_box(text):
    st.markdown(f'<div class="answer-box">{text}</div>', unsafe_allow_html=True)


def render_eval_box(text):
    st.markdown(f'<div class="eval-box">{text}</div>', unsafe_allow_html=True)


inject_custom_css()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

with st.sidebar:
    language_name = st.radio("Language / Språk", ["English", "Svenska"], index=1)
    T = LANGUAGES[language_name]
    language_code = T["code"]

if not api_key:
    st.error(T["missing_api"])
    st.stop()

if "sections" not in st.session_state:
    st.session_state.sections = []
if "processed" not in st.session_state:
    st.session_state.processed = False
if "decision_analysis" not in st.session_state:
    st.session_state.decision_analysis = None
if "file_reports" not in st.session_state:
    st.session_state.file_reports = []

render_hero(T)

top_left, top_right = st.columns([1.5, 1])

with top_left:
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="section-title">{T["welcome_title"]}</div>
            <div class="small-note">{T["welcome_text"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with top_right:
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="section-title">{T["sample_questions"]}</div>
            <div class="sample-chip">{T["sample_q1"]}</div>
            <div class="sample-chip">{T["sample_q2"]}</div>
            <div class="sample-chip">{T["sample_q3"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.sidebar:
    st.markdown("### ⚙️ " + T["upload_header"])

    uploaded_files = st.file_uploader(
        T["upload_label"],
        type=["txt"],
        accept_multiple_files=True,
        help=T["upload_help"],
    )

    top_k = st.slider(T["top_sections"], 1, 5, 3)

    if st.button("🚀 " + T["process_files"], use_container_width=True):
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

    st.markdown("---")
    with st.expander("ℹ️ " + T["how_to_use"], expanded=False):
        st.markdown(T["how_to_use_text"])

processed_files_count = len(
    [r for r in st.session_state.file_reports if r.get("status") == "processed"]
)
sections_count = len(st.session_state.sections)
contradictions_count = len(find_contradictions(st.session_state.sections)) if st.session_state.sections else 0

m1, m2, m3 = st.columns(3)
with m1:
    render_metric_card(T["stats_documents"], processed_files_count)
with m2:
    render_metric_card(T["stats_sections"], sections_count)
with m3:
    render_metric_card(T["stats_contradictions"], contradictions_count)

if st.session_state.file_reports:
    with st.expander("📁 " + T["file_report"], expanded=False):
        for report in st.session_state.file_reports:
            if report["status"] == "processed":
                st.success(
                    f"{report['file_name']} -> {report['message']} ({report['sections_found']} sections)"
                )
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

            if not results:
                render_panel_title(T["answer"])
                st.warning(T["not_found"])
            elif results[0]["score"] < 8:
                render_panel_title(T["answer"])
                st.warning(T["low_relevance"])
            else:
                with st.spinner("🤖 " + T["generating_answer"]):
                    answer = generate_answer(
                        query=query,
                        sections=results,
                        api_key=api_key,
                        model_name=GEMINI_MODEL,
                        language=language_code,
                    )

                with st.spinner("🧪 " + T["evaluating_answer"]):
                    evaluation = evaluate_answer(
                        query=query,
                        answer=answer,
                        sections=results,
                        api_key=api_key,
                        model_name=GEMINI_MODEL,
                        language=language_code,
                    )

                col1, col2 = st.columns([1.65, 1])

                with col1:
                    render_panel_title("💬 " + T["answer"])
                    render_answer_box(answer)

                with col2:
                    render_panel_title("📊 " + T["evaluation"])
                    render_eval_box(evaluation)

                st.markdown("")
                render_panel_title("📚 " + T["retrieved_sections"])
                for sec in results:
                    with st.expander(
                        f"{sec['doc_name']} | {sec['full_section_title']} | Score: {sec['score']}",
                        expanded=False,
                    ):
                        st.write(sec["text"])

with tab2:
    if not st.session_state.sections:
        st.info(T["no_sections"])
    else:
        render_panel_title("🧩 " + T["all_sections"])
        for sec in st.session_state.sections:
            with st.expander(f"{sec['doc_name']} | {sec['full_section_title']}"):
                st.write(sec["text"])

with tab3:
    if not st.session_state.sections:
        st.info(T["no_sections"])
    else:
        contradictions = find_contradictions(st.session_state.sections)

        if not contradictions:
            st.success("✅ " + T["no_contradictions"])
        else:
            st.warning(T["found_contradictions"].format(count=len(contradictions)))

            for c in contradictions:
                with st.expander(f"{c['section_id']} | {c['doc1']} vs {c['doc2']}"):
                    left, right = st.columns(2)

                    with left:
                        st.markdown(f"**{T['document_1']}:** {c['doc1']}")
                        st.write(c["text1"])

                    with right:
                        st.markdown(f"**{T['document_2']}:** {c['doc2']}")
                        st.write(c["text2"])

                    st.markdown(f"**{T['numbers']}:** {c['numbers1']} vs {c['numbers2']}")

with tab4:
    if not st.session_state.sections:
        st.info(T["no_sections"])
    else:
        render_panel_title("🧠 " + T["decision_analysis"])
        st.markdown(f'<div class="small-note">{T["decision_desc"]}</div>', unsafe_allow_html=True)
        st.markdown("")

        if st.button("✨ " + T["generate_insights"]):
            contradictions = find_contradictions(st.session_state.sections)

            with st.spinner("🪄 " + T["generating_insights"]):
                st.session_state.decision_analysis = generate_decision_analysis(
                    sections=st.session_state.sections,
                    contradictions=contradictions,
                    api_key=api_key,
                    model_name=GEMINI_MODEL,
                    language=language_code,
                )

        if st.session_state.decision_analysis:
            render_answer_box(st.session_state.decision_analysis)
