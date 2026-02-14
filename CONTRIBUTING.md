# Contributing to Jarvis AI

Thank you for your interest in contributing! Here's how to get started.

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. **Install** dependencies:
   ```bash
   python -m pip install -r requirements.txt
   cd frontend && npm install
   ```
4. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

```bash
# Backend (auto-reload)
python -m uvicorn server.app:app --reload --port 8080

# Frontend (hot-reload)
cd frontend && npm run dev
```

## Code Style

- **Python**: Follow PEP 8, use docstrings for all public functions
- **JavaScript/React**: Use functional components with hooks
- **Commits**: Use conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`)

## What to Contribute

- 🐛 Bug fixes
- ✨ New tools (add to `tools/` and register in `core/tools.py`)
- 🧠 New LLM providers (extend `core/llm_client.py`)
- 🎨 Dashboard UI improvements
- 📝 Documentation improvements
- 🧪 Tests

## Pull Request Process

1. Update the README if needed
2. Test your changes locally
3. Ensure the frontend builds: `cd frontend && npm run build`
4. Submit a PR with a clear description

## Reporting Issues

Use GitHub Issues with:
- Clear title
- Steps to reproduce
- Expected vs actual behavior
- Python/Node version and OS
