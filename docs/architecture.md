# Jarvis AI - System Architecture

## Overview

Jarvis AI is a multi-modal voice assistant with vision capabilities, designed to understand and execute complex tasks through natural language interaction.

## System Components

### 1. Voice Processing
- **STT (Speech-to-Text)**: Whisper-based transcription
- **TTS (Text-to-Speech)**: Edge-TTS with natural voices
- **Wake Word Detection**: Continuous listening for activation

### 2. Core Intelligence
- **Agent**: Main orchestrator coordinating all components
- **Brain**: Combines internet search + LLM reasoning
- **LLM Client**: Multi-provider support (Groq, OpenAI, Mistral)
- **Memory**: Persistent conversation and fact storage
- **Planner**: Breaks down complex tasks into steps

### 3. Vision Capabilities
- **Screen Reader**: OCR-based text extraction from screen
- **Screen Analyzer**: Semantic understanding of UI elements
- **Image Analyzer**: Analyze images from files
- **Camera Analyzer**: Real-time camera feed analysis

### 4. Tool Execution
- **Browser Tools**: Open URLs, search Google
- **File Tools**: Read, write, list files
- **System Tools**: Execute commands, get system info
- **Vision Tools**: Screen reading, image analysis

## Data Flow

```
User Speech → STT → Agent → Intent Router
                              ↓
                    ┌─────────┴─────────┐
                    ↓                   ↓
                Brain (Search+LLM)    Tool Execution
                    ↓                   ↓
                Response ← Memory ← Results
                    ↓
                  TTS → Speech Output
```

## Component Interactions

- **main.py**: Entry point, manages main loop
- **Agent**: Coordinates all operations
- **Brain**: Handles reasoning and knowledge
- **Tools**: Execute actions in the real world
- **Memory**: Provides context and learning
- **State Manager**: Tracks current state (IDLE, LISTENING, THINKING, SPEAKING)

## Technology Stack

- **Voice**: faster-whisper, edge-tts
- **Vision**: pytesseract, OpenCV, mss
- **LLM**: Groq/OpenAI/Mistral APIs
- **Search**: DuckDuckGo
- **UI**: WebSocket-based HUD

## Security

- Input validation for all user inputs
- Path traversal protection
- Command execution safety checks
- File size limits
- System directory protection
