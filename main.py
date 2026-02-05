from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from loguru import logger

app = FastAPI(title="Health AI")

# Enable CORS so frontend can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to your frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Health AI API!"}

@app.post("/api/analyze-leg")
async def analyze_leg(file: UploadFile = File(...)):
    """
    Analyze an uploaded leg image and return AI prediction.
    """
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            return JSONResponse(
                status_code=400, 
                content={"error": "Invalid file type. Please upload an image."}
            )

        # Open image
        image = Image.open(file.file)
        image = image.convert("RGB")  # Ensure consistent format

        # --- Dummy AI prediction logic ---
        # Replace this with your actual AI model inference
        result = {
            "prediction": "healthy",   # Example: "healthy" or "diseased"
            "confidence": 0.95         # Confidence score between 0 and 1
        }

        # Wrap result in 'analysis' key to match frontend expectation
        return JSONResponse(status_code=200, content={"analysis": result})

    except Exception as e:
        logger.exception("Error analyzing image:")
        return JSONResponse(
            status_code=500,
            content={"error": "Server error: 500"}
        )

# Optional test upload endpoint
@app.post("/api/test-upload")
async def test_upload(file: UploadFile = File(...)):
    """
    Test endpoint to check file uploads.
    """
    try:
        filename = file.filename
        size = len(await file.read())
        return {"filename": filename, "size": size}
    except Exception as e:
        logger.exception("Error in test upload:")
        return JSONResponse(status_code=500, content={"error": "Upload failed"})
