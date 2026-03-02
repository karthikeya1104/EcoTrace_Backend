from sqlalchemy.orm import Session
from app.models.material import BatchMaterial, Material

def add_materials(
    db: Session,
    materials: list[dict],
    batch_id: int,
):
    for material_data in materials:

        material_name = material_data.get("name")
        if not material_name:
            raise ValueError("Material name is required")

        percentage = material_data.get("percentage", 0)
        source = material_data.get("source")
        source_info_provided = True if source else False

        material = (
            db.query(Material)
            .filter(Material.name == material_name)
            .first()
        )

        if not material:
            material = Material(name=material_name)
            db.add(material)
            db.flush()  # ensure material.id exists

        db.add(
            BatchMaterial(
                batch_id=batch_id,
                material_id=material.id,
                percentage=percentage,
                source_info_provided=source_info_provided,
                source=source,
            )
        )