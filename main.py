from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uuid
import shutil
import os

from engine import analyze_leg_image

app = FastAPI(title="LimbScan AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
def serve_ui():
    index = BASE_DIR / "index.html"
    if not index.exists():
        return "<h2>Frontend not found</h2>"
    return index.read_text(encoding="utf-8")


@app.post("/api/analyze-leg")
async def analyze_leg(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Unsupported image format")

    temp_file = BASE_DIR / f"{uuid.uuid4()}.png"

    try:
        with temp_file.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        analysis = analyze_leg_image(str(temp_file))

        return JSONResponse({
            "status": "success",
            "data": analysis,
            "disclaimer": (
                "This tool provides visual observations only "
                "and is not a medical diagnosis."
            )
        })

    except Exception as e:
        # This is what your frontend is seeing
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if temp_file.exists():
            temp_file.unlink()


@app.get("/health")
def health():
    return {"status": "ok"}
