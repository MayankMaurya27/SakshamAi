"""
Generates saksham_ai_architecture.excalidraw — importable into excalidraw.com
Run from the repo root: python scripts/gen_excalidraw.py
"""
import json, random, os

elements = []
counter = [0]

def uid():
    counter[0] += 1
    return f"el{counter[0]:05d}"

def add(elem):
    elements.append(elem)

def mk_rect(x, y, w, h, label, stroke="#1e40af", bg="#dbeafe", fs=13, sw=2, rounded=True):
    rid = uid()
    tid = uid()
    lines = label.count("\n") + 1
    th = fs * 1.25 * lines + 4
    ty = y + (h - th) / 2
    add({
        "id": rid, "type": "rectangle",
        "x": x, "y": y, "width": w, "height": h, "angle": 0,
        "strokeColor": stroke, "backgroundColor": bg, "fillStyle": "solid",
        "strokeWidth": sw, "strokeStyle": "solid", "roughness": 0, "opacity": 100,
        "groupIds": [], "frameId": None,
        "roundness": {"type": 3} if rounded else None,
        "seed": random.randint(1, 999999), "version": 1, "versionNonce": random.randint(1, 999999),
        "isDeleted": False, "boundElements": [{"type": "text", "id": tid}],
        "updated": 1700000000000, "link": None, "locked": False
    })
    add({
        "id": tid, "type": "text",
        "x": x, "y": ty, "width": w, "height": th, "angle": 0,
        "strokeColor": stroke, "backgroundColor": "transparent", "fillStyle": "solid",
        "strokeWidth": 1, "strokeStyle": "solid", "roughness": 0, "opacity": 100,
        "groupIds": [], "frameId": None, "roundness": None,
        "seed": random.randint(1, 999999), "version": 1, "versionNonce": random.randint(1, 999999),
        "isDeleted": False, "boundElements": [],
        "updated": 1700000000000, "link": None, "locked": False,
        "fontSize": fs, "fontFamily": 2, "text": label,
        "textAlign": "center", "verticalAlign": "middle",
        "containerId": rid, "originalText": label, "lineHeight": 1.25
    })
    return rid, x, y, w, h

def mk_arrow(x1, y1, x2, y2, color="#374151", dash=False):
    bx = min(x1, x2); by = min(y1, y2)
    add({
        "id": uid(), "type": "arrow",
        "x": bx, "y": by,
        "width": abs(x2 - x1), "height": abs(y2 - y1), "angle": 0,
        "strokeColor": color, "backgroundColor": "transparent", "fillStyle": "solid",
        "strokeWidth": 2, "strokeStyle": "dashed" if dash else "solid",
        "roughness": 0, "opacity": 100,
        "groupIds": [], "frameId": None, "roundness": {"type": 2},
        "seed": random.randint(1, 999999), "version": 1, "versionNonce": random.randint(1, 999999),
        "isDeleted": False, "boundElements": [],
        "updated": 1700000000000, "link": None, "locked": False,
        "points": [[x1 - bx, y1 - by], [x2 - bx, y2 - by]],
        "lastCommittedPoint": None,
        "startBinding": None, "endBinding": None,
        "startArrowhead": None, "endArrowhead": "arrow"
    })

def mk_text(x, y, w, h, label, color="#1e1e1e", fs=14, align="center"):
    add({
        "id": uid(), "type": "text",
        "x": x, "y": y, "width": w, "height": h, "angle": 0,
        "strokeColor": color, "backgroundColor": "transparent", "fillStyle": "solid",
        "strokeWidth": 1, "strokeStyle": "solid", "roughness": 0, "opacity": 100,
        "groupIds": [], "frameId": None, "roundness": None,
        "seed": random.randint(1, 999999), "version": 1, "versionNonce": random.randint(1, 999999),
        "isDeleted": False, "boundElements": [],
        "updated": 1700000000000, "link": None, "locked": False,
        "fontSize": fs, "fontFamily": 2, "text": label,
        "textAlign": align, "verticalAlign": "middle",
        "containerId": None, "originalText": label, "lineHeight": 1.25
    })

def mk_bg(x, y, w, h, stroke, bg, sw=2, rounded=True):
    add({
        "id": uid(), "type": "rectangle",
        "x": x, "y": y, "width": w, "height": h, "angle": 0,
        "strokeColor": stroke, "backgroundColor": bg, "fillStyle": "solid",
        "strokeWidth": sw, "strokeStyle": "solid", "roughness": 0, "opacity": 100,
        "groupIds": [], "frameId": None,
        "roundness": {"type": 3} if rounded else None,
        "seed": random.randint(1, 999999), "version": 1, "versionNonce": random.randint(1, 999999),
        "isDeleted": False, "boundElements": [],
        "updated": 1700000000000, "link": None, "locked": False
    })

