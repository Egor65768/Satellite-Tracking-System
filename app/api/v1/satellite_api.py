from fastapi import APIRouter, Path, Depends, status, HTTPException, Query
from typing import Annotated
from app.core import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.service import create_satellite_service
from app.schemas import SatelliteInDB, SatelliteCharacteristicInDB
from pydantic import Field

router = APIRouter()

InternationalCode = Annotated[
    str,
    Path(
        title="The international code of the satellite",
        description="Unique international designator (e.g. '1999-025A')",
        examples=["1999-025A", "2023-123B"],
    ),
    Field(max_length=20),  # Максимальная длина 20 символов
]


@router.get(
    "/international_code/{international_code}",
    response_model=SatelliteInDB,
    summary="Get satellite by international code",
    description="Retrieves a satellite information by its unique international code",
    responses={
        404: {"description": "Satellite not found"},
        200: {"description": "Satellite found", "model": SatelliteInDB},
    },
)
async def get_satellite_by_international_code(
    international_code: InternationalCode,
    db: AsyncSession = Depends(get_db),
) -> SatelliteInDB:
    satellite_service = create_satellite_service(db)
    satellite = await satellite_service.get_satellite_by_id(international_code)
    if satellite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Satellite not found"
        )
    return satellite


@router.get(
    "/characteristic/{international_code}",
    response_model=SatelliteCharacteristicInDB,
    summary="Get satellite characteristic by international code",
    description="Retrieves a satellite characteristic by its unique international code",
    responses={
        404: {"description": "Satellite characteristic not found"},
        200: {
            "description": "Satellite characteristic found",
            "model": SatelliteCharacteristicInDB,
        },
    },
)
async def get_satellite_characteristic_by_international_code(
    international_code: InternationalCode,
    db: AsyncSession = Depends(get_db),
) -> SatelliteCharacteristicInDB:
    satellite_service = create_satellite_service(db)
    satellite_characteristic = await satellite_service.get_satellite_characteristics(
        international_code
    )
    if satellite_characteristic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Satellite characteristic not found",
        )
    return satellite_characteristic
