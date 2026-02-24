from app.services.carbon_factors import CARBON_FACTORS
import random

def calculate_base_carbon(materials: list, weight_kg: float):
    """Calculate base carbon footprint based on materials composition"""
    total = 0
    for m in materials:
        factor = CARBON_FACTORS.get(m["name"].lower(), 5)
        portion = (m["percentage"] / 100) * weight_kg
        total += portion * factor
    return round(total, 2)

def calculate_transport_emission(distance: float, fuel_type: str) -> float:
    """Calculate transport emission based on distance and fuel type"""
    # Emission factors in kg CO2 per km
    fuel_factors = {
        "diesel": 2.68,
        "petrol": 2.31,
        "electric": 0.5,
        "lpg": 1.75,
        "natural_gas": 2.15,
    }
    
    factor = fuel_factors.get(fuel_type.lower(), 2.5)
    return round(distance * factor, 2)
