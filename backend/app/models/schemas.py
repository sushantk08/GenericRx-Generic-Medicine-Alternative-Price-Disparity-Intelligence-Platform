from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


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


# Calculator Schemas
class PrescriptionItemInput(BaseModel):
    branded_medicine_id: int
    tablets_per_day: float = Field(
        1.0, ge=0.25, le=20.0, description="Dosage quantity per day"
    )
    days_per_month: int = Field(30, ge=1, le=31)


class PrescriptionSavingsRequest(BaseModel):
    items: list[PrescriptionItemInput]


class PrescriptionItemSavings(BaseModel):
    branded_medicine_id: int
    brand_name: str
    salt_name: str
    tablets_per_month: float
    branded_unit_price: float
    branded_monthly_cost: float
    generic_medicine_id: int | None
    generic_name: str | None
    generic_unit_price: float | None
    generic_monthly_cost: float
    monthly_savings: float
    savings_percentage: float


class PrescriptionSavingsResponse(BaseModel):
    items: list[PrescriptionItemSavings]
    total_branded_monthly_spend: float
    total_generic_monthly_spend: float
    total_monthly_savings: float
    total_annual_savings: float
    overall_savings_percentage: float