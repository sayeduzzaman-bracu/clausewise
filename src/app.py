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
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

LANGUAGES = {
    "English": {
        "code": "en",
        "title": "ClauseWise",
        "hero_badge": "AI Document Intelligence",
        "hero_title": "Turn raw documents into\nanswers, contradictions,\nand decision insight.",
        "hero_subtitle": "A colorful, client-facing workspace for grounded QA, contradiction checks, and insight generation.",
        "upload_header": "Control Center",
        "upload_label": "Upload TXT files",
        "upload_help": "Only .txt files are supported right now.",
        "top_sections": "Top sections",
        "process_files": "Process Files",
        "upload_first": "Upload files first.",
        "processing": "Processing files...",
        "loaded_sections": "Loaded {count} sections.",
        "file_report": "File Processing Report",
        "ask_tab": "Ask",
        "view_tab": "Sections",
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
        "language_toggle": "Language / Språk",
        "ready": "Ready",
        "empty_state_title": "No documents yet",
        "empty_state_text": "Upload files from the sidebar, process them, then start exploring the document universe.",
    },
    "Svenska": {
        "code": "sv",
        "title": "ClauseWise",
        "hero_badge": "AI-dokumentintelligens",
        "hero_title": "Förvandla råa dokument till\nsvar, motsägelser,\noch beslutsinsikter.",
        "hero_subtitle": "En färgstark, kundvänlig arbetsyta för grundad QA, motsägelsekontroll och insiktsgenerering.",
        "upload_header": "Kontrollcenter",
        "upload_label": "Ladda upp TXT-filer",
        "upload_help": "Endast .txt stöds just nu.",
        "top_sections": "Toppsektioner",
        "process_files": "Bearbeta filer",
        "upload_first": "Ladda upp filer först.",
        "processing": "Bearbetar filer...",
        "loaded_sections": "Laddade {count} sektioner.",
        "file_report": "Filbearbetningsrapport",
        "ask_tab": "Frågor",
        "view_tab": "Sektioner",
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
        "welcome_title": "Byggd för strukturerad dokumentresonemang",
        "welcome_text": "Fungerar bäst med strukturerade TXT-dokument. Om inga juridiska sektionsrubriker hittas, används styckesindelning som reservplan.",
        "sample_questions": "Exempelfrågor",
        "sample_q1": "Vad är betalningsvillkoren?",
        "sample_q2": "Finns det motsägelser mellan de uppladdade dokumenten?",
        "sample_q3": "Sammanfatta de största riskerna.",
        "language_toggle": "Language / Språk",
        "ready": "Redo",
        "empty_state_title": "Inga dokument ännu",
        "empty_state_text": "Ladda upp filer från sidopanelen, bearbeta dem och börja sedan utforska dokumentgalaxen.",
    }
}


