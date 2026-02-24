def classify_change(old: str, new: str) -> str:
    """
    Classify the type of change between two material info strings.
    Returns: "no_change", "minor", or "major"
    """
    if (old or "").strip() == (new or "").strip():
        return "no_change"

    diff = abs(len((old or "")) - len((new or "")))
    ratio = diff / max(len(old or ""), 1)

    if ratio < 0.15:
        return "minor"
    return "major"

def analyze_material_differences(old_materials: str, new_materials: str) -> dict:
    """
    Analyze differences between old and new materials.
    Returns detailed change analysis (placeholder with random data).
    """
    change_type = classify_change(old_materials, new_materials)
    
    return {
        "change_type": change_type,
        "impact_level": "low" if change_type == "no_change" else "high" if change_type == "major" else "medium",
        "requires_lab_test": change_type == "major",
        "description": f"Material composition {change_type}."
    }
