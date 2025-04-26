from sqlalchemy import String, ForeignKey, Integer, LargeBinary
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column


class CoverageZone(Base):
    __tablename__ = "coverage_zones"
    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    satellite_code: Mapped[str] = mapped_column(
        String(50), ForeignKey("Satellite.international_code"), nullable=False
    )
    transmitter_type: Mapped[str] = mapped_column(String(50), nullable=False)
    region: Mapped[int] = mapped_column(Integer, ForeignKey("Region.id"), nullable=True)
    subregion: Mapped[int] = mapped_column(
        Integer, ForeignKey("Subregion.id"), nullable=True
    )
    image_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
