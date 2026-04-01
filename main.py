from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import (
    Identifier,
    Country,
    Relationship,
    Characteristic,
    IdentifierCharacteristic,
    Measurement
)
from schemas import (
    IdentifierCreate,
    QualityCheckRequest,
    MeasurementCreate
)

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Factory API is running"}


@app.get("/identifiers")
def get_identifiers(db: Session = Depends(get_db)):
    identifiers = db.query(Identifier).all()

    result = []
    for item in identifiers:
        result.append({
            "identifier_name": item.identifier_name,
            "description": item.description,
            "identifier_type": item.identifier_type
        })

    return result


@app.post("/identifiers")
def create_identifier(identifier: IdentifierCreate, db: Session = Depends(get_db)):
    existing_identifier = db.query(Identifier).filter(
        Identifier.identifier_name == identifier.identifier_name
    ).first()

    if existing_identifier:
        raise HTTPException(status_code=400, detail="Identifier already exists")

    new_identifier = Identifier(
        identifier_name=identifier.identifier_name,
        description=identifier.description,
        identifier_type=identifier.identifier_type
    )

    db.add(new_identifier)
    db.commit()
    db.refresh(new_identifier)

    return {
        "message": "Identifier created successfully",
        "data": {
            "identifier_name": new_identifier.identifier_name,
            "description": new_identifier.description,
            "identifier_type": new_identifier.identifier_type
        }
    }


@app.delete("/identifiers/{identifier_name}")
def delete_identifier(identifier_name: str, db: Session = Depends(get_db)):
    identifier = db.query(Identifier).filter(
        Identifier.identifier_name == identifier_name
    ).first()

    if not identifier:
        raise HTTPException(status_code=404, detail="Identifier not found")

    db.delete(identifier)
    db.commit()

    return {"message": f"Identifier {identifier_name} deleted successfully"}


@app.get("/countries")
def get_countries(db: Session = Depends(get_db)):
    countries = db.query(Country).all()

    result = []
    for item in countries:
        result.append({
            "name": item.name,
            "iso_code": item.iso_code,
            "short_code": item.short_code
        })

    return result


@app.get("/relationships")
def get_relationships(db: Session = Depends(get_db)):
    relationships = db.query(Relationship).all()

    result = []
    for item in relationships:
        result.append({
            "from_identifier_name": item.from_identifier_name,
            "to_identifier_name": item.to_identifier_name,
            "relationship_name": item.relationship_name
        })

    return result


@app.get("/characteristics")
def get_characteristics(db: Session = Depends(get_db)):
    characteristics = db.query(Characteristic).all()

    result = []
    for item in characteristics:
        result.append({
            "master_name": item.master_name,
            "name": item.name,
            "specifics": item.specifics,
            "action_required": item.action_required,
            "report_type": item.report_type,
            "data_type": item.data_type,
            "lower_limit": float(item.lower_limit) if item.lower_limit is not None else None,
            "target": float(item.target) if item.target is not None else None,
            "upper_limit": float(item.upper_limit) if item.upper_limit is not None else None,
            "engineering_unit": item.engineering_unit
        })

    return result


@app.get("/identifier-characteristics/{identifier_name}")
def get_identifier_characteristics(identifier_name: str, db: Session = Depends(get_db)):
    rows = db.query(IdentifierCharacteristic).filter(
        IdentifierCharacteristic.identifier_name == identifier_name
    ).all()

    result = []
    for item in rows:
        result.append({
            "identifier_name": item.identifier_name,
            "master_name": item.master_name,
            "characteristic_name": item.characteristic_name
        })

    return result


