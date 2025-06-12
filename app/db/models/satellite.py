from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Date, ForeignKey
from datetime import date
from typing import List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .country_abbreviations import Country
    from .satellite_characteristic import SatelliteCharacteristic
    from .coverage_zone import CoverageZone


class Satellite(Base):
    __tablename__ = "satellites"
    international_code: Mapped[str] = mapped_column(String(50), primary_key=True)
    name_satellite: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )
    norad_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    launch_date: Mapped[date] = mapped_column(Date, nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"), nullable=False)
    country: Mapped["Country"] = relationship(
        "Country", lazy="joined", back_populates="satellites"
    )
    characteristics: Mapped["SatelliteCharacteristic"] = relationship(
        "SatelliteCharacteristic",
        lazy="joined",
        back_populates="satellite",
        cascade="all, delete-orphan",
        uselist=False,
    )
    coverage_zones: Mapped[List["CoverageZone"]] = relationship(
        "CoverageZone", lazy="selectin", back_populates="satellite"
    )

    def __repr__(self):
        return (
            f"<Satellite(international_code='{self.international_code}', "
            f"name='{self.name_satellite}', norad_id={self.norad_id}, "
            f"country_id={self.country_id})>"
        )
