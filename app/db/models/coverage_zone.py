from sqlalchemy import String, ForeignKey, Integer, LargeBinary, Table, Column
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .satellite import Satellite
    from .region import Region, Subregion


coverage_zone_association = Table(
    "coverage_zone_association",
    Base.metadata,
    Column("coverage_zone_id", String(60), ForeignKey("coverage_zones.id")),
    Column("region_id", Integer, ForeignKey("regions.id")),
)

coverage_zone_association_subregion = Table(
    "coverage_zone_association_subregion",
    Base.metadata,
    Column("coverage_zone_id", String(60), ForeignKey("coverage_zones.id")),
    Column("subregion_id", Integer, ForeignKey("subregions.id")),
)


class CoverageZone(Base):
    __tablename__ = "coverage_zones"
    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    satellite_code: Mapped[str] = mapped_column(
        String(50), ForeignKey("satellites.international_code"), nullable=False
    )
    transmitter_type: Mapped[str] = mapped_column(String(50), nullable=False)
    image_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    satellite: Mapped["Satellite"] = relationship(
        "Satellite", lazy="joined", back_populates="coverage_zones"
    )
    regions: Mapped[List["Region"]] = relationship(
        "Region",
        secondary=coverage_zone_association,
        lazy="selectin",
        back_populates="coverage_zone",
    )
    subregions: Mapped[List["Subregion"]] = relationship(
        "Subregion",
        secondary=coverage_zone_association_subregion,
        lazy="selectin",
        back_populates="coverage_zone",
    )

    def __repr__(self):
        return (
            f"<CoverageZone(id='{self.id}', satellite_code='{self.satellite_code}', "
            f"transmitter_type='{self.transmitter_type}')>"
        )
