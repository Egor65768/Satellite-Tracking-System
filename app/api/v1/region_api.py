from fastapi import APIRouter, Path, Depends, status, Query
from typing import Annotated, List
from app.api.v1.helpers import raise_if_object_none, get_region_service
from app.api.v1.auth import get_current_user
from app.schemas import (
    RegionInDB,
    SubregionInDB,
    PaginationBase,
    RegionCreate,
    SubregionCreate,
    RegionUpdate,
    SubregionUpdate,
)
from app.service import RegionService

router = APIRouter()

RegionID = Annotated[
    int,
    Path(
        title="The ID of the region",
        ge=0,
        le=10000,
    ),
]
SubregionID = Annotated[int, Path(title="The ID of the subregion", ge=0, le=100000)]
RegionName = Annotated[
    str,
    Path(
        title="Region or subregion name",
        min_length=1,
        max_length=60,
        json_schema_extra={"examples": ["Asia", "Moscow region"]},
    ),
]


@router.get(
    "/{region_id}",
    response_model=RegionInDB,
    summary="Get region by ID",
    description="Retrieves a region information by its ID",
    responses={
        404: {"description": "Region not found"},
        200: {"description": "Region found", "model": RegionInDB},
    },
)
async def get_region_by_id(
    region_id: RegionID,
    region_service: RegionService = Depends(get_region_service),
) -> RegionInDB:
    region = await region_service.get_region_by_id(region_id)
    await raise_if_object_none(region, status.HTTP_404_NOT_FOUND, "Region not found")
    return region


@router.get(
    "/subregion/{subregion_id}",
    response_model=SubregionInDB,
    summary="Get subregion by ID",
    description="Retrieves a subregion information by its ID",
    responses={
        404: {"description": "Subregion not found"},
        200: {"description": "Subregion found", "model": SubregionInDB},
    },
)
async def get_subregion_by_id(
    subregion_id: SubregionID,
    region_service: RegionService = Depends(get_region_service),
) -> SubregionInDB:
    subregion = await region_service.get_subregion_by_id(subregion_id)
    await raise_if_object_none(
        subregion, status.HTTP_404_NOT_FOUND, "Subregion not found"
    )
    return subregion


@router.get(
    "/name/{region_name}",
    response_model=RegionInDB,
    summary="Get region by region name",
    description="Retrieves a region information by its name",
    responses={
        404: {"description": "Region not found"},
        200: {"description": "Region found", "model": RegionInDB},
    },
)
async def get_region_by_region_name(
    region_name: RegionName,
    region_service: RegionService = Depends(get_region_service),
) -> RegionInDB:
    region = await region_service.get_region_by_name(region_name)
    await raise_if_object_none(region, status.HTTP_404_NOT_FOUND, "Region not found")
    return region


@router.get(
    "/subregion/name/{subregion_name}",
    response_model=SubregionInDB,
    summary="Get subregion by subregion name",
    description="Retrieves a subregion information by its name",
    responses={
        404: {"description": "Subregion not found"},
        200: {"description": "Subregion found", "model": SubregionInDB},
    },
)
async def get_subregion_by_subregion_name(
    subregion_name: RegionName,
    region_service: RegionService = Depends(get_region_service),
) -> SubregionInDB:
    subregion = await region_service.get_subregion_by_name(subregion_name)
    await raise_if_object_none(
        subregion, status.HTTP_404_NOT_FOUND, "Subregion not found"
    )
    return subregion


