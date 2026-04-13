import os
import html
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
        "title": "ClauseWise",
        "hero_badge": "AI Document Intelligence",
        "hero_title": "Turn raw documents into trusted answers and decision insight.",
        "hero_subtitle": "A structured document analysis workspace for grounded QA, contradiction checks, and recommendations.",
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
        "welcome_title": "Built for structured document reasoning",
        "welcome_text": "Best with structured TXT documents. If no legal-style sections are found, the app falls back to paragraph chunks.",
        "sample_questions": "Sample prompts",
        "sample_q1": "What are the payment terms?",
        "sample_q2": "Are there contradictions between the uploaded documents?",
        "sample_q3": "Summarize the biggest risks.",
        "ready": "System ready",
        "empty_state_title": "No documents yet",
        "empty_state_text": "Upload files from the sidebar, process them, then start exploring the document workspace.",
    },
    "Svenska": {
        "code": "sv",
        "title": "ClauseWise",
        "hero_badge": "AI-dokumentintelligens",
        "hero_title": "Förvandla råa dokument till pålitliga svar och beslutsinsikter.",
        "hero_subtitle": "En strukturerad arbetsyta för dokumentanalys med grundad QA, motsägelsekontroll och rekommendationer.",
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
        "welcome_title": "Byggd för strukturerad dokumentanalys",
        "welcome_text": "Fungerar bäst med strukturerade TXT-dokument. Om inga juridiska sektionsrubriker hittas används styckesindelning som reservlösning.",
        "sample_questions": "Exempelfrågor",
        "sample_q1": "Vad är betalningsvillkoren?",
        "sample_q2": "Finns det motsägelser mellan de uppladdade dokumenten?",
        "sample_q3": "Sammanfatta de största riskerna.",
        "ready": "System redo",
        "empty_state_title": "Inga dokument ännu",
        "empty_state_text": "Ladda upp filer från sidopanelen, bearbeta dem och börja sedan utforska dokumentarbetsytan.",
    }
}


def esc(text: str) -> str:
    return html.escape(str(text)).replace("\n", "<br>")


