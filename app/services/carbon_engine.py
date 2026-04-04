import os
import json
import google.generativeai as genai


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def calculate_transport_emission(distance: float, fuel_type: str, vehicle_type: str, notes: str | None) -> float:
    """
    Estimate transport carbon emissions using Gemini.

    Args:
        distance (float): Distance travelled in kilometers
        fuel_type (str): diesel, petrol, electric, lpg, natural_gas etc
        vehicle_type (str): car, truck, bus, bike, van etc
        notes (str | None): Additional notes for emission calculation

    Returns:
        float: Estimated CO2 emissions in kg
    """

    prompt = f"""
    You are a transportation carbon emission calculator.

    Inputs:
    - Distance: {distance} km
    - Fuel type: {fuel_type}
    - Vehicle type: {vehicle_type}
    - Notes: {notes}

    Determine a realistic CO2 emission factor (kg CO2 per km)
    based on typical global transportation data.

    Then calculate:

    carbon_emission = distance * emission_factor

    Return ONLY valid JSON:

    {{
        "emission_factor": number,
        "carbon_emission_kg": number
    }}
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        data = json.loads(text)

        return round(float(data["carbon_emission_kg"]), 2)

    except Exception:
        # fallback estimation if model response fails
        fallback_factor = 0.25
        return round(distance * fallback_factor, 2)