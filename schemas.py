from pydantic import BaseModel


class IdentifierCreate(BaseModel):
    identifier_name: str
    description: str
    identifier_type: str


class IdentifierResponse(BaseModel):
    identifier_name: str
    description: str
    identifier_type: str

    class Config:
        from_attributes = True


class QualityCheckRequest(BaseModel):
    identifier_name: str
    master_name: str
    characteristic_name: str
    measured_value: float


class QualityCheckResponse(BaseModel):
    identifier_name: str
    master_name: str
    characteristic_name: str
    measured_value: float
    lower_limit: float | None
    target: float | None
    upper_limit: float | None
    status: str

class MeasurementCreate(BaseModel):
    identifier_name: str
    master_name: str
    characteristic_name: str
    measured_value: float


class MeasurementResponse(BaseModel):
    measurement_id: int
    identifier_name: str
    master_name: str
    characteristic_name: str
    measured_value: float
    status: str

    class Config:
        from_attributes = True