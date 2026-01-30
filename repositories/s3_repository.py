from typing import BinaryIO, AsyncIterator

import aioboto3
from botocore.exceptions import ClientError

from core.config import settings


class S3Repository:
    def __init__(
        self,
        endpoint_url: str = settings.s3.endpoint_url,
        access_key: str = settings.s3.access_key,
        secret_key: str = settings.s3.secret_key,
        region: str = settings.s3.region,
        bucket_name: str = settings.s3.bucket_name,
    ):
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.bucket_name = bucket_name
        self.session = aioboto3.Session()

    async def _client(self):
        return self.session.client(
            "s3",
            region_name=self.region,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )

    async def stream_file(self, key: str):
        async with await self._client() as s3:
            response = await s3.get_object(
                Bucket=self.bucket_name,
                Key=key,
            )

            async for chunk in response["Body"].iter_chunks(chunk_size=1024 * 1024):
                yield chunk

    async def upload_file(self, file: BinaryIO, key: str):
        async with await self._client() as s3:
            await s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file,
            )

    async def get_presigned_url(self, key: str, filename: str) -> str | None:
        async with await self._client() as s3:
            try:
                await s3.head_object(Bucket=self.bucket_name, Key=key)
            except ClientError:
                return None
            url = await s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": key,
                    "ResponseContentDisposition": f'attachment; filename="{filename}"',
                },
                ExpiresIn=86400,
            )
            return url

    async def delete(self, key: str) -> None:
        async with await self._client() as s3:
            await s3.delete_object(
                Bucket=self.bucket_name,
                Key=key,
            )


def get_s3_repo():
    return S3Repository()
