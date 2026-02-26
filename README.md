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
| 🎤 **Voice Interface** | Continuous listening (VAD) → STT (Groq/Whisper/SpeechBrain) → TTS pipeline |
| 💬 **Multi-LLM Support** | Groq, OpenAI, Mistral — switch with one config change |
| 🌍 **Bilingual Mode** | Strict English or Hindi language responses |
| 🚀 **Dynamic Modes** | Switch between Fast Mode (speed) and Deep Research Mode (complex queries) |
| ⚙️ **Extended UI** | User profiles, chat history search, and settings management |
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

**Option A — Enterprise Dashboard Mode** (recommended):

First, start the required Postgres and Redis databases:
```bash
docker-compose -f deploy/docker/docker-compose.yml up postgres redis -d
```

Then, start the FastAPI Backend:
```bash
# Terminal 1: Backend
python -m uvicorn server.app.main:app --reload --port 8000
```

Finally, start the React Frontend:
```bash
# Terminal 2: Frontend
cd frontend && npm run dev
```
Open **http://localhost:5173**

**Option B — Voice Mode** (CLI interface):
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
| `/api/history` | `GET` | Conversation history |
| `/api/trash` | `GET` | View deleted items |

## 📁 Project Structure

```
jarvis-ai/
├── core/                   # UNCHANGED — AI brain, agent, LLM, search
├── server/                 # UPGRADED — Enterprise backend
│   ├── app/                #   ├── REST API, Auth, Billing, Middleware
│   ├── ai/                 #   ├── LangChain agent, memory, token tracking
│   ├── tools/              #   ├── Tool registry + permissions
│   └── legacy_routes.py    #   └── Legacy WebSocket streaming endpoints
├── frontend/               # React.js dashboard
├── deploy/                 # Docker + K8s deployment manifests
├── .github/workflows/      # CI/CD pipelines
├── docs/                   # Architecture + Deployment guides
├── voice/                  # Voice pipeline (STT, TTS, VAD)
├── vision/                 # Computer vision (Screen, Camera OCR)
├── tools/                  # Action tools (Browser, File, System)
├── tests/                  # Pytest test suite
├── config.py               # Shared API Keys & config
└── main.py                 # CLI voice entry point
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
| `STT_ENGINE` | `local` | Speech Engine (`local`, `groq`, `speechbrain`) |

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

- Ensure database is running: `docker-compose -f deploy/docker/docker-compose.yml up postgres redis -d`
- Ensure backend is running: `python -m uvicorn server.app.main:app --port 8000`
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
#
