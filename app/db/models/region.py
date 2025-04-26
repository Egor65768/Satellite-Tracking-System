from .base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey


class Region(Base):
    __tablename__ = "regions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name_region: Mapped[str] = mapped_column(String(60), nullable=False)


class Subregion(Base):
    __tablename__ = "subregions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name_subregion: Mapped[str] = mapped_column(String(60), nullable=False)
    id_region: Mapped[int] = mapped_column(ForeignKey("Region.id"), nullable=False)
