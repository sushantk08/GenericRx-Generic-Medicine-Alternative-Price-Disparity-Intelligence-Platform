from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.schemas import AutocompleteItem

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

    # SQL query combining prefix matching with trigram similarity for typo tolerance
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