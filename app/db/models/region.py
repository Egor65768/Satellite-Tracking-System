from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Integer
from typing import List


class Region(Base):
    __tablename__ = "regions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_region: Mapped[str] = mapped_column(String(60), nullable=False)
    subregions: Mapped[List["Subregion"]] = relationship("Subregion", back_populates="region")
    coverage_zone: Mapped[List["CoverageZone"]] = relationship(
        "CoverageZone",
        secondary="coverage_zone_association",
        back_populates="regions"
    )


class Subregion(Base):
    __tablename__ = "subregions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_subregion: Mapped[str] = mapped_column(String(60), nullable=False)
    id_region: Mapped[int] = mapped_column(ForeignKey("regions.id"), nullable=False)
    region: Mapped["Region"] = relationship("Region",back_populates="subregions")
    coverage_zone: Mapped[List["CoverageZone"]] = relationship(
        "CoverageZone",
        secondary="coverage_zone_association_subregion",
        back_populates="subregions"
    )