def mk_line(x1, y1, x2, y2, color="#94a3b8", sw=1, dash=False):
    bx = min(x1, x2); by = min(y1, y2)
    add({
        "id": uid(), "type": "line",
        "x": bx, "y": by,
        "width": abs(x2 - x1), "height": abs(y2 - y1), "angle": 0,
        "strokeColor": color, "backgroundColor": "transparent", "fillStyle": "solid",
        "strokeWidth": sw, "strokeStyle": "dashed" if dash else "solid",
        "roughness": 0, "opacity": 100,
        "groupIds": [], "frameId": None, "roundness": None,
        "seed": random.randint(1, 999999), "version": 1, "versionNonce": random.randint(1, 999999),
        "isDeleted": False, "boundElements": [],
        "updated": 1700000000000, "link": None, "locked": False,
        "points": [[x1 - bx, y1 - by], [x2 - bx, y2 - by]],
        "lastCommittedPoint": None,
        "startBinding": None, "endBinding": None,
        "startArrowhead": None, "endArrowhead": None
    })


# ============================================================
# TITLE
# ============================================================
mk_text(100, 10, 1340, 42, "SAKSHAM AI — System Architecture", "#0f172a", 27)
mk_text(100, 54, 1340, 22,
        "Offline-First RAG Educational Assistant for NCERT/CBSE Classes 6–10  •  FastAPI + FAISS + BM25 + Ollama (llama3.2:1b) + Piper TTS",
        "#64748b", 12)

# ============================================================
# BUILD PHASE
# ============================================================
mk_bg(35, 84, 1175, 325, "#d97706", "#fffbeb", sw=2)
mk_text(52, 92, 600, 22, "⚡  BUILD PHASE — One-time Knowledge Ingestion (run ingest_curriculum.py)", "#92400e", 12)

BY1 = 125; BH = 74
mk_rect(60,  BY1, 180, BH, "NCERT PDFs\nClasses 6–10",           "#92400e", "#fde68a")
mk_rect(300, BY1, 180, BH, "PDF Parser\n(PyMuPDF)",               "#92400e", "#fde68a")
mk_rect(540, BY1, 196, BH, "Section-Aware\nChunker",              "#92400e", "#fde68a")
mk_rect(796, BY1, 248, BH, "Embedder\n(multilingual-e5-small)",   "#92400e", "#fde68a")

mk_arrow(60+180,  BY1+37, 300,      BY1+37, "#b45309")
mk_arrow(300+180, BY1+37, 540,      BY1+37, "#b45309")
mk_arrow(540+196, BY1+37, 796,      BY1+37, "#b45309")

BY2 = 273; BH2 = 68
mk_rect(60,  BY2, 212, BH2, "FAISS Vector Index\nsaksham_index.faiss",    "#1e40af", "#dbeafe")
mk_rect(320, BY2, 212, BH2, "BM25 Keyword Index\nbm25_index.json",         "#065f46", "#d1fae5")
mk_rect(580, BY2, 212, BH2, "Metadata Store\nindex_meta.json",             "#5b21b6", "#ede9fe")
mk_rect(840, BY2, 212, BH2, "Curriculum Manifest\nmanifest.json",          "#9f1239", "#ffe4e6")

emb_cx = 796 + 124   # center-x of Embedder
emb_by = BY1 + BH    # bottom-y of Embedder
for sx in [60+106, 320+106, 580+106, 840+106]:
    mk_arrow(emb_cx, emb_by, sx, BY2, "#b45309")

# ============================================================
# DIVIDER
# ============================================================
mk_line(35, 422, 1510, 422, "#94a3b8", 2, dash=True)
mk_text(480, 427, 580, 26, "── RUNTIME — Every Student Request ──", "#64748b", 12)

# ============================================================
# RUNTIME PHASE BACKGROUND
# ============================================================
mk_bg(35, 460, 1175, 590, "#0891b2", "#f0f9ff", sw=2)
mk_text(52, 468, 500, 22, "🚀  RUNTIME RAG PIPELINE — Query Phase", "#0c4a6e", 12)

# ---- Input row ----
RTY = 500; RTH = 74
mk_rect(60,  RTY, 208, RTH, "Student Question\n+ Class + Subject + Chapter", "#0c4a6e", "#bae6fd")
mk_rect(328, RTY, 192, RTH, "Question Router\n(STRICT vs GUIDED)",            "#0c4a6e", "#bae6fd")
mk_rect(580, RTY, 192, RTH, "Chapter\nValidator",                              "#0c4a6e", "#bae6fd")

mk_arrow(60+208,  RTY+37, 328, RTY+37, "#0891b2")
mk_arrow(328+192, RTY+37, 580, RTY+37, "#0891b2")

# Validator → Hybrid (downward)
val_cx = 580 + 96
mk_arrow(val_cx, RTY + RTH, val_cx, 615, "#0891b2")

# ---- Hybrid Retrieval Engine ----
mk_bg(60, 615, 740, 270, "#10b981", "#ecfdf5", sw=2)
mk_text(76, 622, 420, 20, "🔍  Hybrid Retrieval Engine", "#065f46", 11)

