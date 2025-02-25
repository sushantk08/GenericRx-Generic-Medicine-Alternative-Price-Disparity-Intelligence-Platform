from datetime import datetime, timezone
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from backend.app.db.session import Base


class Salt(Base):
    __tablename__ = "salts"

    id = Column(Integer, primary_key=True, index=True)
    salt_name = Column(String(255), nullable=False, index=True)
    strength_value = Column(Numeric(10, 2), nullable=False)
    strength_unit = Column(String(20), nullable=False)  # 'mg', 'ml', 'mcg', 'gm'
    dosage_form = Column(
        String(50), nullable=False
    )  # 'Tablet', 'Capsule', 'Syrup', etc.
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    branded_medicines = relationship(
        "BrandedMedicine", back_populates="salt", cascade="all, delete-orphan"
    )
    generic_medicines = relationship(
        "GenericMedicine", back_populates="salt", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "salt_name",
            "strength_value",
            "strength_unit",
            "dosage_form",
            name="uq_salt_strength_form",
        ),
    )


class BrandedMedicine(Base):
    __tablename__ = "branded_medicines"

    id = Column(Integer, primary_key=True, index=True)
    brand_name = Column(String(255), nullable=False, index=True)
    salt_id = Column(
        Integer, ForeignKey("salts.id", ondelete="RESTRICT"), nullable=False
    )
    manufacturer = Column(String(255), nullable=True)
    pack_size = Column(Integer, nullable=False)
    mrp = Column(Numeric(10, 2), nullable=False)
    price_per_unit = Column(Numeric(10, 4), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    salt = relationship("Salt", back_populates="branded_medicines")

    __table_args__ = (
        CheckConstraint("pack_size > 0", name="chk_branded_pack_size_positive"),
        CheckConstraint("mrp >= 0", name="chk_branded_mrp_non_negative"),
        CheckConstraint(
            "price_per_unit >= 0", name="chk_branded_unit_price_non_negative"
        ),
    )


class GenericMedicine(Base):
    __tablename__ = "generic_medicines"

    id = Column(Integer, primary_key=True, index=True)
    generic_name = Column(String(255), nullable=False, index=True)
    salt_id = Column(
        Integer, ForeignKey("salts.id", ondelete="RESTRICT"), nullable=False
    )
    source = Column(String(100), default="Jan Aushadhi (PMBJP)", nullable=False)
    pack_size = Column(Integer, nullable=False)
    mrp = Column(Numeric(10, 2), nullable=False)
    price_per_unit = Column(Numeric(10, 4), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    salt = relationship("Salt", back_populates="generic_medicines")

    __table_args__ = (
        CheckConstraint("pack_size > 0", name="chk_generic_pack_size_positive"),
        CheckConstraint("mrp >= 0", name="chk_generic_mrp_non_negative"),
        CheckConstraint(
            "price_per_unit >= 0", name="chk_generic_unit_price_non_negative"
        ),
    )