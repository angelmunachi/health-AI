import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# Load environment variables from .env
load_dotenv()

# Fetch OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OpenAI API key is missing. Please set it in your .env file as OPENAI_API_KEY."
    )

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def analyze_leg_image(image_path: str) -> dict:
    """
    Sends an image to OpenAI Vision API and returns structured analysis.
    Returns a dict with observations, risk_level, and visual_markers.
    """
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Analyze this leg image for swelling, bruising, redness, or other abnormalities. "
                                    "Return a JSON object with keys: observations (list of strings), "
                                    "risk_level ('low', 'medium', 'high', 'unclear'), and visual_markers "
                                    "(list of objects with 'label', 'x', 'y' normalized between 0-1)."
                        },
                        {"type": "input_image", "image_bytes": image_bytes}
                    ]
                }
            ]
        )

        # Parse response
        output_text = ""
        if hasattr(response, "output") and response.output:
            # Concatenate all text segments
            for item in response.output:
                if item.type == "message" and hasattr(item, "content"):
                    for c in item.content:
                        if c.type == "output_text":
                            output_text += c.text + "\n"

        # Try to convert to dict safely
        import json
        try:
            result = json.loads(output_text)
        except Exception:
            # fallback if AI returns free text
            result = {"observations": [output_text.strip()], "risk_level": "unclear", "visual_markers": []}

        return result

    except OpenAIError as e:
        return {"observations": [], "risk_level": "unclear", "visual_markers": [], "error": str(e)}
    except Exception as e:
        return {"observations": [], "risk_level": "unclear", "visual_markers": [], "error": str(e)}
