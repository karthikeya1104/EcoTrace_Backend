def classify_change(old_materials, new_materials) -> str:
    """
    Compare two material lists and classify change.
    Returns: no_change | minor | major
    """

    if not old_materials:
        return "major"

    # normalize old
    old_map = {
        m.get("material_id") or m.get("name"): m["percentage"]
        for m in old_materials
    }

    # normalize new
    new_map = {
        m.get("material_id") or m.get("name"): m["percentage"]
        for m in new_materials
    }
    

    # -------- MATERIAL SET CHANGE --------
    if set(old_map.keys()) != set(new_map.keys()):
        return "major"

    # -------- PERCENTAGE CHANGE --------
    max_diff = 0

    for mat in old_map:
        diff = abs(old_map[mat] - new_map[mat])
        max_diff = max(max_diff, diff)
        

    if max_diff == 0:
        return "no_change"

    if max_diff <= 5:   # <=5% change
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
