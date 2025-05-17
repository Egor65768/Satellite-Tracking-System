from fastapi import APIRouter, Path, Depends, Response, status, HTTPException, Query
from typing import Annotated, Optional
from app.core import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.service import create_country_service
from app.schemas import CountryInDB

router = APIRouter()


@router.get(
    "/{country_id}",
    response_model=Optional[CountryInDB],
    summary="Get country by ID",
    description="Retrieves a country by its unique identifier",
    responses={
        404: {"description": "Country not found"},
        200: {"description": "Country found", "model": CountryInDB},
    },
)
async def get_country_by_id(
    country_id: Annotated[int, Path(title="The ID of the country")],
    db: AsyncSession = Depends(get_db),
) -> Optional[CountryInDB]:
    country_service = create_country_service(db)
    country = await country_service.get_country(country_id)
    if country is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Country not found"
        )
    return country


@router.get(
    "/",
    response_model=Optional[CountryInDB],
    summary="Get country by country abbreviation",
    description="Returns a country by its unique abbreviation",
    responses={
        404: {"description": "Country not found"},
        200: {"description": "Country found", "model": CountryInDB},
    },
)
async def get_country_by_abbreviation(
    abbreviation: Annotated[
        str,
        Query(
            min_length=1,
            max_length=10,
            example="CA",
            description="Filter by country abbreviation",
        ),
    ],
    db: AsyncSession = Depends(get_db),
) -> Optional[CountryInDB]:
    country_service = create_country_service(db)
    country = await country_service.get_by_abbreviation(abbreviation)
    if country is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Country not found"
        )
    return country
