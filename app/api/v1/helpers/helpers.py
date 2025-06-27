from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import get_db
from app.service import (
    create_coverage_zone_service,
    create_user_service,
    create_region_service,
    create_satellite_service,
    create_country_service,
    create_token_service,
)


async def raise_if_object_none(object_to_be_checked, status_code: int, detail: str):
    if not object_to_be_checked:
        raise HTTPException(status_code=status_code, detail=detail)


async def get_coverage_zone_service(db: AsyncSession = Depends(get_db)):
    return create_coverage_zone_service(db)


async def get_user_service(db: AsyncSession = Depends(get_db)):
    return create_user_service(db)


async def get_region_service(db: AsyncSession = Depends(get_db)):
    return create_region_service(db)


async def get_satellite_service(db: AsyncSession = Depends(get_db)):
    return create_satellite_service(db)


async def get_country_service(db: AsyncSession = Depends(get_db)):
    return create_country_service(db)


async def get_token_service(db: AsyncSession = Depends(get_db)):
    return create_token_service(db)