def inject_custom_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: #0f172a;
        }

        .block-container {
            max-width: 1240px;
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }

        [data-testid="stSidebar"] {
            background: #111827;
            border-right: 1px solid rgba(148, 163, 184, 0.14);
        }

        .hero {
            padding: 1.4rem 1.45rem;
            border-radius: 24px;
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 58%, #0b2239 100%);
            border: 1px solid rgba(148, 163, 184, 0.16);
            margin-bottom: 1rem;
        }

        .hero-badge {
            display: inline-block;
            padding: 0.35rem 0.72rem;
            border-radius: 999px;
            background: rgba(59, 130, 246, 0.12);
            border: 1px solid rgba(59, 130, 246, 0.28);
            color: #bfdbfe;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
        }

        .hero-title {
            font-size: 2.15rem;
            line-height: 1.08;
            font-weight: 800;
            letter-spacing: -0.03em;
            color: #f8fafc;
            margin-bottom: 0.6rem;
        }

        .hero-subtitle {
            max-width: 760px;
            color: #cbd5e1;
            font-size: 1rem;
            line-height: 1.55;
        }

        .panel {
            padding: 1rem;
            border-radius: 20px;
            background: #111827;
            border: 1px solid rgba(148, 163, 184, 0.14);
            box-shadow: 0 10px 30px rgba(2, 6, 23, 0.18);
            margin-bottom: 0.9rem;
        }

        .panel-title {
            font-size: 1.02rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 0.35rem;
        }

        .panel-text {
            color: #cbd5e1;
            font-size: 0.94rem;
            line-height: 1.55;
        }

        .chip {
            display: inline-block;
            margin: 0.18rem 0.35rem 0.12rem 0;
            padding: 0.42rem 0.75rem;
            border-radius: 999px;
            background: rgba(59, 130, 246, 0.10);
            border: 1px solid rgba(59, 130, 246, 0.20);
            color: #dbeafe;
            font-size: 0.84rem;
            font-weight: 600;
        }

        .metric-card {
            border-radius: 20px;
            padding: 1rem 1rem 1.05rem 1rem;
            border: 1px solid rgba(148, 163, 184, 0.14);
            color: white;
            min-height: 118px;
        }

        .metric-blue {
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
        }

        .metric-cyan {
            background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%);
        }

        .metric-amber {
            background: linear-gradient(135deg, #b45309 0%, #f59e0b 100%);
        }

        .metric-label {
            font-size: 0.88rem;
            font-weight: 700;
            margin-bottom: 0.45rem;
            color: rgba(255,255,255,0.92);
        }

        .metric-value {
            font-size: 1.95rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 0.28rem;
        }

        .metric-sub {
            font-size: 0.82rem;
            color: rgba(255,255,255,0.88);
        }

        .answer-box {
            background: rgba(16, 185, 129, 0.10);
            border: 1px solid rgba(16, 185, 129, 0.24);
            border-radius: 18px;
            padding: 1rem;
            color: #e5e7eb;
            line-height: 1.6;
            white-space: pre-wrap;
        }

        .eval-box {
            background: rgba(59, 130, 246, 0.10);
            border: 1px solid rgba(59, 130, 246, 0.22);
            border-radius: 18px;
            padding: 1rem;
            color: #e5e7eb;
            line-height: 1.55;
            white-space: pre-wrap;
        }

        .empty-state {
            text-align: center;
            padding: 2rem 1rem;
            border-radius: 20px;
            background: #111827;
            border: 1px solid rgba(148, 163, 184, 0.14);
        }

        .empty-title {
            font-size: 1.12rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 0.3rem;
        }

        .empty-text {
            color: #cbd5e1;
            line-height: 1.5;
        }

        .stButton > button {
            border-radius: 12px;
            font-weight: 700;
            background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%);
            color: white;
            border: none;
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.22);
        }

        .stButton > button:hover {
            filter: brightness(1.03);
        }

        .stTextInput > div > div > input {
            border-radius: 12px;
            background: rgba(255,255,255,0.04);
        }

        [data-baseweb="tab-list"] {
            gap: 0.45rem;
        }

        [data-baseweb="tab"] {
            border-radius: 999px !important;
            background: rgba(255,255,255,0.04) !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        [data-baseweb="tab"][aria-selected="true"] {
            background: rgba(59, 130, 246, 0.14) !important;
        }

        .stExpander {
            border-radius: 16px !important;
            overflow: hidden;
            border: 1px solid rgba(148, 163, 184, 0.12) !important;
            background: rgba(255,255,255,0.025);
        }

        .section-label {
            font-size: 1.02rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 0.5rem;
        }

        .helper-note {
            color: #94a3b8;
            font-size: 0.92rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(T):
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-badge">{esc(T["hero_badge"])}</div>
            <div class="hero-title">{esc(T["hero_title"])}</div>
            <div class="hero-subtitle">{esc(T["hero_subtitle"])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_panel(title, text):
    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-title">{esc(title)}</div>
            <div class="panel-text">{esc(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chip_panel(title, items):
    chips = "".join([f'<span class="chip">{esc(item)}</span>' for item in items])
    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-title">{esc(title)}</div>
            <div style="margin-top:0.35rem;">{chips}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric(label, value, subtitle, klass):
    st.markdown(
        f"""
        <div class="metric-card {klass}">
            <div class="metric-label">{esc(label)}</div>
            <div class="metric-value">{esc(value)}</div>
            <div class="metric-sub">{esc(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_answer_box(text):
    st.markdown(f'<div class="answer-box">{esc(text)}</div>', unsafe_allow_html=True)


def render_eval_box(text):
    st.markdown(f'<div class="eval-box">{esc(text)}</div>', unsafe_allow_html=True)


def render_empty_state(title, text):
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="empty-title">📄 {esc(title)}</div>
            <div class="empty-text">{esc(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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

top_left, top_right = st.columns([1.15, 1])

with top_left:
    render_panel(T["welcome_title"], T["welcome_text"])

with top_right:
    render_chip_panel(
        T["sample_questions"],
        [T["sample_q1"], T["sample_q2"], T["sample_q3"]],
    )

with st.sidebar:
    st.markdown(f"### {T['upload_header']}")

    uploaded_files = st.file_uploader(
        T["upload_label"],
        type=["txt"],
        accept_multiple_files=True,
        help=T["upload_help"],
    )

    top_k = st.slider(T["top_sections"], 1, 5, 3)

    if st.button(T["process_files"], use_container_width=True):
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
    with st.expander(T["how_to_use"], expanded=False):
        st.markdown(T["how_to_use_text"])

processed_files_count = len(
    [r for r in st.session_state.file_reports if r.get("status") == "processed"]
)
sections_count = len(st.session_state.sections)
contradictions_count = len(find_contradictions(st.session_state.sections)) if st.session_state.sections else 0

m1, m2, m3 = st.columns(3)
with m1:
    render_metric(T["stats_documents"], processed_files_count, T["ready"], "metric-blue")
with m2:
    render_metric(T["stats_sections"], sections_count, T["ready"], "metric-cyan")
with m3:
    render_metric(T["stats_contradictions"], contradictions_count, T["ready"], "metric-amber")

if st.session_state.file_reports:
    with st.expander(T["file_report"], expanded=False):
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
        render_empty_state(T["empty_state_title"], T["empty_state_text"])
    else:
        query = st.text_input(T["ask_question"])

        if query:
            results = run_retrieval(query, st.session_state.sections, top_k=top_k)

            if not results:
                st.warning(T["not_found"])
            elif results[0]["score"] < 8:
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
                    st.markdown(f'<div class="section-label">{T["answer"]}</div>', unsafe_allow_html=True)
                    render_answer_box(answer)

                with col2:
                    st.markdown(f'<div class="section-label">{T["evaluation"]}</div>', unsafe_allow_html=True)
                    render_eval_box(evaluation)

                st.markdown("")
                st.markdown(f'<div class="section-label">{T["retrieved_sections"]}</div>', unsafe_allow_html=True)
                for sec in results:
                    with st.expander(
                        f"{sec['doc_name']} | {sec['full_section_title']} | Score: {sec['score']}",
                        expanded=False,
                    ):
                        st.write(sec["text"])

with tab2:
    if not st.session_state.sections:
        render_empty_state(T["empty_state_title"], T["empty_state_text"])
    else:
        st.markdown(f'<div class="section-label">{T["all_sections"]}</div>', unsafe_allow_html=True)
        for sec in st.session_state.sections:
            with st.expander(f"{sec['doc_name']} | {sec['full_section_title']}"):
                st.write(sec["text"])

with tab3:
    if not st.session_state.sections:
        render_empty_state(T["empty_state_title"], T["empty_state_text"])
    else:
        contradictions = find_contradictions(st.session_state.sections)

        if not contradictions:
            st.success(T["no_contradictions"])
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
        render_empty_state(T["empty_state_title"], T["empty_state_text"])
    else:
        st.markdown(f'<div class="section-label">{T["decision_analysis"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="helper-note">{T["decision_desc"]}</div>', unsafe_allow_html=True)
        st.markdown("")

        if st.button(T["generate_insights"]):
            contradictions = find_contradictions(st.session_state.sections)

            with st.spinner("✨ " + T["generating_insights"]):
                st.session_state.decision_analysis = generate_decision_analysis(
                    sections=st.session_state.sections,
                    contradictions=contradictions,
                    api_key=api_key,
                    model_name=GEMINI_MODEL,
                    language=language_code,
                )

        if st.session_state.decision_analysis:
            render_answer_box(st.session_state.decision_analysis)
