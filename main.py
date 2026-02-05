from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from engine import analyze_leg_image
import os

app = FastAPI()

# CORS (allow all origins for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from root
app.mount("/static", StaticFiles(directory=os.path.dirname(os.path.abspath(__file__))), name="static")

# Root endpoint serves your index.html
@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# API endpoint
@app.post("/api/analyze-leg")
async def analyze_leg(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        result = analyze_leg_image(file_bytes)

        if "error" in result:
            return JSONResponse(status_code=500, content={"error": result["error"]})

        return JSONResponse(content=result)

    except Exception as e:
        logging.exception("Failed to analyze leg image")
        return JSONResponse(status_code=500, content={"error": str(e)})
