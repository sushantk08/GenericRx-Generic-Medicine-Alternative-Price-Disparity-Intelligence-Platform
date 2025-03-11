from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check():
    """Verify service health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "GenericRx" in data["service"]


def test_autocomplete_endpoint():
    """Verify sub-second autocomplete returns matching branded medicines."""
    response = client.get("/api/v1/medicines/autocomplete?q=tel")
    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0
    # First match should be Telma
    assert "Telma" in items[0]["brand_name"]
    assert items[0]["salt_name"] == "Telmisartan"
    assert items[0]["price_per_unit"] > 0


def test_medicine_detail_found():
    """Verify medicine details endpoint for a valid ID."""
    response = client.get("/api/v1/medicines/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "Telma" in data["brand_name"]
    assert data["salt_name"] == "Telmisartan"
    assert data["pack_size"] > 0


def test_medicine_detail_not_found():
    """Verify 404 response for non-existent medicine ID."""
    response = client.get("/api/v1/medicines/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Medicine not found"


def test_generic_alternatives_endpoint():
    """Verify generic alternatives mapping and savings calculations."""
    response = client.get("/api/v1/medicines/1/alternatives")
    assert response.status_code == 200
    data = response.json()

    assert "branded_medicine" in data
    assert len(data["alternatives"]) > 0
    best = data["best_alternative"]
    assert best is not None
    assert best["price_per_unit"] < data["branded_medicine"]["price_per_unit"]
    assert data["max_savings_percentage"] > 50.0  # PMBJP generics save 60-85%+


def test_prescription_savings_calculator():
    """Verify monthly and annual savings calculation for a prescription basket."""
    payload = {
        "items": [
            {
                "branded_medicine_id": 1,
                "tablets_per_day": 1.0,
                "days_per_month": 30,
            },
            {
                "branded_medicine_id": 2,
                "tablets_per_day": 2.0,
                "days_per_month": 30,
            },
        ]
    }
    response = client.post("/api/v1/calculator/savings", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert len(data["items"]) == 2
    assert (
        data["total_branded_monthly_spend"] > data["total_generic_monthly_spend"]
    )
    assert data["total_monthly_savings"] > 0
    # Annual savings must equal monthly * 12
    assert data["total_annual_savings"] == round(
        data["total_monthly_savings"] * 12, 2
    )
    assert data["overall_savings_percentage"] > 0