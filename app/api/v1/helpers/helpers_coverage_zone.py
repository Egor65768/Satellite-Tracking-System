from fastapi import HTTPException, Path, status, Depends, UploadFile
from typing import Annotated, Optional
from app.api.v1.helpers import get_coverage_zone_service
from app.service import CoverageZoneService
from app.schemas import CoverageZoneCreate, CoverageZoneUpdate
from pydantic import ValidationError

CoverageZoneId = Annotated[
    str,
    Path(
        title="The identifier of the coverage zone",
        examples=["2012-07B4-1", "2012-07B4-2"],
        min_length=5,
        max_length=60,
    ),
]

RegionName = Annotated[
    str,
    Path(
        title="The name region",
        examples=["USA", "Russia"],
        min_length=1,
        max_length=60,
    ),
]

SubregionName = Annotated[
    str,
    Path(
        title="The name subregion",
        examples=["Moscow", "New York"],
        min_length=1,
        max_length=60,
    ),
]


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


async def valid_coverage_zone_create(
    coverage_zone_id: str, transmitter_type: str, satellite_code: str, image: UploadFile
) -> CoverageZoneCreate:
    if not image.content_type.startswith("image/"):
        raise HTTPException(400, "Only image files are allowed")
    image_data = await image.read()
    try:
        coverage_zone_create = CoverageZoneCreate(
            id=coverage_zone_id,
            transmitter_type=transmitter_type,
            satellite_code=satellite_code,
            image_data=image_data,
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    return coverage_zone_create


async def valid_coverage_zone_update(
    transmitter_type: Optional[str],
    satellite_code: Optional[str],
    image: Optional[UploadFile],
) -> CoverageZoneUpdate:
    update_dict = dict()
    if image is not None:
        if not image.content_type.startswith("image/"):
            raise HTTPException(400, "Only image files are allowed")
        image_data = await image.read()
        update_dict["image_data"] = image_data
    if transmitter_type is not None:
        update_dict["transmitter_type"] = transmitter_type
    if satellite_code is not None:
        update_dict["satellite_code"] = satellite_code

    try:
        return CoverageZoneUpdate(**update_dict)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
