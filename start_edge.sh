#!/bin/bash
echo "=== Starting Saksham AI on NVIDIA Jetson Edge ==="

# 1. Check if the pre-installed Ollama service is available on the host Docker gateway
echo "Checking for pre-installed Ollama at http://172.17.0.1:11434..."
OLLAMA_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://172.17.0.1:11434/api/tags || echo "failed")

USE_HOST_OLLAMA=false
if [ "$OLLAMA_STATUS" = "200" ]; then
    echo "SUCCESS: Found pre-installed Ollama service on host (http://172.17.0.1:11434)."
    echo "Using pre-loaded host models (no installation or pull needed)."
    USE_HOST_OLLAMA=true
else
    echo "INFO: Pre-installed Ollama not detected at http://172.17.0.1:11434 (Status: $OLLAMA_STATUS)."
    echo "Falling back to local user-space Ollama setup..."
fi

# 2. Configure .env file with correct OLLAMA_BASE_URL and offline model paths
cd "$HOME/SakshamAi/backend"
touch .env

if [ "$USE_HOST_OLLAMA" = "true" ]; then
    # Set to the host gateway IP
    if grep -q "OLLAMA_BASE_URL" .env; then
        sed -i 's|OLLAMA_BASE_URL=.*|OLLAMA_BASE_URL=http://172.17.0.1:11434|' .env
    else
        echo "OLLAMA_BASE_URL=http://172.17.0.1:11434" >> .env
    fi
else
    # Set to localhost
    if grep -q "OLLAMA_BASE_URL" .env; then
        sed -i 's|OLLAMA_BASE_URL=.*|OLLAMA_BASE_URL=http://localhost:11434|' .env
    else
        echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env
    fi
fi

# Append model paths for offline mode
if ! grep -q "EMBEDDING_MODEL_PATH" .env; then
    echo "EMBEDDING_MODEL_PATH=/home/codex/SakshamAi/backend/data/models/multilingual-e5-small" >> .env
    echo "RERANK_MODEL_PATH=/home/codex/SakshamAi/backend/data/models/ms-marco-MiniLM-L-6-v2" >> .env
    echo "EMBEDDING_LOCAL_FILES_ONLY=true" >> .env
    echo "RERANK_LOCAL_FILES_ONLY=true" >> .env
    echo "OLLAMA_NUM_CTX=2048" >> .env
fi

# 2.5 Ensure offline models are downloaded
if [ ! -f "data/models/multilingual-e5-small/model.safetensors" ] || [ ! -f "data/models/ms-marco-MiniLM-L-6-v2/model.safetensors" ]; then
    echo "INFO: Offline models not found. Downloading them now..."
    python3 scripts/download_models.py
fi

# 3. Setup Ollama (only if NOT using host Ollama)
if [ "$USE_HOST_OLLAMA" = "false" ]; then
    # Install system dependencies (zstd)
    if ! dpkg -s zstd >/dev/null 2>&1; then
        echo "Installing zstd..."
        sudo apt-get update && sudo apt-get install -y zstd
    fi

    # Check if Ollama is installed in user-space or system
    if [ ! -f "/usr/local/bin/ollama" ] && [ ! -f "$HOME/.local/bin/ollama" ]; then
        echo "Downloading and installing Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
        mkdir -p "$HOME/.local/bin"
        cp /usr/local/bin/ollama "$HOME/.local/bin/ollama"
    fi

    # Restore binary if wiped
    if [ ! -f "/usr/local/bin/ollama" ] && [ -f "$HOME/.local/bin/ollama" ]; then
        echo "Restoring Ollama binary..."
        sudo cp "$HOME/.local/bin/ollama" /usr/local/bin/ollama
    fi

    # Restore runner engine libraries if wiped
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

    # Backup for future boots
    if [ -f "/usr/local/bin/ollama" ] && [ ! -f "$HOME/.local/bin/ollama" ]; then
        mkdir -p "$HOME/.local/bin"
        cp /usr/local/bin/ollama "$HOME/.local/bin/ollama"
    fi
    if [ -d "/usr/local/lib/ollama" ] && [ ! -d "$HOME/.local/lib/ollama" ]; then
        mkdir -p "$HOME/.local/lib"
        cp -r /usr/local/lib/ollama "$HOME/.local/lib/ollama"
    fi

    # Start Ollama service in background
    if ! ps aux | grep -v grep | grep -q "ollama serve"; then
        echo "Starting local Ollama service..."
        ollama serve > "$HOME/ollama.log" 2>&1 &
        sleep 5
    fi

    # Ensure model is pulled
    if ! ollama list | grep -q "llama3.2:1b"; then
        echo "Pulling llama3.2:1b model..."
        ollama pull llama3.2:1b
    fi
fi

# 4. Start FastAPI Backend in background
if ! ps aux | grep -v grep | grep -q "uvicorn app:app"; then
    echo "Starting FastAPI backend server..."
    cd "$HOME/SakshamAi/backend"
    export PYTHONPATH="$HOME/.local/lib/python3.10/site-packages"
    python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 > "$HOME/uvicorn.log" 2>&1 &
    sleep 3
fi

# 5. Expose the port using serveo tunnel
echo "Creating public HTTP tunnel..."
echo "Please click the link generated below to access the website:"
ssh -R 80:localhost:8000 serveo.net
