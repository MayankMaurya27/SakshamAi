#!/bin/bash
echo "=== Starting Saksham AI on NVIDIA Jetson Edge ==="

# 1. Check and install system dependencies (zstd)
if ! dpkg -s zstd >/dev/null 2>&1; then
    echo "Installing zstd..."
    sudo apt-get update && sudo apt-get install -y zstd
fi

# 2. Check if Ollama is installed on system, or in our persistent backup
if [ ! -f "/usr/local/bin/ollama" ] && [ ! -f "$HOME/.local/bin/ollama" ]; then
    echo "Downloading and installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    mkdir -p "$HOME/.local/bin"
    cp /usr/local/bin/ollama "$HOME/.local/bin/ollama"
fi

# If system binary is missing but we have the backup, restore it
if [ ! -f "/usr/local/bin/ollama" ] && [ -f "$HOME/.local/bin/ollama" ]; then
    echo "Restoring Ollama binary..."
    sudo cp "$HOME/.local/bin/ollama" /usr/local/bin/ollama
fi

# 3. Check and restore Ollama libraries/engine
if [ ! -d "/usr/local/lib/ollama" ]; then
    if [ -d "$HOME/.local/lib/ollama" ]; then
        echo "Restoring Ollama runner engine from persistent storage..."
        sudo mkdir -p /usr/local/lib
        sudo cp -r "$HOME/.local/lib/ollama" /usr/local/lib/ollama
    else
        echo "Installing Ollama engine files..."
        curl -fsSL https://ollama.com/install.sh | sh
        mkdir -p "$HOME/.local/lib"
        cp -r /usr/local/lib/ollama "$HOME/.local/lib/ollama"
    fi
fi

# Double check that we have backed up both bin and lib for future boots
if [ -f "/usr/local/bin/ollama" ] && [ ! -f "$HOME/.local/bin/ollama" ]; then
    mkdir -p "$HOME/.local/bin"
    cp /usr/local/bin/ollama "$HOME/.local/bin/ollama"
fi
if [ -d "/usr/local/lib/ollama" ] && [ ! -d "$HOME/.local/lib/ollama" ]; then
    mkdir -p "$HOME/.local/lib"
    cp -r /usr/local/lib/ollama "$HOME/.local/lib/ollama"
fi

# 4. Start Ollama in background if not already running
if ! ps aux | grep -v grep | grep -q "ollama serve"; then
    echo "Starting Ollama service..."
    ollama serve > "$HOME/ollama.log" 2>&1 &
    sleep 5
fi

# 5. Start FastAPI Backend in background if not already running
if ! ps aux | grep -v grep | grep -q "uvicorn app:app"; then
    echo "Starting FastAPI backend server..."
    cd "$HOME/SakshamAi/backend"
    export PYTHONPATH="$HOME/.local/lib/python3.10/site-packages"
    python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 > "$HOME/uvicorn.log" 2>&1 &
    sleep 3
fi

# 6. Expose the port using serveo tunnel
echo "Creating public HTTP tunnel..."
echo "Please click the link generated below to access the website:"
ssh -R 80:localhost:8000 serveo.net
