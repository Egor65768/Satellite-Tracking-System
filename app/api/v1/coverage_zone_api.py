from fastapi import (
    APIRouter,
    Depends,
    status,
    Query,
    Form,
    File,
    UploadFile,
    HTTPException,
)
from typing import Annotated, List, Union, Optional
from app.api.v1.helpers import raise_if_object_none
from app.schemas import (
    CoverageZoneInDB,
    ZoneRegionDetails,
    SatelliteInDB,
    PaginationBase,
    NumberOfZones,
    RegionBase,
    SubregionCreate,
    SubregionBase,
    SubregionCreateByName,
)
from app.service import CoverageZoneService
from app.api.v1.satellite_api import InternationalCode

router = APIRouter()
from app.api.v1.helpers import (
    CoverageZoneId,
    RegionName,
    SubregionName,
    get_coverage_zone_service,
    valid_coverage_zone,
    valid_coverage_zone_create,
    valid_coverage_zone_update,
)


@router.get(
    "/{coverage_zone_id}",
    response_model=CoverageZoneInDB,
    summary="Get coverage zone by ID",
    description="Retrieves a coverage zone information by its ID",
    responses={
        404: {"description": "Coverage zone not found"},
        200: {"description": "Coverage zone found", "model": CoverageZoneInDB},
    },
)
async def get_coverage_zone_by_id(
    coverage_zone_id: CoverageZoneId,
    coverage_zone_service: CoverageZoneService = Depends(get_coverage_zone_service),
) -> CoverageZoneInDB:
    coverage_zone = await coverage_zone_service.get_by_id(coverage_zone_id)
    await raise_if_object_none(
        coverage_zone, status.HTTP_404_NOT_FOUND, "Coverage zone not found"
    )
    return coverage_zone


@router.get(
    "/satellite/satellite_international_code/{satellite_international_code}",
    response_model=List[CoverageZoneInDB],
    summary="Get coverage zones by satellite international code",
    description="Returns a list of coverage zones for a given satellite by its international code",
    responses={
        404: {"description": "Satellite not found"},
        200: {"description": "Satellite found", "model": List[CoverageZoneInDB]},
    },
)
async def get_list_coverage_zone_by_satellite_international_code(
    satellite_international_code: InternationalCode,
    coverage_zone_service: CoverageZoneService = Depends(get_coverage_zone_service),
) -> List[CoverageZoneInDB]:
    coverage_zone_list = (
        await coverage_zone_service.get_coverage_zones_by_satellite_international_code(
            satellite_international_code
        )
    )
    if coverage_zone_list is None:
        await raise_if_object_none(
            coverage_zone_list, status.HTTP_404_NOT_FOUND, "Satellite not found"
        )
    return coverage_zone_list


@router.get(
    "/regions/{coverage_zone_id}",
    response_model=List[ZoneRegionDetails],
    summary="Get regions by coverage zone ID",
    description="Returns a list of regions that the given zone covers",
    responses={
        404: {"description": "Coverage zone not found"},
        200: {"description": "Coverage zone found", "model": List[ZoneRegionDetails]},
    },
)
async def get_region_list_by_coverage_zone_id(
    coverage_zone_id: CoverageZoneId,
    coverage_zone_service: CoverageZoneService = Depends(get_coverage_zone_service),
) -> List[ZoneRegionDetails]:
    regions_list = await coverage_zone_service.get_region_list_by_id(coverage_zone_id)
    if regions_list is None:
        await raise_if_object_none(
            regions_list, status.HTTP_404_NOT_FOUND, "Coverage zone not found"
        )
    return regions_list


@router.get(
    "/satellite/coverage_zone_id/{coverage_zone_id}",
    response_model=SatelliteInDB,
    summary="Get satellite by coverage zone id",
    description="Returns information about the satellite to which the given coverage zone belongs",
    responses={
        404: {"description": "Coverage zone not found"},
        200: {"description": "Coverage zone found", "model": SatelliteInDB},
    },
)
async def get_satellite_by_coverage_zone_id(
    coverage_zone_id: CoverageZoneId,
    coverage_zone_service: CoverageZoneService = Depends(get_coverage_zone_service),
) -> SatelliteInDB:
    satellite = await coverage_zone_service.get_satellite(coverage_zone_id)
    await raise_if_object_none(
        satellite, status.HTTP_404_NOT_FOUND, "Coverage zone not found"
    )
    return satellite


