from fastapi import APIRouter, Path, Depends, status, Query
from typing import Annotated, List
from app.core import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.service import create_country_service, CountryService
from app.schemas import (
    CountryInDB,
    CountryCreate,
    PaginationBase,
    CountryUpdate,
    SatelliteInDB,
)
from app.api.v1.helpers import raise_if_object_none

router = APIRouter()

CountryID = Annotated[int, Path(title="The ID of the country")]
Abbreviation = Annotated[
    str,
    Query(
        min_length=1,
        max_length=10,
        examples=["CA", "RU", "US"],
        description="Filter by country abbreviation",
    ),
]


async def get_country_service(db: AsyncSession = Depends(get_db)):
    return create_country_service(db)


@router.get(
    "/id/{country_id}",
    response_model=CountryInDB,
    summary="Get country by ID",
    description="Retrieves a country by its unique identifier",
    responses={
        404: {"description": "Country not found"},
        200: {"description": "Country found", "model": CountryInDB},
    },
)
async def get_country_by_id(
    country_id: CountryID,
    country_service=Depends(get_country_service),
) -> CountryInDB:
    country = await country_service.get_country(country_id)
    await raise_if_object_none(country, status.HTTP_404_NOT_FOUND, "Country not found")
    return country


@router.get(
    "/abbreviation/",
    response_model=CountryInDB,
    summary="Get country by country abbreviation",
    description="Returns a country by its unique abbreviation",
    responses={
        404: {"description": "Country not found"},
        200: {"description": "Country found", "model": CountryInDB},
    },
)
async def get_country_by_abbreviation(
    abbreviation: Abbreviation,
    country_service=Depends(get_country_service),
) -> CountryInDB:
    country = await country_service.get_by_abbreviation(abbreviation)
    await raise_if_object_none(country, status.HTTP_404_NOT_FOUND, "Country not found")
    return country


@router.post(
    path="/",
    response_model=CountryInDB,
    summary="Create country",
    description="Returns the country if created successfully",
    responses={
        409: {"description": "Country has not been created"},
        200: {"description": "Country create", "model": CountryInDB},
    },
)
async def create_country(
    country_create: CountryCreate,
    country_service=Depends(get_country_service),
) -> CountryInDB:
    country = await country_service.create_country(country_create)
    await raise_if_object_none(
        country, status.HTTP_409_CONFLICT, "A country with such data cannot be created"
    )
    return country


@router.delete(
    "/{country_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete country by ID",
    description="Returns nothing",
    responses={
        404: {"description": "Country not found"},
        204: {"description": "Country was successfully deleted, no content returned"},
    },
)
async def delete_by_id(
    country_id: CountryID,
    country_service: CountryService = Depends(get_country_service),
):
    await raise_if_object_none(
        await country_service.get_country(country_id),
        status.HTTP_404_NOT_FOUND,
        "Country not found",
    )
    country = await country_service.delete_country(country_id)
    await raise_if_object_none(
        country, status.HTTP_409_CONFLICT, "Conflict - Country could not be deleted"
    )
    return None


@router.get(
    "/list/",
    response_model=List[CountryInDB],
    summary="Get a list of countries",
    responses={
        200: {"description": "Countries list", "model": List[CountryInDB]},
    },
)
async def get_countries(
    country_service=Depends(get_country_service),
    limit: Annotated[int, Query(ge=1)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> List[CountryInDB]:
    return await country_service.get_countries(
        PaginationBase(limit=limit, offset=offset)
    )


@router.put(
    "/{country_id}",
    response_model=CountryInDB,
    summary="Update country information",
    description="Updates the information of a country. "
    "Upon successful update, returns the updated country details.",
    responses={
        404: {"description": "Country not found"},
        409: {
            "description": "Conflict - Country could not be updated (e.g., invalid data or constraints violation)"
        },
        200: {"description": "Country updated", "model": CountryInDB},
    },
)
async def update_country(
    country_update: CountryUpdate,
    country_id: CountryID,
    country_service=Depends(get_country_service),
) -> CountryInDB:
    await raise_if_object_none(
        await country_service.get_country(country_id),
        status.HTTP_404_NOT_FOUND,
        "Country not found",
    )

    country = await country_service.update_country(country_id, country_update)
    await raise_if_object_none(
        country, status.HTTP_409_CONFLICT, "A country with such data cannot be updated"
    )
    return country


@router.get(
    "/id/{country_id}/satellite",
    response_model=List[SatelliteInDB],
    summary="Get satellites by ID country id",
    description="Returns a list of satellites that belong to a country by country ID",
    responses={
        404: {"description": "Country not found"},
        200: {"description": "Country found", "model": List[SatelliteInDB]},
    },
)
async def get_satellites_by_country_id(
    country_id: CountryID,
    country_service=Depends(get_country_service),
) -> List[SatelliteInDB]:
    satellite_list = await country_service.get_satellites_by_country_id(country_id)
    if satellite_list is None:
        await raise_if_object_none(
            satellite_list, status.HTTP_404_NOT_FOUND, "Country not found"
        )
    return satellite_list
