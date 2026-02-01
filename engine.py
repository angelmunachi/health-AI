import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# Load local .env if present (Render uses Environment Variables directly)
load_dotenv()

# Fetch OpenAI API key from env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise OpenAIError(
        "OpenAI API key is missing. Set OPENAI_API_KEY in your environment variables."
    )

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def analyze_leg_image(image_path: str) -> dict:
    """
    Sends an image to OpenAI Vision API and returns a structured analysis.
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
                        {"type": "input_text", "text": "Analyze this leg image for swelling or abnormalities."},
                        {"type": "input_image", "image_bytes": image_bytes}
                    ]
                }
            ]
        )

        # Safely parse output
        output_text = getattr(response, "output_text", None)
        if not output_text:
            output_text = str(response)

        # Return structured result
        return {
            "observations": [output_text],
            "general_info": "This analysis is AI-generated and should not replace medical advice.",
            "risk_level": "unclear",
            "visual_markers": []
        }

    except OpenAIError as e:
        return {"error": f"OpenAI API Error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected Error: {str(e)}"}
