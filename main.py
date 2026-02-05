from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid
import shutil
import logging

from engine import analyze_leg_image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI(
    title="LimbScan AI",
    description="AI-assisted visual health awareness tool",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return (BASE_DIR / "index.html").read_text(encoding="utf-8")


@app.post("/api/analyze-leg")
async def analyze_leg(file: UploadFile = File(...)):

    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid image format")

    image_id = f"{uuid.uuid4()}.png"
    image_path = UPLOAD_DIR / image_id

    try:
        with image_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ai_result = analyze_leg_image(str(image_path))

        if "error" in ai_result:
            raise HTTPException(status_code=500, detail=ai_result["error"])

        return JSONResponse(
            content={
                "status": "success",
                "data": {
                    "image_id": image_id,
                    "analysis": ai_result,
                    "disclaimer": (
                        "This tool provides general visual observations only "
                        "and does not provide medical diagnosis."
                    )
                }
            }
        )

    finally:
        if image_path.exists():
            image_path.unlink()


@app.get("/health")
def health():
    return {"status": "ok"}















