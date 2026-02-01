from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid
import shutil
import logging

from engine import analyze_leg_image

# -------------------------
# Logging
# -------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# -------------------------
# FastAPI app
# -------------------------
app = FastAPI(
    title="LimbScan AI",
    description="AI-assisted visual health awareness tool",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Root route
@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    index_file = BASE_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return index_file.read_text(encoding="utf-8")

# Image analysis
@app.post("/api/analyze-leg")
async def analyze_leg(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format. Use JPEG, PNG, or WEBP."
        )

    image_id = f"{uuid.uuid4()}.png"
    temp_path = BASE_DIR / image_id

    try:
        # Save temporarily
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Saved uploaded image as {image_id}")

        # Run AI analysis
        ai_result = analyze_leg_image(temp_path)

        if "error" in ai_result:
            logger.error(f"AI analysis error: {ai_result['error']}")
            raise HTTPException(status_code=500, detail=ai_result["error"])

        return JSONResponse(
            content={
                "status": "success",
                "data": {
                    "image_id": image_id,
                    "analysis": ai_result,
                    "disclaimer": (
                        "This tool provides general visual observations only "
                        "and does not offer medical diagnosis."
                    )
                }
            }
        )

    except Exception as e:
        logger.exception("Failed to analyze image")
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")

    finally:
        if temp_path.exists():
            temp_path.unlink()
            logger.info(f"Deleted temporary image {image_id}")

# Health check
@app.get("/health")
def health_check():
    return {"status": "ok"}
