from sqlalchemy import String, ForeignKey, Integer, LargeBinary, Table, Column
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List


coverage_zone_association = Table(
    'coverage_zone_association',
    Base.metadata,
    Column('coverage_zone_id', String(60), ForeignKey('coverage_zones.id')),
    Column('region_id', Integer, ForeignKey("regions.id"))
)

coverage_zone_association_subregion = Table(
    'coverage_zone_association_subregion',
    Base.metadata,
    Column('coverage_zone_id', String(60), ForeignKey('coverage_zones.id')),
    Column('subregion_id', Integer, ForeignKey("subregions.id"))
)

class CoverageZone(Base):
    __tablename__ = "coverage_zones"
    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    satellite_code: Mapped[str] = mapped_column(
        String(50), ForeignKey("satellites.international_code"), nullable=False
    )
    transmitter_type: Mapped[str] = mapped_column(String(50), nullable=False)
    image_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    satellite: Mapped["Satellite"] = relationship("Satellite", back_populates="coverage_zones")
    regions: Mapped[List["Region"]] = relationship(
        "Region",
        secondary=coverage_zone_association,
        back_populates="coverage_zone"
    )
    subregions: Mapped[List["Subregion"]] = relationship(
        "Subregion",
        secondary=coverage_zone_association_subregion,
        back_populates="coverage_zone"
    )