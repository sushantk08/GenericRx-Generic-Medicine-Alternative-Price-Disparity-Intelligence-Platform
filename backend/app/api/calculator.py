from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.schemas import (
    PrescriptionItemSavings,
    PrescriptionSavingsRequest,
    PrescriptionSavingsResponse,
)

router = APIRouter(prefix="/calculator", tags=["Calculator"])


@router.post("/savings", response_model=PrescriptionSavingsResponse)
def calculate_prescription_savings(
    request: PrescriptionSavingsRequest, db: Session = Depends(get_db)
):
    """Calculate monthly and annual savings by substituting prescribed branded

    medicines with lowest-cost generic alternatives.
    """
    item_savings_list: list[PrescriptionItemSavings] = []
    total_branded_spend = 0.0
    total_generic_spend = 0.0

    for item in request.items:
        monthly_tablets = round(item.tablets_per_day * item.days_per_month, 2)

        # 1. Fetch branded medicine & its salt
        sql_branded = text(
            """
            SELECT 
                b.id,
                b.brand_name,
                b.price_per_unit,
                b.salt_id,
                s.salt_name
            FROM branded_medicines b
            JOIN salts s ON b.salt_id = s.id
            WHERE b.id = :id;
            """
        )
        branded_row = (
            db.execute(sql_branded, {"id": item.branded_medicine_id})
            .mappings()
            .first()
        )

        if not branded_row:
            continue

        b_price_per_unit = float(branded_row["price_per_unit"])
        b_monthly_cost = round(b_price_per_unit * monthly_tablets, 2)

        # 2. Fetch the lowest-priced generic alternative for this salt
        sql_generic = text(
            """
            SELECT 
                g.id,
                g.generic_name,
                g.price_per_unit
            FROM generic_medicines g
            WHERE g.salt_id = :salt_id
            ORDER BY g.price_per_unit ASC
            LIMIT 1;
            """
        )
        generic_row = (
            db.execute(sql_generic, {"salt_id": branded_row["salt_id"]})
            .mappings()
            .first()
        )

        if generic_row:
            g_id = generic_row["id"]
            g_name = generic_row["generic_name"]
            g_price_per_unit = float(generic_row["price_per_unit"])
            g_monthly_cost = round(g_price_per_unit * monthly_tablets, 2)
        else:
            g_id = None
            g_name = None
            g_price_per_unit = None
            g_monthly_cost = b_monthly_cost

        savings = round(b_monthly_cost - g_monthly_cost, 2)
        savings_pct = (
            round((savings / b_monthly_cost) * 100, 2)
            if b_monthly_cost > 0
            else 0.0
        )

        total_branded_spend += b_monthly_cost
        total_generic_spend += g_monthly_cost

        item_savings_list.append(
            PrescriptionItemSavings(
                branded_medicine_id=branded_row["id"],
                brand_name=branded_row["brand_name"],
                salt_name=branded_row["salt_name"],
                tablets_per_month=monthly_tablets,
                branded_unit_price=b_price_per_unit,
                branded_monthly_cost=b_monthly_cost,
                generic_medicine_id=g_id,
                generic_name=g_name,
                generic_unit_price=g_price_per_unit,
                generic_monthly_cost=g_monthly_cost,
                monthly_savings=max(savings, 0.0),
                savings_percentage=max(savings_pct, 0.0),
            )
        )

    total_monthly_savings = round(
        total_branded_spend - total_generic_spend, 2
    )
    total_annual_savings = round(total_monthly_savings * 12, 2)
    overall_pct = (
        round((total_monthly_savings / total_branded_spend) * 100, 2)
        if total_branded_spend > 0
        else 0.0
    )

    return PrescriptionSavingsResponse(
        items=item_savings_list,
        total_branded_monthly_spend=round(total_branded_spend, 2),
        total_generic_monthly_spend=round(total_generic_spend, 2),
        total_monthly_savings=max(total_monthly_savings, 0.0),
        total_annual_savings=max(total_annual_savings, 0.0),
        overall_savings_percentage=max(overall_pct, 0.0),
    )