import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from langchain_groq import ChatGroq

# ──────────────────────────────────────────────
# ⚙️  Page Config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="VidMind – AI Video Q&A",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# 🎨  Global CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;700&display=swap');

/* ── Reset & base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #0d0f14 !important;
    color: #e2e4ea !important;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stSidebar"] {
    background: #12141b !important;
    border-right: 1px solid #1f2130;
}
[data-testid="stSidebar"] * { color: #c8cad4 !important; }

/* ── Typography ── */
h1, h2, h3 {
    font-family: 'Space Mono', monospace !important;
    letter-spacing: -0.5px;
}

/* ── Sidebar title ── */
.sidebar-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    color: #7c6af7 !important;
    padding: 0.5rem 0 1rem 0;
    border-bottom: 1px solid #1f2130;
    margin-bottom: 1.2rem;
}

/* ── Sidebar labels ── */
.sidebar-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #5a5d70 !important;
    margin: 1rem 0 0.3rem 0;
}

/* ── Input fields ── */
textarea, input[type="text"], .stTextInput input, .stTextArea textarea {
    background: #1a1d27 !important;
    border: 1px solid #2a2d3e !important;
    border-radius: 8px !important;
    color: #e2e4ea !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.92rem !important;
}
textarea:focus, input[type="text"]:focus {
    border-color: #7c6af7 !important;
    box-shadow: 0 0 0 2px rgba(124,106,247,0.15) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7c6af7, #5b4de0) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.2s ease !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(124,106,247,0.35) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Tabs ── */
[data-testid="stTabs"] button {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.78rem !important;
    color: #5a5d70 !important;
    border: none !important;
    background: transparent !important;
    padding: 0.6rem 1.2rem !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #7c6af7 !important;
    border-bottom: 2px solid #7c6af7 !important;
}

/* ── Cards ── */
.card {
    background: #151720;
    border: 1px solid #1f2130;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}
.card-accent {
    border-left: 3px solid #7c6af7;
}

/* ── Badge / tag ── */
.badge {
    display: inline-block;
    background: rgba(124,106,247,0.15);
    color: #a89cf7;
    border: 1px solid rgba(124,106,247,0.3);
    border-radius: 20px;
    padding: 0.1rem 0.7rem;
    font-size: 0.7rem;
    font-family: 'Space Mono', monospace;
    margin-right: 0.4rem;
}

/* ── Video embed ── */
.video-wrap {
    position: relative;
    padding-bottom: 56.25%;
    height: 0;
    overflow: hidden;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    margin: 1rem 0 1.5rem 0;
    border: 1px solid #1f2130;
}
.video-wrap iframe {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    border: none;
}

/* ── Transcript box ── */
.transcript-box {
    background: #0f111a;
    border: 1px solid #1f2130;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    font-size: 0.85rem;
    line-height: 1.7;
    color: #b0b3c4;
    max-height: 420px;
    overflow-y: auto;
    white-space: pre-wrap;
    font-family: 'DM Sans', sans-serif;
}

/* ── AI answer box ── */
.answer-box {
    background: linear-gradient(135deg, #15172a, #111320);
    border: 1px solid rgba(124,106,247,0.25);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    font-size: 0.92rem;
    line-height: 1.75;
    color: #dde0ee;
}

/* ── Status messages ── */
.msg-success {
    background: rgba(52,211,153,0.08);
    border: 1px solid rgba(52,211,153,0.25);
    border-radius: 8px;
    padding: 0.7rem 1rem;
    color: #34d399;
    font-size: 0.85rem;
    margin: 0.5rem 0;
}
.msg-error {
    background: rgba(248,113,113,0.08);
    border: 1px solid rgba(248,113,113,0.25);
    border-radius: 8px;
    padding: 0.7rem 1rem;
    color: #f87171;
    font-size: 0.85rem;
    margin: 0.5rem 0;
}
.msg-info {
    background: rgba(96,165,250,0.08);
    border: 1px solid rgba(96,165,250,0.25);
    border-radius: 8px;
    padding: 0.7rem 1rem;
    color: #60a5fa;
    font-size: 0.85rem;
    margin: 0.5rem 0;
}

/* ── Stat chips ── */
.stat-row { display: flex; gap: 0.8rem; flex-wrap: wrap; margin-top: 0.6rem; }
.stat-chip {
    background: #1a1d27;
    border: 1px solid #2a2d3e;
    border-radius: 6px;
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    color: #7c6af7;
    font-family: 'Space Mono', monospace;
}

/* ── Spinner override ── */
[data-testid="stSpinner"] { color: #7c6af7 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0d0f14; }
::-webkit-scrollbar-thumb { background: #2a2d3e; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #7c6af7; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# 🔧  Helpers
# ──────────────────────────────────────────────
def extract_video_id(url: str) -> str | None:
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
        r'youtube\.com/watch\?.*v=([^&\n?#]+)',
        r'youtu\.be/([^?\n]*)',
        r'youtube\.com/shorts/([^?\n]*)',
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def fetch_transcript(video_id: str) -> tuple[str | None, str | None]:
    try:
        api = YouTubeTranscriptApi()
        obj = api.fetch(video_id, languages=["en", "hi", "en-US", "en-GB"])
        text = " ".join(s.text for s in obj.snippets)
        return text, None
    except TranscriptsDisabled:
        return None, "Captions are disabled for this video."
    except NoTranscriptFound:
        return None, "No English or Hindi transcript found."
    except Exception as e:
        return None, f"Unexpected error: {e}"


def video_embed_html(video_id: str) -> str:
    return f"""
    <div class="video-wrap">
        <iframe
            src="https://www.youtube-nocookie.com/embed/{video_id}?rel=0&modestbranding=1&iv_load_policy=3"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
        </iframe>
    </div>
    """


# ──────────────────────────────────────────────
# 🔌  LLM setup  (Groq – llama-4-maverick-17b-128e-instruct)
# ──────────────────────────────────────────────
@st.cache_resource
def get_llm():
    return ChatGroq(
        model="openai/gpt-oss-120b",   # closest available open-source 120b-class model on Groq
        temperature=0.4,
        api_key=st.secrets["GROQ_API_KEY"],
    )


# ──────────────────────────────────────────────
# 📦  Session state defaults
# ──────────────────────────────────────────────
for key, default in {
    "transcript": None,
    "video_id": None,
    "video_url": "",
    "ai_answer": "",
    "fetch_error": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ──────────────────────────────────────────────
# 📐  SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">🧠 VidMind</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">YouTube Video URL</div>', unsafe_allow_html=True)

    video_url = st.text_input(
        label="url",
        value=st.session_state.video_url,
        placeholder="Enter Video URL",
        label_visibility="collapsed",
        key="url_input",
    )

    if st.button("⬇  Load Transcript"):
        vid = extract_video_id(video_url)
        if not vid:
            st.session_state.fetch_error = "❌ Invalid YouTube URL."
            st.session_state.transcript = None
            st.session_state.video_id = None
        else:
            with st.spinner("Fetching transcript…"):
                t, err = fetch_transcript(vid)
            if err:
                st.session_state.fetch_error = err
                st.session_state.transcript = None
                st.session_state.video_id = None
            else:
                st.session_state.transcript = t
                st.session_state.video_id = vid
                st.session_state.video_url = video_url
                st.session_state.fetch_error = ""
                st.session_state.ai_answer = ""

    # Status feedback
    if st.session_state.fetch_error:
        st.markdown(f'<div class="msg-error">{st.session_state.fetch_error}</div>', unsafe_allow_html=True)
    elif st.session_state.transcript:
        wc = len(st.session_state.transcript.split())
        st.markdown(f'<div class="msg-success">✅ Transcript ready · {wc:,} words</div>', unsafe_allow_html=True)

    st.divider()

    # ── Query box ──
    st.markdown('<div class="sidebar-label">Your Question</div>', unsafe_allow_html=True)
    query = st.text_area(
        label="query",
        placeholder="e.g. What is the main topic?\nSummarise the key points.\nWhat does the speaker say about X?",
        height=140,
        label_visibility="collapsed",
        key="query_input",
    )

    ask_disabled = not (st.session_state.transcript and query.strip())
    if st.button("✦  Ask AI", disabled=ask_disabled):
        llm = get_llm()
        prompt = (
            "You are a helpful video-analysis assistant. "
            "A user has provided the full transcript of a YouTube video and a question about it. "
            "Answer the question accurately and thoroughly using only information from the transcript.\n\n"
            f"=== FULL TRANSCRIPT ===\n{st.session_state.transcript}\n\n"
            f"=== USER QUESTION ===\n{query.strip()}\n\n"
            "=== YOUR ANSWER ==="
        )
        with st.spinner("Thinking…"):
            response = llm.invoke(prompt)
        st.session_state.ai_answer = response.content

    if not st.session_state.transcript:
        st.markdown(
            '<div class="msg-info" style="margin-top:0.6rem;">↑ Paste a YouTube link and load the transcript first.</div>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown(
        '<p style="font-size:0.68rem;color:#3a3d50;text-align:center;font-family:\'Space Mono\',monospace;">'
        'Powered by Groq · LangChain · YouTube Transcript API</p>',
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────
# 📄  MAIN AREA  –  Two tabs
# ──────────────────────────────────────────────
tab_qa, tab_viewer = st.tabs(["✦  AI Answer", "🎥  Video & Transcript"])

# ── TAB 1 : AI Q&A ──────────────────────────
with tab_qa:
    st.markdown("## AI Answer")

    if st.session_state.ai_answer:
        st.markdown(
            f'<div class="answer-box">{st.session_state.ai_answer}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("")
        # Quick stats
        ans_words = len(st.session_state.ai_answer.split())
        st.markdown(
            f'<div class="stat-row">'
            f'<span class="stat-chip">🧠 Groq · meta-llama/llama-4-maverick-17b-128e-instruct</span>'
            f'<span class="stat-chip">📝 {ans_words} words in answer</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    elif st.session_state.transcript:
        st.markdown(
            '<div class="card">'
            '<p style="color:#5a5d70;font-size:0.9rem;">Type your question in the sidebar and click <strong style="color:#7c6af7;">✦ Ask AI</strong> to get an answer grounded in the full video transcript.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="card">'
            '<p style="color:#5a5d70;font-size:0.9rem;">Load a YouTube video transcript from the sidebar to get started.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

# ── TAB 2 : Video + Transcript ───────────────
with tab_viewer:
    col_vid, col_tx = st.columns([1, 1], gap="large")

    with col_vid:
        st.markdown("## Video Player")
        if st.session_state.video_id:
            st.markdown(video_embed_html(st.session_state.video_id), unsafe_allow_html=True)
            st.markdown(
                f'<span class="badge">ID: {st.session_state.video_id}</span>'
                f'<span class="badge">Privacy-Enhanced Mode</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="card" style="text-align:center;padding:3rem 1rem;">'
                '<p style="font-size:2.5rem;">🎬</p>'
                '<p style="color:#5a5d70;font-size:0.88rem;">Video will appear here after loading a transcript.</p>'
                '</div>',
                unsafe_allow_html=True,
            )

    with col_tx:
        st.markdown("## Full Transcript")
        if st.session_state.transcript:
            t = st.session_state.transcript
            wc = len(t.split())
            cc = len(t)

            # ── Copy button using st.code (built-in copy icon) ──
            st.markdown(
                f'<div class="stat-row" style="margin-bottom:0.8rem;">'
                f'<span class="stat-chip">📝 {wc:,} words</span>'
                f'<span class="stat-chip">🔤 {cc:,} chars</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Streamlit's st.code block has a built-in copy-to-clipboard button (top-right corner)
            st.code(t, language="text")

            st.markdown(
                '<p style="font-size:0.72rem;color:#3a3d50;margin-top:0.3rem;">'
                '↑ Click the copy icon at the top-right of the transcript box to copy the entire transcript.</p>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="card" style="text-align:center;padding:3rem 1rem;">'
                '<p style="font-size:2.5rem;">📄</p>'
                '<p style="color:#5a5d70;font-size:0.88rem;">Transcript will appear here after loading.</p>'
                '</div>',
                unsafe_allow_html=True,
            )
