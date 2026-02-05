# main.py
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from engine import analyze_leg_image

import logging

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple health check
@app.get("/")
async def root():
    return {"message": "LimbScan AI is live!"}

# Endpoint to analyze leg images
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
