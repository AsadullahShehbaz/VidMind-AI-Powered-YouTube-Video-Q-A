import streamlit as st
import os
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import PyPDF2
import docx
import base64
from transformers import pipeline
from pathlib import Path
import requests  # for currency API

# =====================
# 🔐 Load Gemini API Key
# =====================
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    api_key=GOOGLE_API_KEY
)

# =====================
# 🧭 Sidebar Navigation
# =====================
st.set_page_config(page_title="FocusBot", layout="wide")
st.sidebar.title("📌 FocusBot Navigation")
page = st.sidebar.radio(
    "Choose a feature",
    ["🤖 Chatbot", "📄 Document Reader", "🎥Watch Youtube", "💱 Currency Converter"],
    key="main_nav"
)

# =====================
# 🤖 Chatbot Page
# =====================
if page == "🤖 Chatbot":
    st.title("🤖 Smart Chat – Ask Anything, Anytime")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for role, message in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(message)

    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        response = llm.invoke(user_input)
        reply = response.content
        st.session_state.chat_history.append(("assistant", reply))
        st.rerun()

    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# =====================
# 📄 Document Reader Page
# =====================
elif page == "📄 Document Reader":
    st.title("🧾 Summarize, search, and quiz any document")

    uploaded_file = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])

    def extract_text(file):
        if file.name.endswith('.pdf'):
            reader = PyPDF2.PdfReader(file)
            return [page.extract_text() or "" for page in reader.pages]
        elif file.name.endswith('.docx'):
            doc = docx.Document(file)
            return ["\n".join(para.text for para in doc.paragraphs)]
        elif file.name.endswith('.txt'):
            return [file.read().decode("utf-8")]
        else:
            return ["Unsupported file type."]

    if uploaded_file:
        doc_pages = extract_text(uploaded_file)
        total_pages = len(doc_pages)
        page_num = st.number_input("Go to page", 1, total_pages, 1)

        st.subheader(f"📖 Page {page_num} Text")
        st.text_area("Text", doc_pages[page_num - 1][:3000], height=300)

        tab1, tab2 = st.tabs(["🧠 Full Summary", "💬 Ask Gemini"])

        with tab1:
            st.subheader("🧠 Gemini Summary")
            if st.button("Generate Summary"):
                with st.spinner("Thinking..."):
                    full_text = "\n".join(doc_pages)
                    response = llm.invoke(f"Summarize this document:\n{full_text}")
                    summary = response.content
                    st.success("✅ Summary created!")
                    st.markdown(summary)

                    b64 = base64.b64encode(summary.encode()).decode()
                    href = f'<a href="data:text/plain;base64,{b64}" download="summary.txt">📥 Download Summary</a>'
                    st.markdown(href, unsafe_allow_html=True)

        with tab2:
            st.subheader("💬 Ask a Question About the Document")
            question = st.text_input("Your question:")
            if question:
                full_text = "\n".join(doc_pages)
                prompt = f"Context:\n{full_text}\n\nQuestion: {question}"
                response = llm.invoke(prompt)
                st.markdown("### 💡 Gemini Answer")
                st.write(response.content)

# =====================
# 🎥 Study Tube Page (YouTube)
# =====================
elif page == "🎥Watch Youtube":
import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# ---------- Page configuration ----------
st.set_page_config(
    page_title="YouTube Transcript Extractor",
    page_icon="🎬",
    layout="centered"
)

