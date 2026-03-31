import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# setam baza de test INAINTE sa importam app/database/models
temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
TEST_DATABASE_URL = f"sqlite:///{temp_db.name}"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from database import Base, get_db
from main import app
from models import (
    Identifier,
    Country,
    Relationship,
    Characteristic,
    IdentifierCharacteristic,
    Measurement
)

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def seed_test_data():
    db = TestingSessionLocal()
    try:
        # curata tot
        db.query(Measurement).delete()
        db.query(IdentifierCharacteristic).delete()
        db.query(Relationship).delete()
        db.query(Characteristic).delete()
        db.query(Country).delete()
        db.query(Identifier).delete()
        db.commit()

        db.add(Identifier(
            identifier_name="88823141",
            description="Shampoo Product",
            identifier_type="Finished Product Part"
        ))

        db.add(Country(
            name="France",
            iso_code="FR",
            short_code="250"
        ))

        db.add(Characteristic(
            master_name="CM-10001",
            name="Volume",
            specifics="Shampoo Bottle Volume",
            action_required="CONTROL",
            report_type="VARIABLE",
            data_type="Decimal",
            lower_routine_release_limit=490.0,
            lower_limit=490.0,
            lower_target=500.0,
            target=505.0,
            upper_target=510.0,
            upper_limit=520.0,
            upper_routine_release_limit=520.0,
            test_frequency=1,
            precision=2,
            engineering_unit="ml"
        ))

        db.add(IdentifierCharacteristic(
            identifier_name="88823141",
            master_name="CM-10001",
            characteristic_name="Volume"
        ))

        db.commit()
    finally:
        db.close()


def setup_function():
    seed_test_data()


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Factory API is running"}


def test_get_identifiers():
    response = client.get("/identifiers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_identifier():
    payload = {
        "identifier_name": "77777777",
        "description": "Pytest Product",
        "identifier_type": "Test Type"
    }

    response = client.post("/identifiers", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Identifier created successfully"
    assert data["data"]["identifier_name"] == "77777777"


def test_delete_identifier():
    # il cream mai intai
    client.post("/identifiers", json={
        "identifier_name": "77777777",
        "description": "Pytest Product",
        "identifier_type": "Test Type"
    })

    response = client.delete("/identifiers/77777777")
    assert response.status_code == 200
    assert response.json()["message"] == "Identifier 77777777 deleted successfully"


def test_quality_check_within_limits():
    payload = {
        "identifier_name": "88823141",
        "master_name": "CM-10001",
        "characteristic_name": "Volume",
        "measured_value": 505
    }

    response = client.post("/quality-check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Within limits"


def test_create_measurement():
    payload = {
        "identifier_name": "88823141",
        "master_name": "CM-10001",
        "characteristic_name": "Volume",
        "measured_value": 530
    }

    response = client.post("/measurements", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Measurement saved successfully"
    assert data["data"]["status"] == "Above upper limit"


def test_get_measurements():
    client.post("/measurements", json={
        "identifier_name": "88823141",
        "master_name": "CM-10001",
        "characteristic_name": "Volume",
        "measured_value": 505
    })

    response = client.get("/measurements")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1