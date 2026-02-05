import os
import base64
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_leg_image(image_path: str) -> dict:
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
                                "Respond clearly in bullet points."
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

        # ✅ SAFE PARSING (THIS FIXES THE 500)
        text_output = ""

        if response.output and len(response.output) > 0:
            for item in response.output:
                if "content" in item:
                    for block in item["content"]:
                        if block["type"] == "output_text":
                            text_output += block["text"] + "\n"

        if not text_output.strip():
            text_output = "No clear visual abnormalities detected."

        return {
            "observations": text_output.strip(),
            "risk_level": "unclear",
            "visual_markers": []
        }

    except Exception as e:
        # This will show exact OpenAI error in Render logs
        raise RuntimeError(f"OpenAI request failed: {str(e)}")
