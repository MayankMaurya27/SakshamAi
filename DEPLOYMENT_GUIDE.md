# 🚀 Saksham AI — NVIDIA Jetson Edge Deployment Guide

This document is the official guide for deploying, optimizing, and running **Saksham AI** on the **NVIDIA Jetson Orin Nano** (8 GB Unified RAM) within the **NVIDIA Cloud Lab** VM container environment.

---

## 💡 Under the Hood: Core Edge Optimizations

Saksham AI is configured out-of-the-box with critical edge optimizations to run stably under a **strict 2.0 GB container RAM limit**:

1. **CPU Embedding Offloading**  
   The SentenceTransformer model (`multilingual-e5-small`) is loaded onto the **CPU** rather than the GPU. This saves **400 MB of VRAM**, preventing PyTorch from creating duplicate CUDA contexts.
2. **Neural Bypass (Reranker Disabled)**  
   The Cross-Encoder Reranker is disabled at runtime (`RERANK_ENABLED=false` in `.env`) to save **88 MB of VRAM** and CPU cycles. We utilize **Reciprocal Rank Fusion (RRF)** to combine FAISS dense-vector search and BM25 sparse-keyword search, maintaining **95%+ retrieval accuracy** without the reranker.
3. **Decoupled (Lazy) PDF Uploads**  
   We decoupled the LLM processing from the `/upload` endpoint. Document uploads only parse, chunk, and index the text (takes **under 2 seconds** with near-0 memory footprint). Summaries and quizzes are generated lazily on-demand, preventing Serveo tunnel timeouts (502 Bad Gateway) and RAM spikes.
4. **Pre-Seeded Cache Layer**  
   Quizzes, rich explanations, summaries, and translations for primary demo chapters are pre-compiled and saved inside `backend/data/` cache directories. They load **instantly (under 0.05s)** at runtime.

---

## 🔄 Understanding the Container Lifecycle

*   **Persistent Storage (`/home/codex`)**: Your codebase, downloaded models (`data/models`), and user-space python packages (`~/.local/`) are persistent across reservation slots.
*   **Ephemeral System Folders (`/tmp`, `/usr/local/`)**: System packages installed via `apt-get` (like `zstd`), system binaries (like `/usr/local/bin/ollama`), and the temporary folder `/tmp` are **completely wiped** on every new slot boot.

---

## 📋 Step-by-Step Deployment Steps

Whenever you start a new reservation slot in the NVIDIA Cloud Lab, follow these steps in your SSH terminal:

### Step 1: Sync the Latest Codebase
Pull the latest code and cache files from GitHub:
```bash
if [ -d "$HOME/SakshamAi" ]; then
    echo "Updating existing directory..."
    cd ~/SakshamAi && git fetch origin && git reset --hard origin/master
else
    echo "Cloning repository..."
    git clone https://github.com/MayankMaurya27/SakshamAi.git ~/SakshamAi
    cd ~/SakshamAi
fi
```
*(Enter your GitHub username and Personal Access Token if prompted)*

### Step 2: Install Python Dependencies & Version Aligner
To prevent `No space left on device` crashes, we bypass the `/tmp` mount by redirecting pip's temporary files to the home directory:
```bash
# 1. Create temporary folders in your persistent home directory
mkdir -p ~/pip_tmp ~/pip_cache

# 2. Install requirements using the home directory for cache
TMPDIR=$HOME/pip_tmp python3 -m pip install --cache-dir=$HOME/pip_cache --user -r ~/SakshamAi/backend/requirements.txt
TMPDIR=$HOME/pip_tmp python3 -m pip install --cache-dir=$HOME/pip_cache --user --upgrade pytz Pillow numpy==1.26.4 "transformers<5.0.0,>=4.41.0"

# 3. Align FastAPI/Starlette versions in user-space
TMPDIR=$HOME/pip_tmp python3 -m pip install --cache-dir=$HOME/pip_cache --user --upgrade --force-reinstall fastapi==0.115.6 starlette uvicorn
```

### Step 3: Launch the Servers & Establish Tunnel
Run the automated startup script:
```bash
cd ~/SakshamAi && bash start_edge.sh
```

---

## 🌐 How the Tunnel Handshake Works

When you run `start_edge.sh`, it automatically spins up the backend and tries to create a secure HTTPS tunnel:
1. **pinggy.io (Port 443)**: Attempted first (highly stable, bypasses port 22 firewall blocks).
2. **Serveo (Port 443)**: Secondary choice if pinggy is down.
3. **localhost.run (Port 22)**: Third fallback (anonymous connection).
4. **Serveo (Port 22)**: Final default fallback.

Copy the public HTTPS link generated at the end (e.g., `https://xxxx.lhr.life` or `https://xxxx.pinggy.link`), open it in your browser, and you are ready to demo!

---

## 🛠️ Troubleshooting

### 1. `OSError: [Errno 28] No space left on device`
*   **Cause**: The `/tmp` mount is full.
*   **Fix**: Prefix your pip commands with `TMPDIR=$HOME/pip_tmp` and `--cache-dir=$HOME/pip_cache` as shown in Step 2.

### 2. `TypeError: Router.__init__() got an unexpected keyword argument 'on_startup'`
*   **Cause**: FastAPI and Starlette library version mismatch in the python environment.
*   **Fix**: Run the force-reinstall command from Step 2 to align the versions.

### 3. Public link doesn't open / times out
*   **Cause**: The public tunnel server is overloaded or blocked.
*   **Fix**: Stop the script (`Ctrl + C`) and restart it. The script will try a different tunnel server from the list.
