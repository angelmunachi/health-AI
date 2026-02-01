import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# Load environment variables from .env
load_dotenv()

# Fetch OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise OpenAIError(
        "OpenAI API key is missing. Please set it in your .env file as OPENAI_API_KEY."
    )

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def analyze_leg_image(image_path: str) -> dict:
    """
    Example function: sends image to OpenAI Vision API and returns analysis.
    Adjust model & parameters as needed.
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()

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

    # Simplified response parsing (adjust based on your AI model output)
    result = {
        "analysis": response.output_text if hasattr(response, "output_text") else str(response)
    }
    return result
