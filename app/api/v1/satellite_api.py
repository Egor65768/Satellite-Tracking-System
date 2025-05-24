from fastapi import APIRouter, Path, Depends, status, HTTPException, Query
from typing import Annotated, List
from app.core import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.service import create_satellite_service
from app.schemas import (
    SatelliteInDB,
    SatelliteCharacteristicInDB,
    SatelliteCompleteInfo,
    PaginationBase,
    SatelliteCreate,
    SatelliteCharacteristicCreate,
    SatelliteUpdate,
    SatelliteCharacteristicUpdate,
)
from app.api.v1.helpers import raise_if_object_none

router = APIRouter()

InternationalCode = Annotated[
    str,
    Path(
        title="The international code of the satellite",
        description="Unique international designator (e.g. '1999-025A')",
        examples=["1999-025A", "2023-123B"],
        max_length=20,
    ),
]

detail_fail_create = (
    "A satellite with such data cannot be created."
    "Check that the foreign key for a country with such "
    "an id exists or that a satellite with such data "
    "already exists"
)


@router.get(
    "/{international_code}",
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
    "/{international_code}/characteristics",
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


@router.get(
    "/{international_code}/complete",
    response_model=SatelliteCompleteInfo,
    summary="Get satellite complete information by international code",
    description="Retrieves a satellite characteristic and "
    "information by its unique international code",
    responses={
        404: {"description": "Satellite complete information not found"},
        200: {
            "description": "Satellite complete information found",
            "model": SatelliteCompleteInfo,
        },
    },
)
async def get_satellite_complete_information_by_international_code(
    international_code: InternationalCode,
    db: AsyncSession = Depends(get_db),
) -> SatelliteCompleteInfo:
    satellite_service = create_satellite_service(db)
    satellite_complete_info = await satellite_service.get_satellite_complete_info(
        international_code
    )
    if satellite_complete_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Satellite complete information not found",
        )
    return satellite_complete_info


