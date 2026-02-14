#!/bin/bash
# Linux/Mac Installer for Jarvis AI

echo "========================================"
echo "   JARVIS AI - Linux/Mac Installer"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found!"
    echo "Please install Python 3.8+ using your package manager"
    exit 1
fi

echo "[1/5] Python detected"
python3 --version

# Install dependencies
echo ""
echo "[2/5] Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

echo "[3/5] Dependencies installed successfully"

# Check for .env file
if [ ! -f .env ]; then
    echo ""
    echo "[4/5] Creating .env file from template..."
    cp .env.example .env
    echo "[IMPORTANT] Please edit .env and add your API key"
else
    echo "[4/5] .env file already exists"
fi

# Create data directory
mkdir -p data

# Create empty memory file if needed
if [ ! -f data/memory.json ]; then
    echo "{}" > data/memory.json
    echo "[5/5] Created memory file"
else
    echo "[5/5] Memory file exists"
fi

echo ""
echo "========================================"
echo "   Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API key"
echo "2. Run: python3 installers/doctor.py (to verify)"
echo "3. Run: python3 main.py (to start Jarvis)"
echo ""
