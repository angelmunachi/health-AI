from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import logging

# Initialize logger
logger = logging.getLogger("uvicorn.error")

# Initialize FastAPI app
app = FastAPI(title="Health AI", description="AI leg analysis API")

# Allow CORS (so frontend can call the API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Health AI API is running!"}

# Image analysis endpoint
@app.post("/api/analyze-leg")
async def analyze_leg(file: UploadFile = File(...)):
    try:
        # Ensure the uploaded file is an image
        if not file.content_type.startswith("image/"):
            return JSONResponse(status_code=400, content={"error": "Invalid file type. Please upload an image."})

        # Open the image safely
        image = Image.open(file.file)
        # Optionally convert to RGB
        image = image.convert("RGB")

        # ----------------------------
        # TODO: Replace this with your AI model prediction
        # For now, we return a dummy prediction
        result = {"prediction": "healthy", "confidence": 0.95}
        # ----------------------------

        return JSONResponse(status_code=200, content=result)

    except Exception as e:
        # Log the full error in Render logs
        logger.exception("Error analyzing image:")
        return JSONResponse(status_code=500, content={"error": "Server error: 500"})


# Optional: Example endpoint to test file uploads without AI
@app.post("/api/test-upload")
async def test_upload(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        size = len(contents)
        return {"filename": file.filename, "size_bytes": size}
    except Exception as e:
        logger.exception("Error in test upload:")
        return JSONResponse(status_code=500, content={"error": "Server error: 500"})
