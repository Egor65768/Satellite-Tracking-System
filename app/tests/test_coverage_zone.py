import pytest
import aiofiles
from typing import Optional
from app.db import CoverageZoneRepository
from app.schemas import (
    CoverageZoneCreate,
    CoverageZoneInDB,
    PaginationBase,
    Object_str_ID,
)

test_create_data = [
    {
        "id": "2021-12bd-23730",
        "transmitter_type": "Ku-Band",
        "image": "app/tests/test/test1.jpg",
    },
    {
        "id": "2001-1234-24670",
        "transmitter_type": "Ku-Band",
        "image": "app/tests/test/test2.jpg",
    },
]


async def get_data_image(path_img: str) -> Optional[bytes]:
    try:
        async with aiofiles.open(path_img, "rb") as f:
            image_date = await f.read()
        return image_date
    except FileNotFoundError:
        return None
    except PermissionError:
        return None


class TestCreate:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("zone_data", test_create_data)
    async def test_create_1(self, db_session, zone_data):
        local_data = await get_data_image(zone_data["image"])
        coverage_zone = CoverageZoneCreate(
            id=zone_data["id"],
            transmitter_type=zone_data["transmitter_type"],
            image_data=local_data,
        )
        repo = CoverageZoneRepository(db_session)
        async with db_session.begin():
            zone: CoverageZoneInDB = await repo.create_entity(coverage_zone)
            assert zone is not None
            assert zone.id == zone_data["id"]
            assert zone.transmitter_type == zone_data["transmitter_type"]
            async with await repo.s3._get_client() as client:
                response = await client.get_object(
                    Bucket=repo.s3.bucket_name, Key=f"zone/{zone.id}.jpg"
                )
                s3_image_data = await response["Body"].read()
                assert local_data == s3_image_data


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_1(self, db_session):
        repo = CoverageZoneRepository(db_session)
        id_list = [
            Object_str_ID(id="2021-12bd-23730"),
            Object_str_ID(id="2001-1234-24670"),
        ]
        numbers_in_db = 2
        async with db_session.begin():
            for id_obj in id_list:
                zone_list = await repo.get_models(PaginationBase())
                assert len(zone_list) == numbers_in_db
                await repo.delete_model(id_obj)
                zone_list = await repo.get_models(PaginationBase())
                numbers_in_db -= 1
                assert len(zone_list) == numbers_in_db
