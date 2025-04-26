from .base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Date, ForeignKey
from datetime import date


class Satellite(Base):
    __tablename__ = "satellites"
    international_code: Mapped[str] = mapped_column(String(50), primary_key=True)
    name_satellite: Mapped[str] = mapped_column(String(100), nullable=False)
    norad_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    launch_date: Mapped[date] = mapped_column(Date)
    country_id: Mapped[int] = mapped_column(ForeignKey("Country.id"), nullable=False)
