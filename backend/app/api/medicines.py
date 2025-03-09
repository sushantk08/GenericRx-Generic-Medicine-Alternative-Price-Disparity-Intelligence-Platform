from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.schemas import (
    AlternativesResponse,
    AutocompleteItem,
    GenericAlternativeItem,
    MedicineDetail,
)

router = APIRouter(prefix="/medicines", tags=["Medicines"])


@router.get("/autocomplete", response_model=list[AutocompleteItem])
def autocomplete_medicines(
    q: str = Query(
        ..., min_length=1, description="Medicine brand name search prefix"
    ),
    limit: int = Query(
        10, ge=1, le=50, description="Maximum suggestions to return"
    ),
    db: Session = Depends(get_db),
):
    """Sub-second autocomplete search utilizing PostgreSQL trigram and prefix matching."""
    clean_query = q.strip()
    prefix_pattern = f"{clean_query}%"

    sql = text(
        """
        SELECT 
            b.id,
            b.brand_name,
            s.salt_name,
            CONCAT(s.strength_value, ' ', s.strength_unit) AS strength,
            s.dosage_form,
            b.manufacturer,
            CAST(b.mrp AS FLOAT) AS mrp,
            CAST(b.price_per_unit AS FLOAT) AS price_per_unit,
            similarity(b.brand_name, :clean_query) AS sml
        FROM branded_medicines b
        JOIN salts s ON b.salt_id = s.id
        WHERE b.brand_name ILIKE :prefix_pattern OR b.brand_name % :clean_query
        ORDER BY 
            CASE WHEN b.brand_name ILIKE :prefix_pattern THEN 1 ELSE 2 END,
            sml DESC,
            b.brand_name ASC
        LIMIT :limit;
        """
    )

    result = db.execute(
        sql,
        {
            "clean_query": clean_query,
            "prefix_pattern": prefix_pattern,
            "limit": limit,
        },
    ).mappings()

    items = []
    for row in result:
        items.append(
            AutocompleteItem(
                id=row["id"],
                brand_name=row["brand_name"],
                salt_name=row["salt_name"],
                strength=row["strength"],
                dosage_form=row["dosage_form"],
                manufacturer=row["manufacturer"],
                mrp=row["mrp"],
                price_per_unit=row["price_per_unit"],
            )
        )
    return items


@router.get("/{id}", response_model=MedicineDetail)
def get_medicine_detail(id: int, db: Session = Depends(get_db)):
    """Retrieve detailed specifications of a branded medicine by ID."""
    sql = text(
        """
        SELECT 
            b.id,
            b.brand_name,
            b.manufacturer,
            b.pack_size,
            CAST(b.mrp AS FLOAT) AS mrp,
            CAST(b.price_per_unit AS FLOAT) AS price_per_unit,
            b.created_at,
            s.id AS salt_id,
            s.salt_name,
            CAST(s.strength_value AS FLOAT) AS strength_value,
            s.strength_unit,
            s.dosage_form
        FROM branded_medicines b
        JOIN salts s ON b.salt_id = s.id
        WHERE b.id = :id;
        """
    )

    row = db.execute(sql, {"id": id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Medicine not found")

    return MedicineDetail(
        id=row["id"],
        brand_name=row["brand_name"],
        manufacturer=row["manufacturer"],
        pack_size=row["pack_size"],
        mrp=row["mrp"],
        price_per_unit=row["price_per_unit"],
        created_at=row["created_at"],
        salt_id=row["salt_id"],
        salt_name=row["salt_name"],
        strength_value=row["strength_value"],
        strength_unit=row["strength_unit"],
        dosage_form=row["dosage_form"],
    )


@router.get("/{id}/alternatives", response_model=AlternativesResponse)
def get_generic_alternatives(id: int, db: Session = Depends(get_db)):
    """Find all generic substitutes sharing the exact active salt composition,

    and compute price disparities and percentage savings.
    """
    branded = get_medicine_detail(id=id, db=db)

    # Fetch all generic substitutes for this salt_id
    sql = text(
        """
        SELECT 
            g.id,
            g.generic_name,
            g.source,
            g.pack_size,
            CAST(g.mrp AS FLOAT) AS mrp,
            CAST(g.price_per_unit AS FLOAT) AS price_per_unit
        FROM generic_medicines g
        WHERE g.salt_id = :salt_id
        ORDER BY g.price_per_unit ASC;
        """
    )

    rows = db.execute(sql, {"salt_id": branded.salt_id}).mappings().fetchall()

    alternatives = []
    best_alt = None
    max_savings = 0.0

    for r in rows:
        gen_price = r["price_per_unit"]
        diff = round(branded.price_per_unit - gen_price, 4)

        if branded.price_per_unit > 0:
            savings_pct = round((diff / branded.price_per_unit) * 100, 2)
        else:
            savings_pct = 0.0

        alt_item = GenericAlternativeItem(
            id=r["id"],
            generic_name=r["generic_name"],
            source=r["source"],
            pack_size=r["pack_size"],
            mrp=r["mrp"],
            price_per_unit=gen_price,
            price_diff_per_unit=diff,
            percentage_savings=max(savings_pct, 0.0),
        )
        alternatives.append(alt_item)

        if alt_item.percentage_savings > max_savings:
            max_savings = alt_item.percentage_savings
            best_alt = alt_item

    if not best_alt and alternatives:
        best_alt = alternatives[0]

    return AlternativesResponse(
        branded_medicine=branded,
        alternatives=alternatives,
        best_alternative=best_alt,
        max_savings_percentage=max_savings,
    )