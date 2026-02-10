# ---------- PATH FIX (MUST BE FIRST) ----------
import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# ---------- STANDARD IMPORTS ----------
from fastapi import FastAPI, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import joblib
import json
import numpy as np
import subprocess
import shutil

# ---------- AGENTS ----------
from agents.chat_spec_agent.chat_spec_agent import ChatSpecAgent

# ---------- APP ----------
app = FastAPI(title="AutoDev Backend")

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- PATHS ----------
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
PREPROCESSOR_PATH = os.path.join(BASE_DIR, "preprocessor.pkl")
METADATA_PATH = os.path.join(BASE_DIR, "model_metadata.json")
STRATEGY_PATH = os.path.join(BASE_DIR, "training_strategy_v1.json")
DRAFT_SPEC = os.path.join(BASE_DIR, "application_spec_draft.json")
FINAL_SPEC = os.path.join(BASE_DIR, "application_spec_v1.json")

# ---------- GLOBAL STATE ----------
model = None
scaler = None
metadata = None
strategy = None
chat_agent = None

# ============================================================
# ROUTE MANIFEST (SOURCE OF TRUTH)
# ============================================================
@app.get("/routes")
def route_manifest():
    return {
        "pages": [
            {"path": "/", "file": "index.html"},
            {"path": "/about", "file": "about.html"},
            {"path": "/portfolio", "file": "portfolio.html"},
            {"path": "/blog", "file": "blog.html"},
            {"path": "/contact", "file": "contact.html"},
            {"path": "/admin/login", "file": "admin/login.html"},
        ]
    }

# ============================================================
# WEBSITE PAGE SERVING
# ============================================================
def serve_html(file_path: str):
    full_path = os.path.join(FRONTEND_DIR, file_path)
    if not os.path.exists(full_path):
        return HTMLResponse(
            f"<h1>404</h1><p>{file_path} not built yet.</p>",
            status_code=404
        )
    with open(full_path) as f:
        return HTMLResponse(f.read())

@app.get("/", response_class=HTMLResponse)
def home():
    return serve_html("index.html")

@app.get("/about", response_class=HTMLResponse)
def about():
    return serve_html("about.html")

@app.get("/portfolio", response_class=HTMLResponse)
def portfolio():
    return serve_html("portfolio.html")

@app.get("/blog", response_class=HTMLResponse)
def blog():
    return serve_html("blog.html")

@app.get("/contact", response_class=HTMLResponse)
def contact():
    return serve_html("contact.html")

@app.get("/admin/login", response_class=HTMLResponse)
def admin_login():
    return serve_html("admin/login.html")

# ============================================================
# CHAT (CONVERSATION PHASE)
# ============================================================
@app.on_event("startup")
def init_chat_agent():
    global chat_agent
    try:
        chat_agent = ChatSpecAgent()
        print("✅ ChatSpecAgent ready")
    except Exception as e:
        chat_agent = None
        print("⚠️ ChatSpecAgent disabled:", e)

@app.post("/chat")
def chat(data: dict = Body(default={})):
    if not chat_agent:
        return {"error": "Chat agent unavailable"}
    return chat_agent.run(data.get("message", ""))

# ============================================================
# BUILD CONTROL (LOCK + ORCHESTRATE)
# ============================================================
@app.post("/go")
def go(_: dict = Body(default={})):
    if not os.path.exists(DRAFT_SPEC):
        return {"error": "No draft spec to build"}

    shutil.copy(DRAFT_SPEC, FINAL_SPEC)

    subprocess.Popen(
        ["python", os.path.join(BASE_DIR, "orchestrator.py")],
        cwd=BASE_DIR
    )

    return {
        "status": "BUILD_STARTED",
        "preview_url": "http://127.0.0.1:8000/"
    }

# ============================================================
# ML CONTEXT
# ============================================================
@app.on_event("startup")
def load_artifacts():
    global model, scaler, metadata, strategy

    if os.path.exists(STRATEGY_PATH):
        with open(STRATEGY_PATH) as f:
            strategy = json.load(f)

    if not os.path.exists(MODEL_PATH):
        return

    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(PREPROCESSOR_PATH)

    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH) as f:
            metadata = json.load(f)

@app.get("/context")
def context():
    return {"strategy": strategy, "metadata": metadata}

@app.post("/predict")
def predict(data: dict):
    if not model or not metadata:
        return {"error": "Model not ready"}

    features = data.get("features", [])
    if len(features) != metadata["feature_count"]:
        return {
            "error": "Invalid feature length",
            "expected": metadata["feature_count"],
            "received": len(features)
        }

    X = np.array(features).reshape(1, -1)
    X_scaled = scaler.transform(X)
    distances, indices = model.kneighbors(X_scaled)

    return {"neighbors": indices.tolist(), "distances": distances.tolist()}