@app.post("/quality-check")
def quality_check(data: QualityCheckRequest, db: Session = Depends(get_db)):
    link = db.query(IdentifierCharacteristic).filter(
        IdentifierCharacteristic.identifier_name == data.identifier_name,
        IdentifierCharacteristic.master_name == data.master_name,
        IdentifierCharacteristic.characteristic_name == data.characteristic_name
    ).first()

    if not link:
        raise HTTPException(
            status_code=404,
            detail="This characteristic is not linked to the given identifier"
        )

    characteristic = db.query(Characteristic).filter(
        Characteristic.master_name == data.master_name,
        Characteristic.name == data.characteristic_name
    ).first()

    if not characteristic:
        raise HTTPException(
            status_code=404,
            detail="Characteristic not found"
        )

    if characteristic.lower_limit is None or characteristic.upper_limit is None:
        return {
            "identifier_name": data.identifier_name,
            "master_name": data.master_name,
            "characteristic_name": data.characteristic_name,
            "measured_value": data.measured_value,
            "lower_limit": None,
            "target": float(characteristic.target) if characteristic.target is not None else None,
            "upper_limit": None,
            "status": "No numeric limits defined"
        }

    lower_limit = float(characteristic.lower_limit)
    upper_limit = float(characteristic.upper_limit)
    target = float(characteristic.target) if characteristic.target is not None else None

    if data.measured_value < lower_limit:
        status = "Below lower limit"
    elif data.measured_value > upper_limit:
        status = "Above upper limit"
    else:
        status = "Within limits"

    return {
        "identifier_name": data.identifier_name,
        "master_name": data.master_name,
        "characteristic_name": data.characteristic_name,
        "measured_value": data.measured_value,
        "lower_limit": lower_limit,
        "target": target,
        "upper_limit": upper_limit,
        "status": status
    }


@app.post("/measurements")
def create_measurement(data: MeasurementCreate, db: Session = Depends(get_db)):
    link = db.query(IdentifierCharacteristic).filter(
        IdentifierCharacteristic.identifier_name == data.identifier_name,
        IdentifierCharacteristic.master_name == data.master_name,
        IdentifierCharacteristic.characteristic_name == data.characteristic_name
    ).first()

    if not link:
        raise HTTPException(
            status_code=404,
            detail="This characteristic is not linked to the given identifier"
        )

    characteristic = db.query(Characteristic).filter(
        Characteristic.master_name == data.master_name,
        Characteristic.name == data.characteristic_name
    ).first()

    if not characteristic:
        raise HTTPException(status_code=404, detail="Characteristic not found")

    if characteristic.lower_limit is None or characteristic.upper_limit is None:
        status = "No numeric limits defined"
    else:
        lower_limit = float(characteristic.lower_limit)
        upper_limit = float(characteristic.upper_limit)

        if data.measured_value < lower_limit:
            status = "Below lower limit"
        elif data.measured_value > upper_limit:
            status = "Above upper limit"
        else:
            status = "Within limits"

    new_measurement = Measurement(
        identifier_name=data.identifier_name,
        master_name=data.master_name,
        characteristic_name=data.characteristic_name,
        measured_value=data.measured_value,
        status=status
    )

    db.add(new_measurement)
    db.commit()
    db.refresh(new_measurement)

    return {
        "message": "Measurement saved successfully",
        "data": {
            "measurement_id": new_measurement.measurement_id,
            "identifier_name": new_measurement.identifier_name,
            "master_name": new_measurement.master_name,
            "characteristic_name": new_measurement.characteristic_name,
            "measured_value": float(new_measurement.measured_value),
            "status": new_measurement.status
        }
    }


@app.get("/measurements")
def get_measurements(db: Session = Depends(get_db)):
    measurements = db.query(Measurement).all()

    result = []
    for item in measurements:
        result.append({
            "measurement_id": item.measurement_id,
            "identifier_name": item.identifier_name,
            "master_name": item.master_name,
            "characteristic_name": item.characteristic_name,
            "measured_value": float(item.measured_value),
            "status": item.status,
            "measured_at": item.measured_at
        })

    return result


@app.get("/statistics/{identifier_name}")
def get_statistics(identifier_name: str, db: Session = Depends(get_db)):
    measurements = db.query(Measurement).filter(
        Measurement.identifier_name == identifier_name
    ).all()

    if not measurements:
        return {"message": "No data"}

    values = [float(m.measured_value) for m in measurements]

    return {
        "identifier_name": identifier_name,
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "average": sum(values) / len(values)
    }