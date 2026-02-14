# Troubleshooting Guide

## Common Issues & Solutions

### 🎤 Microphone Issues

**Problem: "No microphone detected"**
- **Solution**: Run `python installer/doctor.py` to see available devices
- Check microphone is plugged in
- Try different USB port
- Grant microphone permissions in Windows settings

**Problem: "Invalid sample rate" error**
- **Solution**: The system auto-detects the correct sample rate
- If persists, edit `voice/stt.py` and try different sample rates: 16000, 44100, 48000

**Problem: Wake word not detected**
- **Solution**: 
  - Speak clearly: "Jarvis"
  - System also recognizes phonetic variations: "Javis", "Travis"
  - Increase microphone volume
  - Reduce background noise

---

### 🔑 API Key Issues

**Problem: "No API key found"**
- **Solution**:
  1. Check `.env` file exists in project root
  2. Verify key name: `GROQ_API_KEY` or `OPENAI_API_KEY` or `MISTRAL_API_KEY`
  3. No quotes around the key value
  4. File saved properly

**Problem: "Invalid API key"**
- **Solution**:
  - Regenerate API key from provider dashboard
  - Copy entire key (no extra spaces)
  - Check provider in `config.py` matches your key

**Problem: "Rate limit exceeded"**
- **Solution**:
  - Groq: Wait 60 seconds (free tier limits)
  - OpenAI: Add payment method or reduce usage
  - Switch to different provider temporarily

---

### 🗣️ Speech Issues

**Problem: TTS not working / no sound**
- **Solution**:
  - Check speakers/headphones connected
  - Volume not muted
  - Try different voice in `voice/tts.py`
  - Install edge-tts: `pip install edge-tts`

**Problem: STT transcription is poor**
- **Solution**:
  - Speak clearly and at normal pace
  - Reduce background noise
  - Check microphone positioning (6-12 inches from mouth)
  - Upgrade Whisper model to "medium" or "large" in `voice/stt.py`

---

### 🧠 LLM Issues

**Problem: Responses in wrong language**
- **Solution**: The LLM adapts to input. Specify language in your question: "Answer in English"

**Problem: Slow responses**
- **Solution**:
  - Use Groq (fastest provider)
  - Reduce internet search results in `core/search.py`
  - Check internet connection

**Problem: Generic/poor quality responses**
- **Solution**:
  - Switch to better model (GPT-4, Claude)
  - Add more context to your questions
  - Check memory is working

---

### 💾 Memory Issues

**Problem: Jarvis doesn't remember previous conversations**
- **Solution**:
  - Check `data/memory.json` exists
  - File permissions allow read/write
  - Memory not corrupted (valid JSON)

**Problem: "Memory file not found"**
- **Solution**:
  - Run Jarvis once to auto-create `data/memory.json`
  - Or create empty file: `echo {} > data/memory.json`

---

### 🖥️ HUD Issues

**Problem: HUD not connecting**
- **Solution**:
  1. Ensure `main.py` is running
  2. Open `hud/index.html` in modern browser (Chrome, Edge, Firefox)
  3. Check WebSocket URL: `ws://localhost:8000`
  4. Check firewall not blocking port 8000

**Problem: HUD shows wrong state**
- **Solution**: Refresh the browser page

---

### 👁️ Vision Issues

**Problem: "Tesseract not found"**
- **Solution**:
  - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
  - Install Tesseract-OCR
  - Add to PATH or set path in `vision/screen_reader.py`

**Problem: Screen capture fails**
- **Solution**:
  - Check `mss` installed: `pip install mss`
  - Grant screen recording permissions (macOS)
  - Try different monitor number

**Problem: Camera not working**
- **Solution**:
  - Check camera connected and not in use
  - Grant camera permissions
  - Try different camera index in `vision/camera_analysis.py`

---

### 📦 Installation Issues

**Problem: Dependencies fail to install**
- **Solution**:
  ```bash
  pip install --upgrade pip
  pip install -r requirements.txt --no-cache-dir
  ```

**Problem: Import errors**
- **Solution**:
  - Verify you're in correct directory
  - Check `__init__.py` files exist
  - Reinstall package: `pip install -e .`

---

### ⚙️ General Issues

**Problem: High CPU/Memory usage**
- **Solution**:
  - Whisper model uses significant resources
  - Close other applications
  - Use smaller Whisper model ("tiny" or "small")

**Problem: Jarvis crashes unexpectedly**
- **Solution**:
  - Check logs for errors
  - Verify all dependencies installed
  - Run `python installer/doctor.py`
  - Create GitHub issue with error details

---

## Getting Help

1. **Check logs**: Look for error messages in console
2. **Run doctor**: `python installer/doctor.py`
3. **Update dependencies**: `pip install -r requirements.txt --upgrade`
4. **Restart**: Close and restart Jarvis
5. **Create Issue**: If problem persists, create GitHub issue with:
   - Error message
   - Doctor output
   - Steps to reproduce

## Performance Tips

- Use Groq for fastest responses
- Use "small" Whisper model for speed
- Reduce search results limit
- Close unnecessary applications
- Good internet connection recommended
