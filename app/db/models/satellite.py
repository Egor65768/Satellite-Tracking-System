from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Date, ForeignKey
from datetime import date
from typing import List
from .country_abbreviations import Country
from .satellite_characteristic import SatelliteCharacteristic
from .coverage_zone import CoverageZone


class Satellite(Base):
    __tablename__ = "satellites"
    international_code: Mapped[str] = mapped_column(String(50), primary_key=True)
    name_satellite: Mapped[str] = mapped_column(String(100), nullable=False)
    norad_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    launch_date: Mapped[date] = mapped_column(Date)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"), nullable=False)
    country: Mapped["Country"] = relationship("Country", back_populates="satellites",cascade="all, delete-orphan")
    characteristics: Mapped["SatelliteCharacteristic"] = relationship(
        "SatelliteCharacteristic", back_populates="satellite", cascade="all, delete-orphan"
    )
    coverage_zones: Mapped[List["CoverageZone"]] = relationship("CoverageZone", back_populates="satellite")
