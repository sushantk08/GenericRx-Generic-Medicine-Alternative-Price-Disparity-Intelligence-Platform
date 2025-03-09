from datetime import datetime
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


class MedicineDetail(BaseModel):
    id: int
    brand_name: str
    manufacturer: str | None
    pack_size: int
    mrp: float
    price_per_unit: float
    salt_id: int
    salt_name: str
    strength_value: float
    strength_unit: str
    dosage_form: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)