@router.get(
    "/list/",
    response_model=List[SatelliteInDB],
    summary="Get a list of satellites",
    responses={
        200: {"description": "Satellites list", "model": List[SatelliteInDB]},
    },
)
async def get_satellites(
    db: AsyncSession = Depends(get_db),
    limit: Annotated[int, Query(ge=1)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> List[SatelliteInDB]:
    satellite_service = create_satellite_service(db)
    return await satellite_service.get_satellites(
        PaginationBase(limit=limit, offset=offset)
    )


@router.post(
    path="/",
    response_model=SatelliteInDB,
    summary="Create satellite",
    description="Returns the satellite if created successfully",
    responses={
        409: {"description": "Satellite has not been created"},
        200: {"description": "Satellite create", "model": SatelliteInDB},
    },
)
async def create_satellite(
    satellite_create: SatelliteCreate,
    db: AsyncSession = Depends(get_db),
) -> SatelliteInDB:
    satellite_service = create_satellite_service(db)
    satellite = await satellite_service.create_satellite_base(satellite_create)
    await raise_if_object_none(satellite, status.HTTP_409_CONFLICT, detail_fail_create)
    await db.commit()
    return satellite


@router.post(
    path="/complete",
    response_model=SatelliteCompleteInfo,
    summary="Create satellite complete",
    description="Returns the satellite complete information if created successfully",
    responses={
        409: {"description": "Satellite has not been created"},
        200: {"description": "Satellite create", "model": SatelliteCompleteInfo},
    },
)
async def create_satellite_complete(
    satellite_create: SatelliteCreate,
    satellite_characteristic: SatelliteCharacteristicCreate,
    db: AsyncSession = Depends(get_db),
) -> SatelliteCompleteInfo:
    satellite_service = create_satellite_service(db)
    satellite = await satellite_service.create_full_satellite(
        satellite_create, satellite_characteristic
    )
    await raise_if_object_none(satellite, status.HTTP_409_CONFLICT, detail_fail_create)
    await db.commit()
    return satellite


@router.post(
    path="/characteristic",
    response_model=SatelliteCharacteristicInDB,
    summary="Create satellite characteristic",
    description="Returns the satellite characteristic if created successfully",
    responses={
        409: {"description": "Satellite characteristic has not been created"},
        200: {
            "description": "Satellite characteristic create",
            "model": SatelliteCharacteristicInDB,
        },
    },
)
async def create_satellite_characteristic(
    satellite_characteristic: SatelliteCharacteristicCreate,
    db: AsyncSession = Depends(get_db),
) -> SatelliteCharacteristicInDB:
    satellite_service = create_satellite_service(db)
    satellite_characteristic = await satellite_service.create_satellite_characteristic(
        satellite_characteristic
    )
    detail = "A satellite characteristics with such data cannot be created"
    await raise_if_object_none(
        satellite_characteristic, status.HTTP_409_CONFLICT, detail
    )
    await db.commit()
    return satellite_characteristic


@router.delete(
    path="/characteristic/{international_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete satellite characteristic by international code",
    responses={
        404: {"description": "Satellite characteristic not found"},
        204: {
            "description": "Satellite characteristic was successfully deleted, "
            "no content returned"
        },
    },
)
async def delete_satellite_characteristic_by_international_code(
    international_code: InternationalCode, db: AsyncSession = Depends(get_db)
):
    satellite_service = create_satellite_service(db)
    res = await satellite_service.delete_characteristic(international_code)
    detail = "Satellite characteristic not found"
    await raise_if_object_none(res, status.HTTP_404_NOT_FOUND, detail)
    await db.commit()


@router.delete(
    path="/{international_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete satellite by international code",
    responses={
        404: {"description": "Satellite not found"},
        204: {"description": "Satellite was successfully deleted, no content returned"},
    },
)
async def delete_satellite_by_international_code(
    international_code: InternationalCode, db: AsyncSession = Depends(get_db)
):
    satellite_service = create_satellite_service(db)
    res = await satellite_service.delete_satellite(international_code)
    detail = "Satellite not found"
    await raise_if_object_none(res, status.HTTP_404_NOT_FOUND, detail)
    await db.commit()


@router.put(
    path="/{international_code}",
    response_model=SatelliteInDB,
    summary="Update satellite information",
    description="Updates the information of a satellite. "
    "Upon successful update, returns the updated satellite details.",
    responses={
        404: {"description": "Satellite not found"},
        200: {"description": "Satellite update successfully", "model": SatelliteInDB},
        409: {
            "description": "Conflict - Satellite could not be updated "
            "(e.g., invalid data or constraints violation)"
        },
    },
)
async def update_satellite(
    satellite_update: SatelliteUpdate,
    international_code: InternationalCode,
    db: AsyncSession = Depends(get_db),
) -> SatelliteInDB:
    satellite_service = create_satellite_service(db)
    await raise_if_object_none(
        await satellite_service.get_satellite_by_id(international_code),
        status.HTTP_404_NOT_FOUND,
        "Satellite not found",
    )
    updated_satellite = await satellite_service.update_satellite(
        international_code, satellite_update
    )
    await raise_if_object_none(
        updated_satellite,
        status.HTTP_409_CONFLICT,
        "A satellite with such data cannot be updated",
    )
    # await db.commit()
    return updated_satellite


@router.put(
    path="/characteristic/{international_code}",
    response_model=SatelliteCharacteristicInDB,
    summary="Update satellite characteristics information",
    description="Updates the information characteristics of a satellite. "
    "Upon successful update, returns the updated satellite details.",
    responses={
        404: {"description": "Satellite characteristics not found"},
        200: {
            "description": "Satellite characteristics update successfully",
            "model": SatelliteCharacteristicInDB,
        },
        409: {
            "description": "Conflict - Satellite characteristics could not be updated "
            "(e.g., invalid data or constraints violation)"
        },
    },
)
async def update_satellite_characteristics(
    satellite_characteristics_update: SatelliteCharacteristicUpdate,
    international_code: InternationalCode,
    db: AsyncSession = Depends(get_db),
) -> SatelliteCharacteristicInDB:
    satellite_service = create_satellite_service(db)
    await raise_if_object_none(
        await satellite_service.get_satellite_characteristics(international_code),
        status.HTTP_404_NOT_FOUND,
        "Satellite characteristics not found",
    )
    updated_satellite_characteristics = (
        await satellite_service.update_satellite_characteristic(
            international_code, satellite_characteristics_update
        )
    )
    await raise_if_object_none(
        updated_satellite_characteristics,
        status.HTTP_409_CONFLICT,
        "A satellite with such data cannot be updated",
    )
    # await db.commit()
    return updated_satellite_characteristics
