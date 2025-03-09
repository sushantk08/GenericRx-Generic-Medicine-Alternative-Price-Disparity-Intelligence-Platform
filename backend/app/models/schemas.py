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


class GenericAlternativeItem(BaseModel):
    id: int
    generic_name: str
    source: str
    pack_size: int
    mrp: float
    price_per_unit: float
    price_diff_per_unit: float
    percentage_savings: float

    model_config = ConfigDict(from_attributes=True)


class AlternativesResponse(BaseModel):
    branded_medicine: MedicineDetail
    alternatives: list[GenericAlternativeItem]
    best_alternative: GenericAlternativeItem | None
    max_savings_percentage: float

    model_config = ConfigDict(from_attributes=True)