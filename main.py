from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid
import shutil
import os
import base64
import tempfile

from engine import analyze_leg_image  # AI logic lives here

# -------------------------
# App Configuration
# -------------------------
app = FastAPI(
    title="LimbScan AI",
    description="AI-assisted visual health awareness tool",
    version="1.0.0"
)

# -------------------------
# CORS (for frontend + three.js)
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Static Files (PWA, icons, three.js assets)
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = STATIC_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# -------------------------
# Root Route (serves UI)
# -------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    index_file = BASE_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return index_file.read_text(encoding="utf-8")

# -------------------------
# Image Upload + AI Analysis
# -------------------------
@app.post("/api/analyze-leg")
async def analyze_leg(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format. Use JPEG, PNG, or WEBP."
        )

    image_id = f"{uuid.uuid4()}.png"
    temp_path = UPLOADS_DIR / image_id

    try:
        # Save uploaded image
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Close the UploadFile to avoid locked files
        await file.close()

        # ---- AI Analysis ----
        ai_result = analyze_leg_image(temp_path)

        # Convert image to base64 for immediate frontend display
        with temp_path.open("rb") as f:
            image_bytes = f.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        return JSONResponse(
            content={
                "status": "success",
                "data": {
                    "image_id": image_id,
                    "image_base64": f"data:{file.content_type};base64,{image_b64}",
                    "analysis": ai_result,
                    "disclaimer": (
                        "This tool provides general visual observations only "
                        "and does not offer medical diagnosis. "
                        "Consult a qualified healthcare professional for concerns."
                    )
                }
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# -------------------------
# Health Check
# -------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}