@router.get(
    "/coverage_zones/",
    response_model=List[CoverageZoneInDB],
    summary="Get a list coverage zone",
    responses={
        200: {"description": "Coverage zone list", "model": List[CoverageZoneInDB]},
    },
)
async def get_coverage_zones(
    limit: Annotated[int, Query(ge=1)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    coverage_zone_service: CoverageZoneService = Depends(get_coverage_zone_service),
) -> List[CoverageZoneInDB]:
    zone_list = await coverage_zone_service.get_coverage_zones(
        PaginationBase(limit=limit, offset=offset)
    )
    return zone_list


@router.get(
    "/coverage_zones/count/",
    response_model=NumberOfZones,
    summary="Returns the number of coverage zones",
    responses={
        200: {"description": "Number of coverage zones", "model": NumberOfZones},
    },
)
async def get_number_of_coverage_zones(
    coverage_zone_service: CoverageZoneService = Depends(get_coverage_zone_service),
) -> NumberOfZones:
    number_of_zones = await coverage_zone_service.get_count_coverage_zone_in_db()
    return number_of_zones


@router.post(
    path="/",
    response_model=CoverageZoneInDB,
    summary="Create coverage zone",
    description="Returns the coverage zone if created successfully",
    responses={
        409: {"description": "Coverage zone has not been created"},
        200: {"description": "Coverage zone create", "model": CoverageZoneInDB},
    },
)
async def create_coverage_zone(
    coverage_zone_id: Annotated[
        str, Form(..., min_length=5, max_length=60, examples=["2012-07B4-1"])
    ],
    transmitter_type: Annotated[
        str, Form(..., min_length=5, max_length=25, examples=["Ku-band"])
    ],
    satellite_code: Annotated[
        str, Form(..., min_length=5, max_length=50, examples=["123_A_123_A"])
    ],
    image: Annotated[
        UploadFile, File(..., description="Coverage zone image in JPEG/PNG format")
    ],
    coverage_zone_service: CoverageZoneService = Depends(get_coverage_zone_service),
) -> CoverageZoneInDB:
    coverage_zone_create = await valid_coverage_zone_create(
        coverage_zone_id, transmitter_type, satellite_code, image
    )
    coverage_zone = await coverage_zone_service.create_coverage_zone(
        coverage_zone_create
    )
    await raise_if_object_none(
        coverage_zone, status.HTTP_409_CONFLICT, "Coverage zone has not been created"
    )
    return coverage_zone


@router.post(
    path="/region/{coverage_zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Adds a region to the coverage zone",
    responses={
        409: {"description": "The region cannot be added to this coverage zone."},
        404: {"description": "Coverage zone not found"},
        204: {"description": "The region has been added to this coverage zone."},
    },
)
async def add_region_by_coverage_zone_id(
    region_data: RegionBase,
    coverage_zone_id: CoverageZoneId,
    _: None = Depends(valid_coverage_zone),
    coverage_zone_service: CoverageZoneService = Depends(get_coverage_zone_service),
):
    result = await coverage_zone_service.add_region_by_coverage_zone_id(
        coverage_zone_id, region_data
    )
    await raise_if_object_none(
        result,
        status.HTTP_409_CONFLICT,
        "The region cannot be added to this coverage area.",
    )


@router.post(
    path="/regions/{coverage_zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Adds a regions list to the coverage zone",
    responses={
        409: {"description": "The region cannot be added to this coverage zone."},
        404: {"description": "Coverage zone not found"},
        204: {"description": "The regions has been added to this coverage zone."},
    },
)
async def add_regions_by_coverage_zone_id(
    regions_data: List[RegionBase],
    coverage_zone_id: CoverageZoneId,
    _: None = Depends(valid_coverage_zone),
    coverage_zone_service: CoverageZoneService = Depends(get_coverage_zone_service),
):
    result = await coverage_zone_service.add_regions_by_coverage_zone_id(
        coverage_zone_id, regions_data
    )
    if not result or not all(result):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "The region cannot be added to this coverage area.",
                "result": result,
            },
        )


@router.delete(
    "/{coverage_zone_id}/region_name/{region_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete region coverage zone",
    description="Returns nothing",
    responses={
        409: {"description": "The region cannot be deleted to this coverage zone."},
        404: {"description": "Coverage zone not found"},
        204: {"description": "The region has been deleted to this coverage zone."},
    },
)
async def delete_region_coverage_zone(
    coverage_zone_id: CoverageZoneId,
    region_name: RegionName,
    _: None = Depends(valid_coverage_zone),
    coverage_zone_service: CoverageZoneService = Depends(get_coverage_zone_service),
):
    region_data = RegionBase(name_region=region_name)
    result = await coverage_zone_service.delete_region_by_coverage_zone(
        coverage_zone_id, region_data
    )
    await raise_if_object_none(
        result,
        status.HTTP_409_CONFLICT,
        "The region cannot be deleted to this coverage area.",
    )


