import os
import json
import google.generativeai as genai
import random

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_ai_rating(product, batch, materials):
    """
    Generate sustainability rating using Gemini
    based on product details + batch + materials.
    """

    payload_data = {
        "product": product,
        "batch": {
            "batch_code": getattr(batch, "batch_code", None),
            "created_at": batch.created_at.isoformat() if getattr(batch, "created_at", None) else None
        },
        "materials": materials
    }

    prompt = f"""
        You are a sustainability expert.

        Evaluate the environmental sustainability of the given product or batch.

        Consider factors such as:
        - material sustainability (renewable, recycled, or harmful materials)
        - energy and water usage in production
        - carbon footprint and emissions
        - lifecycle impact (durability, reuse, disposal)
        - recyclability or biodegradability
        - environmental and ecological impact (including pollution, waste, microplastics if applicable)

        If the provided data is incomplete or insufficient, use general knowledge of similar products and industry standards to make a reasonable assessment. Clearly base your reasoning on typical characteristics when doing so.

        Give a sustainability rating out of 100, where:
        - 0 = extremely harmful to environment
        - 100 = highly sustainable and eco-friendly

        Input data:
        {json.dumps(payload_data, indent=2)}

        Return STRICT JSON ONLY in this format:

        {{
        "rating": number (0-100),
        "reasoning": "short clear explanation"
        }}
        """
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "response_mime_type": "application/json"
            }
        )

        text = response.text.strip()

        # Remove markdown code blocks if Gemini adds them
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        data = json.loads(text)

        print(data.get("rating"), data.get("reasoning"))

        return {
            "rating": float(data.get("rating")),
            "reasoning": data.get("reasoning", "")
        }

    except json.JSONDecodeError:
        return {
            "rating": None,
            "reasoning": "Failed to parse AI response"
        }

    except Exception as e:
        return {
            "rating": None,
            "reasoning": f"AI analysis failed: {str(e)}"
        }


def analyze_batch_materials(material_info: str):
    """
    Analyze batch materials and return AI insights (placeholder).
    Will be replaced with actual AI implementation later.
    """
    return {
        "material_complexity": random.choice(["low", "medium", "high"]),
        "sustainability_rating": round(random.uniform(40, 95), 2),
        "recommendations": [
            "Consider sustainable sourcing",
            "Optimize material usage",
            "Explore eco-friendly alternatives"
        ]
    }