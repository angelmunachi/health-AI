import os
import base64
from openai import OpenAI

# Read API key from Render environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_leg_image(image_path: str) -> dict:
    """
    Sends an image to OpenAI Vision and returns structured observations.
    """

    # Read and encode image as base64 (REQUIRED)
    with open(image_path, "rb") as img:
        image_base64 = base64.b64encode(img.read()).decode("utf-8")

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
                                "Analyze this leg image for visible swelling, "
                                "discoloration, wounds, or abnormalities. "
                                "Respond in clear bullet points."
                            )
                        },
                        {
                            "type": "input_image",
                            "image_base64": image_base64
                        }
                    ]
                }
            ],
            max_output_tokens=300
        )

        # Safely extract text
        output_text = response.output_text

        return {
            "observations": output_text,
            "risk_level": "unclear",
            "visual_markers": []
        }

    except Exception as e:
        # This will surface real OpenAI errors in Render logs
        raise RuntimeError(f"OpenAI analysis failed: {str(e)}")
