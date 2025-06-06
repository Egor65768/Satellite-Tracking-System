from fastapi import HTTPException, Path, status, Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import get_db
from app.service import create_coverage_zone_service, CoverageZoneService

CoverageZoneId = Annotated[
    str,
    Path(
        title="The identifier of the coverage zone",
        examples=["2012-07B4-1", "2012-07B4-2"],
        min_length=5,
        max_length=60,
    ),
]


async def get_coverage_zone_service(db: AsyncSession = Depends(get_db)):
    return create_coverage_zone_service(db)


async def valid_coverage_zone(
    coverage_zone_id: CoverageZoneId,
    coverage_zone_service: CoverageZoneService = Depends(get_coverage_zone_service),
):
    coverage_zone = await coverage_zone_service.get_by_id(coverage_zone_id)
    if coverage_zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Coverage zone not found"
        )
    return None
