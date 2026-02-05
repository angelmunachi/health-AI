import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in environment variables")

client = OpenAI(api_key=OPENAI_API_KEY)


def analyze_leg_image(image_path: str) -> dict:
    """
    Sends an image to OpenAI Vision and returns structured observations
    """

    # Read and encode image
    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Analyze this leg image for visible swelling, skin changes, "
                                "or abnormalities. Respond strictly in JSON with:\n"
                                "{ observations: [], general_info: string, risk_level: "
                                "'low' | 'medium' | 'unclear', visual_markers: "
                                "[{label, x, y}] }"
                            )
                        },
                        {
                            "type": "input_image",
                            "image_base64": image_base64
                        }
                    ]
                }
            ],
            max_output_tokens=500
        )

        # Extract text safely
        output_text = response.output_text

        # If model fails to return JSON, fail gracefully
        if not output_text:
            raise RuntimeError("Empty response from OpenAI")

        return eval(output_text) if output_text.strip().startswith("{") else {
            "observations": [output_text],
            "general_info": "AI returned unstructured output.",
            "risk_level": "unclear",
            "visual_markers": []
        }

    except Exception as e:
        # This is what triggers your 500
        raise RuntimeError(f"OpenAI analysis failed: {str(e)}")
