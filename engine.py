# engine.py
import base64
from io import BytesIO
from PIL import Image
from openai import OpenAI

import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_leg_image(file_bytes):
    """
    Takes image bytes and returns AI analysis.
    """
    try:
        # Convert bytes to base64
        img_b64 = base64.b64encode(file_bytes).decode("utf-8")

        # Send request to OpenAI Responses API
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Analyze this leg image for visual health indicators and generate structured output."
                        },
                        {
                            "type": "input_image",
                            "image_data": img_b64
                        }
                    ]
                }
            ]
        )

        # Extract text content from response
        # The response content might be a list of dicts
        content = response.output[0].content[0].text if response.output else "No analysis available."

        # For demo purposes, return structured JSON
        result = {
            "data": {
                "analysis": {
                    "observations": ["Check for swelling, bruises, color changes."],
                    "general_info": "This is a general visual observation only.",
                    "risk_level": "unclear",
                    "visual_markers": [
                        {"x": 0.3, "y": 0.5, "label": "Example Marker"}
                    ],
                    "raw_text": content
                }
            }
        }

        return result

    except Exception as e:
        return {"error": str(e)}