@router.post(
    path="/subregion/{coverage_zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Adds a subregion to the coverage zone",
    description="If the region of this subregion "
    "does not belong to this coverage "
    "area, then adds the region as well",
    responses={
        409: {"description": "The subregion cannot be added to this coverage zone."},
        404: {"description": "Coverage zone not found"},
        204: {"description": "The subregion has been added to this coverage zone."},
    },
)
async def add_subregion_by_coverage_zone_id(
    subregion_data: Union[SubregionCreate, SubregionCreateByName],
    coverage_zone_id: CoverageZoneId,
    _: None = Depends(valid_coverage_zone),
    coverage_zone_service: CoverageZoneService = Depends(get_coverage_zone_service),
):
    if isinstance(subregion_data, SubregionCreate):
        result = await coverage_zone_service.add_subregion_by_coverage_zone_id(
            coverage_zone_id, subregion_data
        )
    else:
        result = await coverage_zone_service.add_subregion_by_region_name_and_coverage_zone_id(
            coverage_zone_id, subregion_data
        )
    await raise_if_object_none(
        result,
        status.HTTP_409_CONFLICT,
        "The subregion cannot be added to this coverage area.",
    )


@router.post(
    path="/subregions/{coverage_zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Adds a subregions list to the coverage zone",
    responses={
        409: {"description": "The subregions cannot be added to this coverage zone."},
        404: {"description": "Coverage zone not found"},
        204: {"description": "The regions has been added to this coverage zone."},
    },
)
async def add_subregions_by_coverage_zone_id(
    subregions_data: List[SubregionCreate],
    coverage_zone_id: CoverageZoneId,
    _: None = Depends(valid_coverage_zone),
    coverage_zone_service: CoverageZoneService = Depends(get_coverage_zone_service),
):
    result = await coverage_zone_service.add_subregions_by_coverage_zone_id(
        coverage_zone_id, subregions_data
    )
    if not result or not all(result):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "The subregion cannot be added to this coverage area.",
                "result": result,
            },
        )


@router.delete(
    "/{coverage_zone_id}/subregion_name/{subregion_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete subregion coverage zone",
    description="Returns nothing",
    responses={
        409: {"description": "The subregion cannot be deleted to this coverage zone."},
        404: {"description": "Coverage zone not found"},
        204: {"description": "The subregion has been deleted to this coverage zone."},
    },
)
async def delete_subregion_coverage_zone(
    subregion_name: SubregionName,
    coverage_zone_id: CoverageZoneId,
    _: None = Depends(valid_coverage_zone),
    coverage_zone_service: CoverageZoneService = Depends(get_coverage_zone_service),
):
    subregion_data = SubregionBase(name_subregion=subregion_name)
    result = await coverage_zone_service.delete_subregion_by_coverage_zone(
        coverage_zone_id, subregion_data
    )
    await raise_if_object_none(
        result,
        status.HTTP_409_CONFLICT,
        "The subregion cannot be deleted to this coverage area.",
    )


@router.delete(
    "/{coverage_zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete coverage zone",
    description="Returns nothing",
    responses={
        404: {"description": "Coverage zone not found."},
        204: {"description": "The coverage zone has been deleted."},
    },
)
async def delete_coverage_zone(
    coverage_zone_id: CoverageZoneId,
    _: None = Depends(valid_coverage_zone),
    coverage_zone_service: CoverageZoneService = Depends(get_coverage_zone_service),
):
    result = await coverage_zone_service.delete_coverage_zone(coverage_zone_id)
    await raise_if_object_none(
        result,
        status.HTTP_409_CONFLICT,
        "Coverage zone cannot be deleted",
    )


@router.put(
    "/{coverage_zone_id}",
    response_model=CoverageZoneInDB,
    summary="Update coverage zone information",
    description="Updates the information of a coverage zone. "
    "Upon successful update, returns the updated coverage zone details.",
    responses={
        404: {"description": "Coverage zone not found"},
        409: {
            "description": "Conflict - Coverage zone could not be updated (e.g., invalid data or constraints violation)"
        },
        200: {"description": "Coverage zone updated", "model": CoverageZoneInDB},
    },
)
async def update_coverage_zone(
    coverage_zone_id: CoverageZoneId,
    transmitter_type: Annotated[
        Optional[str], Form(min_length=5, max_length=25, examples=["Ku-band"])
    ] = None,
    satellite_code: Annotated[
        Optional[str], Form(min_length=5, max_length=50, examples=["123_A_123_A"])
    ] = None,
    image: Annotated[
        Optional[UploadFile], File(description="Coverage zone image in JPEG/PNG format")
    ] = None,
    coverage_zone_service: CoverageZoneService = Depends(get_coverage_zone_service),
) -> CoverageZoneInDB:
    coverage_zone_update = await valid_coverage_zone_update(
        transmitter_type, satellite_code, image
    )
    coverage_zone_updated = await coverage_zone_service.update_coverage_zone(
        coverage_zone_id, coverage_zone_update
    )
    await raise_if_object_none(
        coverage_zone_updated,
        status.HTTP_409_CONFLICT,
        "Conflict - Coverage zone could not be updated "
        "(e.g., invalid data or constraints violation)",
    )
    return coverage_zone_updated
