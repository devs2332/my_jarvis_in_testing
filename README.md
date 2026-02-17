# <img src="https://img.shields.io/badge/🤖-JARVIS%20AI-blue?style=for-the-badge" alt="Jarvis AI" />

<div align="center">

**Advanced Voice-Activated AI Assistant with RAG & Vector Memory**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20DB-FF6F00?style=flat-square)](https://www.trychroma.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

<br />

[Features](#-features) · [Architecture](#-architecture) · [Quick Start](#-quick-start) · [Dashboard](#-dashboard) · [API](#-api-endpoints) · [Contributing](#-contributing)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **RAG Pipeline** | Retrieval-Augmented Generation with vector memory context |
| �️ **Vector Memory** | ChromaDB-powered semantic search across all conversations |
| ⚡ **Streaming Responses** | Token-by-token LLM streaming via WebSocket |
| 🎨 **React Dashboard** | Modern dark-themed UI with chat, knowledge base & system status |
| 🌐 **FastAPI Backend** | REST + WebSocket API with full CORS support |
| 🎤 **Voice Interface** | Wake word detection → STT (Whisper) → TTS pipeline |
| 💬 **Multi-LLM Support** | Groq, OpenAI, Mistral — switch with one config change |
| 🔍 **Web Search** | DuckDuckGo integration for real-time information |
| 🛠️ **Tool System** | Extensible registry for browser, file, and system tools |
| 📋 **Task Planner** | LLM-powered multi-step task decomposition & execution |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React.js Dashboard                       │
│            Chat  │  Knowledge Base  │  System Status        │
└────────────┬────────────┬───────────────────────────────────┘
             │ REST       │ WebSocket (streaming)
┌────────────▼────────────▼───────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │  Agent   │  │  Brain   │  │  Tools   │  │  Planner   │  │
│  └────┬─────┘  └────┬─────┘  └──────────┘  └────────────┘  │
│       │            │ RAG                                    │
│  ┌────▼────────────▼─────┐  ┌────────────┐                 │
│  │ ChromaDB Vector Store │  │ JSON Memory│                  │
│  └───────────────────────┘  └────────────┘                  │
└─────────────────────────────────────────────────────────────┘
         │                              │
   ┌─────▼─────┐                 ┌──────▼──────┐
   │ LLM APIs  │                 │ DuckDuckGo  │
   │ Groq/OAI  │                 │   Search    │
   └───────────┘                 └─────────────┘
```

## � Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+ (for dashboard)
- An LLM API key ([Groq](https://console.groq.com/) is free)

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/jarvis-ai.git
cd jarvis-ai

# Python dependencies
python -m pip install -r requirements.txt

# React dashboard
cd frontend && npm install && cd ..
```

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env` with your API key(s):

```env
GROQ_API_KEY=gsk_your_key_here
```

Set your provider in `config.py`:

```python
LLM_PROVIDER = "groq"  # or "openai" or "mistral"
```

### 3. Run

**Option A — Dashboard Mode** (recommended):
```bash
# Terminal 1: Backend
python -m uvicorn server.app:app --reload --port 8080

# Terminal 2: Frontend
cd frontend && npm run dev
```
Open **http://localhost:5173**

**Option B — Voice Mode**:
```bash
python main.py
```

## 🎨 Dashboard

The React dashboard provides three views:

| View | Description |
|------|-------------|
| 💬 **Chat** | Send messages with real-time streaming responses |
| 🧠 **Knowledge Base** | Semantic search across all stored conversations |
| 📊 **System Status** | LLM provider, vector DB stats, registered tools |

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | `GET` | Health check |
| `/api/status` | `GET` | System status & stats |
| `/api/chat` | `POST` | Send message → get response |
| `/ws/chat` | `WebSocket` | Streaming token-by-token |
| `/api/memory` | `GET` | List stored memories |
| `/api/memory/search?q=` | `GET` | Semantic similarity search |
| `/api/facts` | `GET` | Key-value facts |
| `/api/conversations` | `GET` | Conversation history |

## 📁 Project Structure

```
jarvis-ai/
├── server/                 # FastAPI backend
│   ├── app.py             # Application + middleware
│   └── routes.py          # REST + WebSocket endpoints
├── core/                   # AI engine
│   ├── agent.py           # Orchestrator (sync + async streaming)
│   ├── brain.py           # RAG pipeline: search → memory → LLM
│   ├── vector_memory.py   # ChromaDB semantic vector store
│   ├── llm_client.py      # Multi-provider LLM (Groq/OpenAI/Mistral)
│   ├── memory.py          # JSON key-value memory
│   ├── reasoning.py       # Context-aware prompt builder
│   ├── planner.py         # Multi-step task planner
│   ├── tools.py           # Unified tool registry
│   └── search.py          # DuckDuckGo web search
├── frontend/               # React.js dashboard
│   ├── src/App.jsx        # Main dashboard (Chat, KB, Status)
│   ├── src/index.css      # Dark theme design system
│   └── vite.config.js     # Vite + API proxy config
├── voice/                  # Voice pipeline
│   ├── stt.py             # Speech-to-text (Whisper)
│   ├── tts.py             # Text-to-speech (Edge TTS)
│   └── wake_word.py       # "Jarvis" wake word detection
├── vision/                 # Computer vision
│   ├── screen_reader.py   # Screen OCR capture
│   ├── image_analysis.py  # Image analysis
│   └── camera_analysis.py # Camera feed analysis
├── tools/                  # Action tools
│   ├── browser.py         # Web browsing
│   ├── files.py           # File operations
│   └── system.py          # System commands
├── config.py              # All configuration
├── main.py                # Voice mode entry point
└── requirements.txt       # Python dependencies
```

## 🔧 Configuration

All settings in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `LLM_PROVIDER` | `"groq"` | LLM provider (`groq`, `openai`, `mistral`) |
| `VECTOR_DB_DIR` | `data/vector_db` | ChromaDB persist directory |
| `SERVER_PORT` | `8080` | FastAPI server port |
| `MEMORY_FILE` | `memory.json` | JSON memory file path |

## 🐛 Troubleshooting

<details>
<summary><b>"No API key found"</b></summary>

- Verify `.env` file exists in root directory
- Check the key matches your provider in `config.py`
- Get a free key at [console.groq.com](https://console.groq.com/)
</details>

<details>
<summary><b>"Invalid sample rate" error</b></summary>

- System auto-detects microphone sample rate
- Run `python installer/doctor.py` to check audio devices
</details>

<details>
<summary><b>Dashboard not loading</b></summary>

- Ensure backend is running: `python -m uvicorn server.app:app --port 8080`
- Ensure frontend is running: `cd frontend && npm run dev`
- Check browser console for errors
</details>

<details>
<summary><b>ChromaDB first-run is slow</b></summary>

- First import downloads the embedding model (~80MB)
- Subsequent starts are fast
</details>

## 🔐 Privacy & Security

- 🏠 All voice processing happens **locally** (Whisper)
- 🔒 API keys stored in `.env` (git-ignored)
- 💾 Vector memory stored **locally** in ChromaDB
- 🚫 No telemetry or data collection
- 🌐 Internet only for LLM API calls and web search

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ | Inspired by JARVIS from Iron Man**

⭐ Star this repo if you find it useful!

</div>
#   m y _ j a r v i s _ i n _ t e s t i n g  
 #   m y _ j a r v i s _ i n _ t e s t i n g  
 