# ---------- Custom CSS for a polished look ----------
st.markdown("""
<style>
    .main > div {
        padding: 2rem 1rem;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        border: none;
        transition: all 0.2s;
    }
    .stButton button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stTextInput input {
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 0.75rem;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    .video-container {
        position: relative;
        padding-bottom: 56.25%; /* 16:9 aspect ratio */
        height: 0;
        overflow: hidden;
        max-width: 100%;
        background: #000;
        margin: 1.5rem 0;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .video-container iframe {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Helper function to extract video ID ----------
def extract_video_id(url):
    """
    Extract YouTube video ID from various URL formats.
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
        r'youtu\.be\/([^?\n]*)',
        r'youtube\.com\/shorts\/([^?\n]*)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# ---------- Function to fetch transcript ----------
def fetch_transcript(video_id):
    """
    Retrieve the transcript for a given video ID.
    """
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_obj = ytt_api.fetch(video_id, languages=['en', 'hi'])
        transcript = " ".join(snippet.text for snippet in transcript_obj.snippets)
        return transcript, None
    except TranscriptsDisabled:
        return None, "No captions are available for this video."
    except NoTranscriptFound:
        return None, "No English transcript was found. The video might have captions in another language."
    except Exception as e:
        return None, f"An unexpected error occurred: {str(e)}"

# ---------- Function to generate distraction‑free embed ----------
def get_video_embed_html(video_id):
    """
    Return an iframe with parameters to minimise distractions (no ads, no suggestions).
    Uses youtube-nocookie.com for privacy.
    """
    return f"""
    <div class="video-container">
        <iframe src="https://www.youtube-nocookie.com/embed/{video_id}?rel=0&modestbranding=1&iv_load_policy=3&controls=1&autoplay=0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen>
        </iframe>
    </div>
    """

# ---------- Main UI ----------
st.title("🎥 YouTube Transcript Extractor")
st.markdown("Enter a YouTube link to watch the video **without distractions** and get its full transcript.")

# Input row with a default example
col1, col2 = st.columns([3, 1])
with col1:
    url_input = st.text_input(
        "Video URL",
        value="https://www.youtube.com/watch?v=1dkfuga2_Ps",
        placeholder="Paste YouTube link here...",
        label_visibility="collapsed"
    )
with col2:
    fetch_button = st.button("Get Transcript & Video", type="primary")

# Process the request
if fetch_button:
    if not url_input.strip():
        st.markdown('<div class="error-box">⚠️ Please enter a YouTube URL.</div>', unsafe_allow_html=True)
    else:
        video_id = extract_video_id(url_input)
        if not video_id:
            st.markdown('<div class="error-box">❌ Could not extract video ID from the provided URL. Please check the link.</div>', unsafe_allow_html=True)
        else:
            # Always show the video player (distraction‑free)
            st.markdown("### 🎬 Video Player")
            st.markdown(get_video_embed_html(video_id), unsafe_allow_html=True)
            st.caption("ℹ️ The player hides suggestions and uses youtube‑nocookie.com for privacy. Ads may still appear depending on the video owner.")

            # Fetch transcript
            with st.spinner("Fetching transcript..."):
                transcript, error = fetch_transcript(video_id)

            if error:
                st.markdown(f'<div class="error-box">❌ {error}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="success-box">✅ Transcript fetched successfully! (Video ID: <code>{video_id}</code>)</div>', unsafe_allow_html=True)

                # Transcript display with copy button
                st.markdown("### 📄 Transcript")
                st.code(transcript, language="text")

                # Word/character count
                word_count = len(transcript.split())
                char_count = len(transcript)
                st.caption(f"📊 {word_count} words · {char_count} characters")

# Footer / info
st.markdown("---")
st.markdown(
    "🔍 **Note:** The transcript is fetched using the [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api). "
    "Only videos with English (or Hindi) captions are supported."
)

# =====================
# 💱 Currency Converter Page
# =====================
elif page == "💱 Currency Converter":
    st.title("💱 Currency Converter")

    st.markdown("Convert one currency into another using real-time exchange rates.")

    currency_list = ["USD", "EUR", "GBP", "PKR", "INR", "CAD", "AUD", "JPY", "CNY", "SAR"]

    from_currency = st.selectbox("From Currency", currency_list, index=0)
    to_currency = st.selectbox("To Currency", currency_list, index=1)
    amount = st.number_input("Amount", min_value=0.0, value=1.0, format="%.2f")

    if st.button("🔁 Convert"):
        if from_currency == to_currency:
            st.warning("Please select two different currencies.")
        else:
            try:
                url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
                response = requests.get(url)
                data = response.json()

                if to_currency in data["rates"]:
                    rate = data["rates"][to_currency]
                    converted = amount * rate
                    st.success(f"{amount:.2f} {from_currency} = {converted:.2f} {to_currency}")
                    st.caption(f"Exchange Rate: 1 {from_currency} = {rate:.4f} {to_currency}")
                else:
                    st.error("Currency not supported.")
            except Exception as e:
                st.error(f"Error fetching conversion: {e}")
