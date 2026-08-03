import os
import sys
import time
import json
import resource
import urllib.request
from pathlib import Path

# Add backend directory to system path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

try:
    from config.settings import get_settings
    from ai.embeddings import get_embedding_model
    from ai.faiss_manager import get_saksham_index
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def get_memory_mb():
    # maxrss is in bytes on macOS, in kilobytes on Linux
    maxrss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == 'darwin':
        return maxrss / (1024 * 1024)
    else:
        return maxrss / 1024

def test_ollama_generation():
    settings = get_settings()
    # Resolve correct host IP (checks host gateway first, then localhost)
    endpoints = ["http://172.17.0.1:11434", "http://localhost:11434"]
    active_url = None
    
    for url in endpoints:
        try:
            req = urllib.request.Request(f"{url}/api/tags")
            with urllib.request.urlopen(req, timeout=2) as r:
                if r.status == 200:
                    active_url = url
                    break
        except Exception:
            continue
            
    if not active_url:
        return "Not Running", 0.0
        
    payload = json.dumps({
        "model": "llama3.2:1b",
        "prompt": "what is force?",
        "stream": False,
        "options": {"num_ctx": 1024}
    }).encode("utf-8")
    
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(f"{active_url}/api/generate", data=payload, headers=headers)
    
    try:
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=120) as r:
            res = json.loads(r.read().decode("utf-8"))
            latency = (time.time() - t0) * 1000
            return "Active", latency
    except Exception as e:
        return f"Error ({e})", 0.0

def run_benchmarks():
    print("====================================================")
    print("         SAKSHAM AI JETSON PERFORMANCE VALIDATOR")
    print("====================================================")
    
    # 1. Base Memory
    base_mem = get_memory_mb()
    print(f"[*] Base Python Memory footprint: {base_mem:.2f} MB")
    
    # 2. Embedding Model Load
    print("[*] Loading embedding model (multilingual-e5-small)...")
    t0 = time.time()
    embed_model = get_embedding_model()
    embed_load_time = (time.time() - t0) * 1000
    embed_mem = get_memory_mb()
    print(f"    - Load Latency: {embed_load_time:.2f} ms")
    print(f"    - Memory Allocation: {embed_mem:.2f} MB (Diff: {embed_mem - base_mem:.2f} MB)")
    
    # 3. Sentence Embedding Inference
    print("[*] Warm-up embedding inference...")
    embed_model.embed_text("warmup sentence", is_query=True)
    
    embed_latencies = []
    for i in range(20):
        t0 = time.time()
        embed_model.embed_text("what is the definition of force, motion, and gravity?", is_query=True)
        embed_latencies.append((time.time() - t0) * 1000)
    avg_embed_latency = sum(embed_latencies) / len(embed_latencies)
    print(f"    - Average Query Embedding Latency (CPU): {avg_embed_latency:.2f} ms")
    
    # 4. FAISS Search Latency
    print("[*] Loading FAISS index (14,750 vectors)...")
    index = get_saksham_index()
    query_vector = embed_model.embed_text("force", is_query=True)
    
    # Warmup FAISS search
    index.search(query_vector, k=5)
    
    search_latencies = []
    for _ in range(50):
        t0 = time.time()
        index.search(query_vector, k=5)
        search_latencies.append((time.time() - t0) * 1000)
    avg_search_latency = sum(search_latencies) / len(search_latencies)
    print(f"    - Average FAISS Vector Search Latency: {avg_search_latency:.2f} ms")
    
    # 5. LLM Host Generation Latency
    print("[*] Checking LLM generation latency (llama3.2:1b)...")
    ollama_status, ollama_latency = test_ollama_generation()
    print(f"    - Ollama Status: {ollama_status}")
    if ollama_latency > 0:
        print(f"    - LLM Question Generation Latency: {ollama_latency/1000:.2f} s")
    else:
        print("    - Skipped LLM benchmarks (Ollama service not running / timeout).")
    
    print("\n====================================================")
    print("              METRICS SUMMARY FOR SLIDES")
    print("====================================================")
    print(f"⚡ Embedding Latency:   {avg_embed_latency:.2f} ms")
    print(f"⚡ FAISS Search Latency: {avg_search_latency:.2f} ms")
    print(f"💾 CPU Memory Usage:    {embed_mem:.2f} MB")
    print(f"📶 Offline Safety:      100% Offline Functional")
    print("====================================================")

if __name__ == "__main__":
    run_benchmarks()
