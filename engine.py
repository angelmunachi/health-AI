import os
import logging
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# Load .env if exists
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("engine")

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise OpenAIError("OpenAI API key missing. Set OPENAI_API_KEY in env variables.")

# Initialize client
client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_leg_image(image_path: str) -> dict:
    """
    Sends image to OpenAI Vision API and returns structured analysis.
    """
    try:
        # Ensure file exists
        if not os.path.isfile(image_path):
            return {"error": f"File not found: {image_path}"}

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # API call
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Analyze this leg image for swelling or abnormalities."},
                        {"type": "input_image", "image_bytes": image_bytes}
                    ]
                }
            ]
        )

        # Extract text safely
        output_text = getattr(response, "output_text", None)
        if not output_text:
            output_text = str(response)

        # Return structured result
        return {
            "observations": [output_text],
            "general_info": "This analysis is AI-generated. Not a medical diagnosis.",
            "risk_level": "unclear",
            "visual_markers": []
        }

    except OpenAIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return {"error": "OpenAI API error. Check your API key or usage limits."}

    except Exception as e:
        logger.exception("Unexpected error in analyze_leg_image")
        return {"error": f"Unexpected server error: {str(e)}"}