def inject_custom_css():
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(255, 0, 153, 0.18), transparent 28%),
                radial-gradient(circle at top right, rgba(0, 255, 255, 0.14), transparent 24%),
                radial-gradient(circle at bottom left, rgba(255, 191, 0, 0.12), transparent 28%),
                linear-gradient(180deg, #0b1020 0%, #0e152d 48%, #0a1224 100%);
        }

        .block-container {
            max-width: 1250px;
            padding-top: 1.1rem;
            padding-bottom: 2rem;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(18,25,47,0.95), rgba(13,18,34,0.98));
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        .hero-shell {
            position: relative;
            overflow: hidden;
            padding: 1.35rem 1.4rem 1.3rem 1.4rem;
            border-radius: 28px;
            background:
                linear-gradient(135deg, rgba(255,0,153,0.18), rgba(76,110,245,0.18) 38%, rgba(0,200,151,0.16) 72%, rgba(255,191,0,0.14));
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0 24px 80px rgba(0,0,0,0.28);
            margin-bottom: 1rem;
        }

        .hero-shell:before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                radial-gradient(circle at 15% 20%, rgba(255,255,255,0.14), transparent 18%),
                radial-gradient(circle at 85% 25%, rgba(255,255,255,0.10), transparent 18%);
            pointer-events: none;
        }

        .hero-badge {
            display: inline-block;
            padding: 0.34rem 0.75rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.16);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            margin-bottom: 0.8rem;
        }

        .hero-title {
            font-size: 2.55rem;
            line-height: 1.03;
            font-weight: 900;
            letter-spacing: -0.03em;
            white-space: pre-line;
            margin-bottom: 0.7rem;
        }

        .hero-subtitle {
            font-size: 1rem;
            line-height: 1.5;
            max-width: 760px;
            opacity: 0.92;
        }

        .panel {
            border-radius: 24px;
            padding: 1rem 1rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.035));
            border: 1px solid rgba(255,255,255,0.09);
            box-shadow: 0 16px 40px rgba(0,0,0,0.18);
            margin-bottom: 0.9rem;
        }

        .panel-soft {
            border-radius: 22px;
            padding: 1rem;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 0.9rem;
        }

        .panel-title {
            font-size: 1.06rem;
            font-weight: 800;
            margin-bottom: 0.35rem;
        }

        .panel-text {
            opacity: 0.86;
            line-height: 1.55;
            font-size: 0.94rem;
        }

        .chip {
            display: inline-block;
            margin: 0.16rem 0.35rem 0.16rem 0;
            padding: 0.42rem 0.78rem;
            border-radius: 999px;
            font-size: 0.84rem;
            font-weight: 600;
            background: linear-gradient(135deg, rgba(255,0,153,0.16), rgba(76,110,245,0.14));
            border: 1px solid rgba(255,255,255,0.10);
        }

        .metric-tile {
            border-radius: 24px;
            padding: 1rem 1rem 1.1rem 1rem;
            color: white;
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0 16px 42px rgba(0,0,0,0.18);
            min-height: 120px;
        }

        .metric-pink {
            background: linear-gradient(135deg, rgba(255,0,153,0.72), rgba(125,57,255,0.72));
        }

        .metric-cyan {
            background: linear-gradient(135deg, rgba(0,194,255,0.72), rgba(0,255,170,0.60));
        }

        .metric-amber {
            background: linear-gradient(135deg, rgba(255,153,0,0.76), rgba(255,60,60,0.62));
        }

        .metric-label {
            font-size: 0.88rem;
            font-weight: 700;
            opacity: 0.95;
            margin-bottom: 0.5rem;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 900;
            line-height: 1;
            margin-bottom: 0.35rem;
        }

        .metric-sub {
            font-size: 0.82rem;
            opacity: 0.92;
        }

        .answer-box {
            border-radius: 24px;
            padding: 1rem 1rem;
            background: linear-gradient(135deg, rgba(0,255,170,0.14), rgba(0,194,255,0.10));
            border: 1px solid rgba(0,255,170,0.18);
            line-height: 1.58;
            white-space: pre-wrap;
            box-shadow: 0 16px 38px rgba(0,0,0,0.16);
        }

        .eval-box {
            border-radius: 24px;
            padding: 1rem 1rem;
            background: linear-gradient(135deg, rgba(255,0,153,0.12), rgba(125,57,255,0.10));
            border: 1px solid rgba(255,0,153,0.18);
            line-height: 1.55;
            white-space: pre-wrap;
            box-shadow: 0 16px 38px rgba(0,0,0,0.16);
        }

        .empty-state {
            text-align: center;
            padding: 2rem 1rem;
            border-radius: 24px;
            background: linear-gradient(180deg, rgba(255,255,255,0.045), rgba(255,255,255,0.03));
            border: 1px solid rgba(255,255,255,0.08);
        }

        .empty-title {
            font-size: 1.2rem;
            font-weight: 800;
            margin-bottom: 0.3rem;
        }

        .empty-text {
            opacity: 0.82;
        }

        .stButton > button {
            border-radius: 14px;
            font-weight: 800;
            border: 1px solid rgba(255,255,255,0.08);
            background: linear-gradient(135deg, rgba(255,0,153,0.85), rgba(125,57,255,0.88));
            color: white;
            box-shadow: 0 10px 24px rgba(125,57,255,0.28);
        }

        .stButton > button:hover {
            filter: brightness(1.04);
        }

        .stTextInput > div > div > input {
            border-radius: 14px;
            background: rgba(255,255,255,0.05);
        }

        [data-baseweb="tab-list"] {
            gap: 0.45rem;
        }

        [data-baseweb="tab"] {
            border-radius: 999px !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            background: rgba(255,255,255,0.05) !important;
        }

        [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, rgba(255,0,153,0.28), rgba(76,110,245,0.28)) !important;
        }

        .stExpander {
            border-radius: 18px !important;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.08) !important;
            background: rgba(255,255,255,0.03);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def esc(text: str) -> str:
    return html.escape(str(text)).replace("\n", "<br>")


