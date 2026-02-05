import os
import base64
import logging
from openai import OpenAI, OpenAIError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("engine")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not found in environment variables")

client = OpenAI(api_key=OPENAI_API_KEY)


def analyze_leg_image(image_path: str) -> dict:
    try:
        if not os.path.exists(image_path):
            return {"error": "Uploaded image not found"}

        # Convert image → base64 (REQUIRED on Render)
        with open(image_path, "rb") as img:
            encoded_image = base64.b64encode(img.read()).decode("utf-8")

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Analyze this leg image and describe visible swelling, discoloration, "
                                "or abnormalities. Respond clearly and safely."
                            )
                        },
                        {
                            "type": "input_image",
                            "image_base64": encoded_image
                        }
                    ]
                }
            ],
        )

        output_text = response.output_text

        return {
            "observations": [output_text],
            "general_info": "This is an AI-generated visual observation.",
            "risk_level": "unclear",
            "visual_markers": []
        }

    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return {"error": "AI service error. Please try again later."}

    except Exception as e:
        logger.exception("Unexpected engine error")
        return {"error": "Internal server error during image analysis"}
