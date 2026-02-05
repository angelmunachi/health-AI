from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles   # <-- THIS IS MISSING IN YOUR CODE
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from engine import analyze_leg_image  # your function for image analysis

app = FastAPI()

# CORS (optional, for testing from any origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount root folder as /static
app.mount("/static", StaticFiles(directory=os.path.dirname(os.path.abspath(__file__))), name="static")

# Serve your index.html at /
@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# API endpoint for analyzing leg images
@app.post("/api/analyze-leg")
async def analyze_leg(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        result = analyze_leg_image(file_bytes)

        if "error" in result:
            return JSONResponse(
                status_code=500,
                content={"error": result["error"]}
            )

        return JSONResponse(content=result)

    except Exception as e:
        logging.exception("Failed to analyze leg image")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
