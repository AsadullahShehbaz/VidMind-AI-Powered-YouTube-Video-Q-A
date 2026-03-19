# 🧠 VidMind — AI-Powered YouTube Video Q&A

> Paste a YouTube link. Ask anything. Get answers grounded in the full transcript — instantly.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLM-F55036?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-0.1+-1C3C3C?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)

---

## What It Does

VidMind extracts the complete transcript of any YouTube video and sends it — in full — to a Groq-hosted LLM alongside your question. No chunking, no summarization before answering. The model sees everything.

---

## Features

| | |
|---|---|
| 🎯 **Full-context Q&A** | Entire transcript injected into every prompt — no information loss |
| ⚡ **Groq inference** | Sub-second responses via `meta-llama/llama-4-maverick-17b-128e-instruct` |
| 🎬 **Privacy-enhanced player** | Distraction-free YouTube embed via `youtube-nocookie.com` |
| 📄 **One-click transcript copy** | Native copy button on the full transcript block |
| 🌑 **Dark UI** | Custom-styled Streamlit with Space Mono + DM Sans typography |

---

## Tech Stack

- **Frontend** — Streamlit (wide layout, custom CSS)
- **LLM** — Groq API via `langchain-groq` · `meta-llama/llama-4-maverick-17b-128e-instruct`
- **Transcript** — `youtube-transcript-api` (English + Hindi fallback)
- **Orchestration** — LangChain

---

## Quick Start

**1. Clone & install**
```bash
git clone https://github.com/your-username/vidmind.git
cd vidmind
pip install -r requirements.txt
```

**2. Add your Groq API key**
```toml
# .streamlit/secrets.toml
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxx"
```
Get a free key at [console.groq.com](https://console.groq.com)

**3. Run**
```bash
streamlit run app.py
```

---

## How to Use

```
1. Paste a YouTube URL in the sidebar
2. Click  ⬇ Load Transcript
3. Type your question
4. Click  ✦ Ask AI
```

Switch to the **Video & Transcript** tab to watch the video and read or copy the full transcript alongside each other.

---

## Project Structure

```
vidmind/
├── app.py               # Single-file Streamlit app
├── requirements.txt     # Dependencies
└── .streamlit/
    └── secrets.toml     # API keys (not committed)
```

---

## Requirements

```
streamlit>=1.35.0
langchain-groq>=0.1.9
youtube-transcript-api>=0.6.2
```

---

## Limitations

- Only works with videos that have English or Hindi captions enabled
- Very long videos (3h+) may approach token limits depending on the model context window

---

## License

MIT © 2025 — built with ☕ and too many YouTube tabs open.