@router.get(
    "/regions/",
    response_model=List[RegionInDB],
    summary="Get a list of regions",
    responses={
        200: {"description": "Regions list", "model": List[RegionInDB]},
    },
)
async def get_regions(
    region_service: RegionService = Depends(get_region_service),
    limit: Annotated[int, Query(ge=1)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> List[RegionInDB]:
    return await region_service.get_regions(PaginationBase(limit=limit, offset=offset))


@router.get(
    "/subregions/",
    response_model=List[SubregionInDB],
    summary="Get a list of subregions",
    responses={
        200: {"description": "Subregions list", "model": List[SubregionInDB]},
    },
)
async def get_subregions(
    region_service: RegionService = Depends(get_region_service),
    limit: Annotated[int, Query(ge=1)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> List[SubregionInDB]:
    return await region_service.get_subregions(
        PaginationBase(limit=limit, offset=offset)
    )


@router.post(
    path="/",
    response_model=RegionInDB,
    summary="Create region",
    description="Returns the region if created successfully",
    responses={
        409: {"description": "Region has not been created"},
        200: {"description": "Region create", "model": RegionInDB},
    },
)
async def create_region(
    region_create: RegionCreate,
    region_service: RegionService = Depends(get_region_service),
    _auth=Depends(get_current_user),
) -> RegionInDB:
    region = await region_service.create_region(region_create)
    await raise_if_object_none(
        region, status.HTTP_409_CONFLICT, "A region with such data cannot be created"
    )
    return region


@router.post(
    path="/subregion",
    response_model=SubregionInDB,
    summary="Create subregion",
    description="Returns the subregion if created successfully",
    responses={
        409: {"description": "Subregion has not been created"},
        200: {"description": "Subregion create", "model": SubregionInDB},
    },
)
async def create_subregion(
    subregion_create: SubregionCreate,
    region_service: RegionService = Depends(get_region_service),
    _auth=Depends(get_current_user),
) -> SubregionInDB:
    subregion = await region_service.create_subregion(subregion_create)
    await raise_if_object_none(
        subregion,
        status.HTTP_409_CONFLICT,
        "A subregion with such data cannot be created",
    )
    return subregion


@router.delete(
    "/{region_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete region by ID",
    description="Returns nothing",
    responses={
        404: {"description": "Region not found"},
        204: {"description": "Region was successfully deleted, no content returned"},
        409: {"description": "Conflict - Region could not be deleted"},
    },
)
async def region_delete_by_id(
    region_id: RegionID,
    region_service: RegionService = Depends(get_region_service),
    _auth=Depends(get_current_user),
):
    await raise_if_object_none(
        await region_service.get_region_by_id(region_id),
        status.HTTP_404_NOT_FOUND,
        "Region not found",
    )
    region = await region_service.delete_region(region_id)
    await raise_if_object_none(
        region, status.HTTP_409_CONFLICT, "Conflict - Region could not be deleted"
    )
    return None


@router.delete(
    "/subregion/{subregion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete subregion by ID",
    description="Returns nothing",
    responses={
        404: {"description": "Subregion not found"},
        204: {"description": "Subregion was successfully deleted, no content returned"},
    },
)
async def subregion_delete_by_id(
    subregion_id: SubregionID,
    region_service: RegionService = Depends(get_region_service),
    _auth=Depends(get_current_user),
):
    subregion = await region_service.delete_subregion(subregion_id)
    await raise_if_object_none(
        subregion, status.HTTP_404_NOT_FOUND, "Subregion not found"
    )
    return None


@router.put(
    "/{region_id}",
    response_model=RegionInDB,
    summary="Update region information",
    description="Updates the information of a region. "
    "Upon successful update, returns the updated region details.",
    responses={
        404: {"description": "Region not found"},
        409: {
            "description": "Conflict - Region could not be updated "
            "(e.g., invalid data or constraints violation)"
        },
        200: {"description": "Region updated", "model": RegionInDB},
    },
)
async def update_region(
    region_update: RegionUpdate,
    region_id: RegionID,
    region_service: RegionService = Depends(get_region_service),
    _auth=Depends(get_current_user),
) -> RegionInDB:
    await raise_if_object_none(
        await region_service.get_region_by_id(region_id),
        status.HTTP_404_NOT_FOUND,
        "Region not found",
    )

    region = await region_service.update_region(region_id, region_update)
    await raise_if_object_none(
        region, status.HTTP_409_CONFLICT, "A region with such data cannot be updated"
    )
    return region


@router.put(
    "/subregion/{subregion_id}",
    response_model=SubregionInDB,
    summary="Update subregion information",
    description="Updates the information of a subregion. "
    "Upon successful update, returns the updated subregion details.",
    responses={
        404: {"description": "Subregion not found"},
        409: {
            "description": "Conflict - Subregion could not be updated "
            "(e.g., invalid data or constraints violation)"
        },
        200: {"description": "Subregion updated", "model": SubregionInDB},
    },
)
async def update_subregion(
    subregion_update: SubregionUpdate,
    subregion_id: SubregionID,
    region_service: RegionService = Depends(get_region_service),
    _auth=Depends(get_current_user),
) -> SubregionInDB:
    await raise_if_object_none(
        await region_service.get_subregion_by_id(subregion_id),
        status.HTTP_404_NOT_FOUND,
        "Subregion not found",
    )

    subregion = await region_service.update_subregion(subregion_id, subregion_update)
    await raise_if_object_none(
        subregion,
        status.HTTP_409_CONFLICT,
        "A subregion with such data cannot be updated",
    )
    return subregion
