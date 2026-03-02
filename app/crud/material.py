from sqlalchemy.orm import Session
from app.models.material import BatchMaterial, Material

def add_materials(
    db: Session,
    materials: list,   # you can type as list[BatchMaterialInput] if imported
    batch_id: int,
):
    for material_data in materials:

        material_name = material_data.name
        if not material_name:
            raise ValueError("Material name is required")

        percentage = material_data.percentage or 0
        source = material_data.source or None
        source_info_provided = bool(source)

        material = (
            db.query(Material)
            .filter(Material.name == material_name)
            .first()
        )

        if not material:
            material = Material(name=material_name)
            db.add(material)
            db.flush()  # Ensure material.id is available

        db.add(
            BatchMaterial(
                batch_id=batch_id,
                material_id=material.id,
                percentage=percentage,
                source_info_provided=source_info_provided,
                source=source,
            )
        )