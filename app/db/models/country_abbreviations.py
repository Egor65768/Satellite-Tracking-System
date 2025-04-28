from .base import Base
from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import String, Integer
from typing import List
from .satellite import Satellite


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    abbreviation: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    satellites: Mapped[List["Satellite"]] = relationship("Satellite", back_populates="country")
