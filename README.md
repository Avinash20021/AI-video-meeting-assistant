# 🎬 AI Video Meeting Assistant

> Transcribe · Summarise · Chat with your meetings

An end-to-end AI powered meeting intelligence tool that takes a YouTube URL or local video file, transcribes the audio, generates a structured summary, extracts action items and key decisions, and supports RAG based Q&A chat over the transcript.

---

## ✨ Features

- 🔊 **Audio Ingestion** — Download and process YouTube videos or local files via yt-dlp
- 📝 **Transcription** — Cloud transcription using Sarvam AI (saaras:v2.5) with automatic 25s chunking to handle API limits
- 🏷️ **Title Generation** — Auto generates a professional meeting title using Mistral LLM
- 📋 **Summarisation** — Map-Reduce summarisation pipeline for long transcripts using Mistral
- ✅ **Action Item Extraction** — Extracts tasks, owners, and deadlines from transcript
- 🔑 **Key Decision Extraction** — Identifies all key decisions made in the meeting
- ❓ **Open Questions** — Surfaces unresolved questions and follow-up topics
- 💬 **RAG Chat** — Ask anything about the meeting using FAISS vector search + Mistral LLM

---

## 🧠 Architecture

```
YouTube URL / Local File
        ↓
   yt-dlp (audio download)
        ↓
   Sarvam AI (speech to text — 25s chunks)
        ↓
   Full Transcript (string)
        ↓
   ┌────────────────┬─────────────────────┐
   ↓                ↓                     ↓
Mistral LLM    Mistral LLM          HuggingFace
(title,        (action items,       all-MiniLM-L6-v2
summary)       decisions,           (embeddings)
               questions)                ↓
                                    FAISS Vector Store
                                         ↓
                                    RAG Chat (Mistral)
        ↓
   Streamlit UI
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| LLM | Mistral AI (mistral-small-latest) via LangChain |
| Speech to Text | Sarvam AI (saaras:v2.5) |
| Embeddings | HuggingFace all-MiniLM-L6-v2 |
| Vector Store | FAISS (in-memory) |
| Audio Processing | yt-dlp, pydub |
| Framework | LangChain |
| Language | Python 3.11+ |

---

## 📁 Project Structure

```
VIDEO AGENT/
├── app.py                  # Main Streamlit UI
├── requirements.txt        # Dependencies
├── .env                    # API keys (not pushed)
├── Core/
│   ├── Transcribe.py       # Sarvam AI + Whisper transcription
│   ├── summarizer.py       # Map-Reduce summarisation
│   ├── extractor.py        # Action items, decisions, questions
│   ├── vector_store.py     # FAISS vector store + embeddings
│   └── rag_engine.py       # RAG chain + Mistral chat
└── utils/
    └── audio_processor.py  # yt-dlp audio download + chunking
```

---

## ⚙️ Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/video-agent.git
cd video-agent
```

### 2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
```env
SARVAM_API_KEY=your_sarvam_api_key
MISTRAL_API_KEY=your_mistral_api_key
```

### 5. Run the app
```bash
streamlit run app.py
```

---

## 🔑 API Keys Required

| Service | Get API Key |
|---|---|
| Sarvam AI | https://www.sarvam.ai |
| Mistral AI | https://console.mistral.ai |

---

## 💡 Key Technical Decisions

**Why FAISS over ChromaDB?**
ChromaDB requires SQLite 3.35+ but Windows Python bundles SQLite 3.31 causing silent crashes. FAISS runs entirely in memory with no SQLite dependency — stable on all platforms.

**Why 25 second audio chunks?**
Sarvam AI's API rejects audio longer than 30 seconds. 25 seconds gives a 5 second safety margin.

**Why Map-Reduce for summarisation?**
Long transcripts exceed LLM token limits. Map-Reduce summarises each chunk individually then combines partial summaries into one final summary.

**Why all-MiniLM-L6-v2 for embeddings?**
Lightweight, fast, runs locally with no API cost, produces 384 dimensional vectors with strong semantic similarity performance.

---

## 🙋 Author

**Avinash Kumar Yadav**
B.Tech CSE — RGPV Bhopal (2025)
📧 yadavavinash200218@gmail.com