HY = 650; HH = 60
mk_rect(80,  HY,      198, HH, "Semantic Search\n(FAISS cosine)",        "#1e40af", "#dbeafe", fs=12)
mk_rect(80,  HY+82,   198, HH, "BM25 Keyword\nSearch",                   "#065f46", "#d1fae5", fs=12)
mk_rect(336, HY+30,   198, HH, "Reciprocal Rank\nFusion (RRF, k=60)",    "#7c3aed", "#ede9fe", fs=12)
mk_rect(592, HY,      190, HH, "Phrase Boost",                            "#b45309", "#fef3c7", fs=12)
mk_rect(592, HY+82,   190, HH, "CrossEncoder\nReranker (optional)",       "#9f1239", "#ffe4e6", fs=12)

mk_arrow(80+198, HY+30,  336, HY+60, "#10b981")   # Semantic → RRF
mk_arrow(80+198, HY+112, 336, HY+60, "#10b981")   # BM25    → RRF
mk_arrow(336+198, HY+60, 592, HY+30, "#10b981")   # RRF     → Boost
mk_arrow(336+198, HY+60, 592, HY+112,"#10b981")   # RRF     → Reranker

# Hybrid right edge → Context Cleaner
mk_arrow(60+740, 615+135, 870, RTY+37, "#10b981")

# ---- Generation Pipeline (right column) ----
GX = 870; GY = RTY; GW = 215; GH = 72; GGAP = 87
mk_rect(GX, GY,           GW, GH, "Context Cleaner\n& Token Budget",     "#4338ca", "#e0e7ff", fs=12)
mk_rect(GX, GY+GGAP,      GW, GH, "Prompt Builder\n(STRICT / GUIDED)",   "#4338ca", "#e0e7ff", fs=12)
mk_rect(GX, GY+GGAP*2,    GW, GH, "Ollama LLM\n(llama3.2:1b)",           "#7c3aed", "#ede9fe", fs=12)
mk_rect(GX, GY+GGAP*3,    GW, GH, "Answer Formatter",                    "#4338ca", "#e0e7ff", fs=12)
mk_rect(GX-20, GY+GGAP*4+5, GW+40, 78, "📤 Final Answer\nto Student",   "#059669", "#d1fae5", fs=14, sw=3)

gcx = GX + GW // 2
mk_arrow(gcx, GY+GH,         gcx, GY+GGAP,        "#4338ca")
mk_arrow(gcx, GY+GGAP+GH,    gcx, GY+GGAP*2,      "#4338ca")
mk_arrow(gcx, GY+GGAP*2+GH,  gcx, GY+GGAP*3,      "#4338ca")
mk_arrow(gcx, GY+GGAP*3+GH,  gcx, GY+GGAP*4+5,    "#059669")

# Dashed "feeds into" arrows from stored indexes to hybrid engine
mk_arrow(60+106,  BY2+BH2, 80+99,   HY,        "#1e40af", dash=True)  # FAISS → Semantic
mk_arrow(320+106, BY2+BH2, 80+99,   HY+82+30,  "#065f46", dash=True)  # BM25i → BM25 Search
mk_arrow(580+106, BY2+BH2, 336+99,  HY+30+30,  "#5b21b6", dash=True)  # Meta  → RRF

# ============================================================
# ADDITIONAL FEATURES PANEL
# ============================================================
FX = 1268; FY = 460; FW = 240; FGH = 64; FGAP = 74
total_f_h = FGH * 6 + FGAP * 5 + 48
mk_bg(FX - 8, FY, FW + 16, total_f_h, "#7c3aed", "#faf5ff", sw=2)
mk_text(FX, FY + 8, FW, 20, "✨  Additional API Features", "#5b21b6", 11)

features_list = [
    ("🧩 Quiz Generator\n(/quiz)",                  "#7c3aed", "#ede9fe"),
    ("📄 Summary Builder\n(/summary)",              "#0891b2", "#e0f2fe"),
    ("🌐 Hindi Localize\n(/localize/hi)",           "#059669", "#d1fae5"),
    ("♿ Accessibility\n(Dyslexia/Beginner/Visual)","#b45309", "#fef3c7"),
    ("🔊 Piper TTS\n(Audio Output)",                "#9f1239", "#ffe4e6"),
    ("📎 User PDF Upload\n(/upload)",               "#4338ca", "#e0e7ff"),
]
for i, (label, stroke, bg) in enumerate(features_list):
    mk_rect(FX, FY + 34 + i * FGAP, FW, FGH, label, stroke, bg, fs=11)

# ============================================================
# EDGE / OFFLINE DEPLOY BANNER
# ============================================================
mk_bg(35, 1064, 1490, 74, "#475569", "#f8fafc", sw=2)
mk_text(52, 1072, 1470, 58,
        "🔌  Edge / Offline Deploy — Jetson Nano / Edge AI\n"
        "Ships with pre-built FAISS+BM25 indexes  •  No PDFs required at runtime  •  Fully offline  •  No HuggingFace network calls",
        "#1e293b", 12)

# ============================================================
# WRITE OUTPUT FILE
# ============================================================
out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saksham_ai_architecture.excalidraw")

doc = {
    "type": "excalidraw",
    "version": 2,
    "source": "https://excalidraw.com",
    "elements": elements,
    "appState": {
        "gridSize": None,
        "viewBackgroundColor": "#ffffff"
    },
    "files": {}
}

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=2, ensure_ascii=False)

print(f"✅  Generated {len(elements)} elements → {out_path}")
