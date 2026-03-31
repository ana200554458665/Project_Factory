from sqlalchemy import Column, String, Integer, Text, DECIMAL, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from database import Base


class Identifier(Base):
    __tablename__ = "Identifiers"

    identifier_name = Column(String(255), primary_key=True)
    description = Column(Text)
    identifier_type = Column(String(255))


class Country(Base):
    __tablename__ = "Countries"

    name = Column(String(255), primary_key=True)
    iso_code = Column(String(255))
    short_code = Column(String(255))


class ConsumerUnit(Base):
    __tablename__ = "ConsumerUnits"

    number_of_consumers = Column(Integer, primary_key=True)
    country_name = Column(String(255), ForeignKey("Countries.name"), primary_key=True)

    country = relationship("Country", backref="consumer_units")


class Ownership(Base):
    __tablename__ = "Ownership"

    identifier_name = Column(String(255), ForeignKey("Identifiers.identifier_name"), primary_key=True)
    user_id_tnumber = Column(String(255), primary_key=True)
    originator_first_name = Column(String(255))
    originator_last_name = Column(String(255))
    user_id_intranet = Column(String(255))
    email = Column(String(255))
    owner_first_name = Column(String(255))
    owner_last_name = Column(String(255))

    identifier = relationship("Identifier", backref="ownerships")


class Relationship(Base):
    __tablename__ = "Relationships"

    from_identifier_name = Column(String(255), ForeignKey("Identifiers.identifier_name"), primary_key=True)
    to_identifier_name = Column(String(255), ForeignKey("Identifiers.identifier_name"), primary_key=True)
    relationship_name = Column(String(255))

    from_identifier = relationship("Identifier", foreign_keys=[from_identifier_name])
    to_identifier = relationship("Identifier", foreign_keys=[to_identifier_name])


class Characteristic(Base):
    __tablename__ = "Characteristics"

    master_name = Column(String(255), primary_key=True)
    name = Column(String(255), primary_key=True)
    specifics = Column(String(255))
    action_required = Column(String(255))
    report_type = Column(String(255))
    data_type = Column(String(255))
    lower_routine_release_limit = Column(DECIMAL(10, 2))
    lower_limit = Column(DECIMAL(10, 2))
    lower_target = Column(DECIMAL(10, 2))
    target = Column(DECIMAL(10, 2))
    upper_target = Column(DECIMAL(10, 2))
    upper_limit = Column(DECIMAL(10, 2))
    upper_routine_release_limit = Column(DECIMAL(10, 2))
    test_frequency = Column(Integer)
    precision = Column(Integer)
    engineering_unit = Column(String(255))


class IdentifierCharacteristic(Base):
    __tablename__ = "IdentifierCharacteristics"

    identifier_name = Column(String(255), ForeignKey("Identifiers.identifier_name"), primary_key=True)
    master_name = Column(String(255), primary_key=True)
    characteristic_name = Column(String(255), primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["master_name", "characteristic_name"],
            ["Characteristics.master_name", "Characteristics.name"]
        ),
    )

    identifier = relationship("Identifier", backref="identifier_characteristics")
    characteristic = relationship("Characteristic")

from sqlalchemy import DateTime
from sqlalchemy.sql import func

class Measurement(Base):
    __tablename__ = "Measurements"

    measurement_id = Column(Integer, primary_key=True, autoincrement=True)
    identifier_name = Column(String(255), ForeignKey("Identifiers.identifier_name"), nullable=False)
    master_name = Column(String(255), nullable=False)
    characteristic_name = Column(String(255), nullable=False)
    measured_value = Column(DECIMAL(10, 2), nullable=False)
    measured_at = Column(DateTime, server_default=func.now(), nullable=False)
    status = Column(String(100), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["master_name", "characteristic_name"],
            ["Characteristics.master_name", "Characteristics.name"]
        ),
    )