def render_hero(T):
    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-badge">✨ {esc(T["hero_badge"])}</div>
            <div class="hero-title">{esc(T["hero_title"])}</div>
            <div class="hero-subtitle">{esc(T["hero_subtitle"])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_panel(title, text):
    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-title">{esc(title)}</div>
            <div class="panel-text">{esc(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sample_panel(title, chips):
    chip_html = "".join([f'<span class="chip">{esc(chip)}</span>' for chip in chips])
    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-title">{esc(title)}</div>
            <div style="margin-top: 0.5rem;">{chip_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric(label, value, subtitle, variant):
    st.markdown(
        f"""
        <div class="metric-tile {variant}">
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
            <div class="empty-title">🪐 {esc(title)}</div>
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

top_left, top_right = st.columns([1.2, 1])

with top_left:
    render_info_panel(T["welcome_title"], T["welcome_text"])

with top_right:
    render_sample_panel(
        T["sample_questions"],
        [T["sample_q1"], T["sample_q2"], T["sample_q3"]],
    )

with st.sidebar:
    st.markdown(f"### 🎛️ {T['upload_header']}")

    uploaded_files = st.file_uploader(
        T["upload_label"],
        type=["txt"],
        accept_multiple_files=True,
        help=T["upload_help"],
    )

    top_k = st.slider(T["top_sections"], 1, 5, 3)

    if st.button(f"🚀 {T['process_files']}", use_container_width=True):
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
    with st.expander(f"ℹ️ {T['how_to_use']}", expanded=False):
        st.markdown(T["how_to_use_text"])

processed_files_count = len(
    [r for r in st.session_state.file_reports if r.get("status") == "processed"]
)
sections_count = len(st.session_state.sections)
contradictions_count = len(find_contradictions(st.session_state.sections)) if st.session_state.sections else 0

m1, m2, m3 = st.columns(3)
with m1:
    render_metric(T["stats_documents"], processed_files_count, T["ready"], "metric-pink")
with m2:
    render_metric(T["stats_sections"], sections_count, T["ready"], "metric-cyan")
with m3:
    render_metric(T["stats_contradictions"], contradictions_count, T["ready"], "metric-amber")

if st.session_state.file_reports:
    with st.expander(f"📁 {T['file_report']}", expanded=False):
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
    [f"💬 {T['ask_tab']}", f"🧩 {T['view_tab']}", f"⚠️ {T['contradictions_tab']}", f"🧠 {T['insights_tab']}"]
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
                    st.markdown("### 💬 " + T["answer"])
                    render_answer_box(answer)

                with col2:
                    st.markdown("### 📊 " + T["evaluation"])
                    render_eval_box(evaluation)

                st.markdown("### 📚 " + T["retrieved_sections"])
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
        st.markdown("### 🧩 " + T["all_sections"])
        for sec in st.session_state.sections:
            with st.expander(f"{sec['doc_name']} | {sec['full_section_title']}"):
                st.write(sec["text"])

with tab3:
    if not st.session_state.sections:
        render_empty_state(T["empty_state_title"], T["empty_state_text"])
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
        render_empty_state(T["empty_state_title"], T["empty_state_text"])
    else:
        st.markdown("### 🧠 " + T["decision_analysis"])
        render_info_panel(T["decision_analysis"], T["decision_desc"])

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
