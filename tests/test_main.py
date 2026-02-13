from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import pytest
from datetime import date, timedelta
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app, get_session
from backend.models import HomeopathicMedicine, Transaction

# In-memory database for testing
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", 
        connect_args={"check_same_thread": False}, 
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_create_medicine(client):
    response = client.post(
        "/api/medicines",
        json={
            "medicine_name": "Arnica",
            "potency": "30C",
            "form": "Dilution",
            "bottle_size": "30ml",
            "manufacturer": "SBL",
            "batch_number": "B123",
            "expiry_date": "2030-01-01",
            "mrp": 100.0,
            "purchase_price": 50.0,
            "quantity": 10
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["medicine_name"] == "Arnica"
    assert data["id"] is not None

def test_create_duplicate_medicine(client):
    payload = {
        "medicine_name": "Arnica",
        "potency": "30C",
        "form": "Dilution",
        "bottle_size": "30ml",
        "manufacturer": "SBL",
        "batch_number": "B123",
        "expiry_date": "2030-01-01",
        "mrp": 100.0,
        "purchase_price": 50.0,
        "quantity": 10
    }
    client.post("/api/medicines", json=payload)
    response = client.post("/api/medicines", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_negative_stock_prevention(client):
    # Create medicine
    res = client.post(
        "/api/medicines",
        json={
             "medicine_name": "Nux Vomica", "potency": "200C", "form": "Dilution",
             "bottle_size": "30ml", "manufacturer": "SBL", "batch_number": "B456",
             "expiry_date": "2030-01-01", "mrp": 100, "purchase_price": 50, "quantity": 5
        }
    )
    med_id = res.json()["id"]

    # Try to sell 6 (more than stock)
    response = client.post(
        "/api/transaction",
        json={
            "medicine_id": med_id,
            "change_amount": -6,
            "action_type": "SELL"
        }
    )
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]

def test_expiry_sale_prevention(client):
    # Create expired medicine
    expired_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    res = client.post(
        "/api/medicines",
        json={
             "medicine_name": "Rhus Tox", "potency": "30C", "form": "Dilution",
             "bottle_size": "30ml", "manufacturer": "SBL", "batch_number": "B789",
             "expiry_date": expired_date, "mrp": 100, "purchase_price": 50, "quantity": 10
        }
    )
    med_id = res.json()["id"]

    # Try to sell without override
    response = client.post(
        "/api/transaction",
        json={
            "medicine_id": med_id,
            "change_amount": -1,
            "action_type": "SELL"
        }
    )
    assert response.status_code == 400
    assert "Cannot sell expired medicine" in response.json()["detail"]

    # Try to sell WITH override
    response = client.post(
        "/api/transaction",
        json={
            "medicine_id": med_id,
            "change_amount": -1,
            "action_type": "SELL",
            "note": "OVERRIDE"
        }
    )
    assert response.status_code == 200

def test_get_medicines(client):
    # Create two medicines
    client.post("/api/medicines", json={
        "medicine_name": "A", "potency": "30C", "form": "D", "bottle_size": "30ml",
        "manufacturer": "M", "batch_number": "B1", "expiry_date": "2030-01-01",
        "mrp": 10, "purchase_price": 5, "quantity": 10
    })
    client.post("/api/medicines", json={
        "medicine_name": "B", "potency": "30C", "form": "D", "bottle_size": "30ml",
        "manufacturer": "M", "batch_number": "B2", "expiry_date": "2030-01-01",
        "mrp": 10, "purchase_price": 5, "quantity": 10
    })
    
    response = client.get("/api/medicines")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

def test_transaction_history(client):
    # Create medicine and transaction
    res = client.post("/api/medicines", json={
        "medicine_name": "H", "potency": "30C", "form": "D", "bottle_size": "30ml",
        "manufacturer": "M", "batch_number": "BH", "expiry_date": "2030-01-01",
        "mrp": 10, "purchase_price": 5, "quantity": 10
    })
    med_id = res.json()["id"]

    client.post("/api/transaction", json={
        "medicine_id": med_id, "change_amount": -1, "action_type": "SELL", "note": "Test Note"
    })

    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[-1]["change"] == -1
    assert data[-1]["note"] == "Test Note"

def test_delete_medicine(client):
    res = client.post("/api/medicines", json={
        "medicine_name": "DEL", "potency": "30C", "form": "D", "bottle_size": "30ml",
        "manufacturer": "M", "batch_number": "BD", "expiry_date": "2030-01-01",
        "mrp": 10, "purchase_price": 5, "quantity": 10
    })
    med_id = res.json()["id"]

    # Delete
    response = client.delete(f"/api/medicines/{med_id}")
    assert response.status_code == 200

    # Verify gone
    response = client.get("/api/medicines")
    ids = [m["id"] for m in response.json()]
    assert med_id not in ids

def test_export_csv(client):
    response = client.get("/api/export")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "ID,Name,Potency" in response.text
