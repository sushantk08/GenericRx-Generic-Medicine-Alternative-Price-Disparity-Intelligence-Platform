from pydantic import BaseModel, ConfigDict


class AutocompleteItem(BaseModel):
    id: int
    brand_name: str
    salt_name: str
    strength: str
    dosage_form: str
    manufacturer: str | None
    mrp: float
    price_per_unit: float

    model_config = ConfigDict(from_attributes=True)