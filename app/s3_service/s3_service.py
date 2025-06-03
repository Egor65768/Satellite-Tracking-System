from app.core import settings
from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from typing import Optional


class S3Service:
    def __init__(self):
        self.session = get_session()
        self.bucket_name = settings.BUCKET_NAME
        self.endpoint_url = settings.ENDPOINT_URL
        self.aws_access_key_id = settings.ACCESS_KEY
        self.aws_secret_access_key = settings.SECRET_KEY

    async def _get_client(self):
        return self.session.create_client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            verify=False,
        )

    async def upload_file(self, file_data: bytes, file_key: str) -> bool:
        async with await self._get_client() as client:
            try:
                response = await client.put_object(
                    Bucket=self.bucket_name,
                    Key=file_key,
                    Body=file_data,
                    ACL="public-read",  # или другой ACL, если нужно
                )
                return response["ResponseMetadata"]["HTTPStatusCode"] == 200
            except ClientError:
                return False

    async def delete_file(self, file_key: str) -> bool:
        async with await self._get_client() as client:
            try:
                response = await client.delete_object(
                    Bucket=self.bucket_name,
                    Key=file_key,
                )
                return response["ResponseMetadata"]["HTTPStatusCode"] in (200, 204)
            except ClientError:
                return False

    async def get_file(self, zone_id: str) -> Optional[bytes]:
        try:
            async with await self._get_client() as client:
                response = await client.get_object(
                    Bucket=self.bucket_name, Key=f"zone/{zone_id}.jpg"
                )
                s3_image_data = await response["Body"].read()
                return s3_image_data
        except ClientError:
            return None
