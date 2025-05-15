from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, ForeignKey, Text
from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .satellite import Satellite


class SatelliteCharacteristic(Base):
    __tablename__ = "satellite_characteristic"
    international_code: Mapped[str] = mapped_column(
        String(50), ForeignKey("satellites.international_code"), primary_key=True
    )
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    period: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    launch_site: Mapped[str] = mapped_column(String(100), nullable=False)
    rocket: Mapped[str] = mapped_column(String(50), nullable=False)
    launch_mass: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    manufacturer: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    expected_lifetime: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_lifetime: Mapped[int] = mapped_column(Integer, nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    satellite: Mapped["Satellite"] = relationship(
        "Satellite",
        lazy="joined",
        back_populates="characteristics",
        uselist=False,
    )

    def __repr__(self):
        return (
            f"<SatelliteCharacteristic(international_code='{self.international_code}', "
            f"longitude={self.longitude}, launch_site='{self.launch_site}', "
            f"rocket='{self.rocket}')>"
        )
