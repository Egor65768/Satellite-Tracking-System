from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Integer
from typing import List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .coverage_zone import CoverageZone


class Region(Base):
    __tablename__ = "regions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_region: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    subregions: Mapped[List["Subregion"]] = relationship(
        "Subregion", lazy="selectin", back_populates="region"
    )
    coverage_zone: Mapped[List["CoverageZone"]] = relationship(
        "CoverageZone",
        secondary="coverage_zone_association",
        lazy="selectin",
        back_populates="regions",
    )

    def __repr__(self):
        return f"<Region(id={self.id}, name_region='{self.name_region}')>"


class Subregion(Base):
    __tablename__ = "subregions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_subregion: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    id_region: Mapped[int] = mapped_column(ForeignKey("regions.id"), nullable=False)
    region: Mapped["Region"] = relationship(
        "Region", lazy="joined", back_populates="subregions"
    )
    coverage_zone: Mapped[List["CoverageZone"]] = relationship(
        "CoverageZone",
        secondary="coverage_zone_association_subregion",
        lazy="selectin",
        back_populates="subregions",
    )

    def __repr__(self):
        return f"<Subregion(id={self.id}, name_subregion='{self.name_subregion}', id_region={self.id_region})>"
