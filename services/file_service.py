from typing import BinaryIO

from fastapi import Depends
from datetime import datetime

from db.models.file import FileORM
from repositories.s3_repository import S3Repository, get_s3_repo
from utils import gen_unique_filename
from repositories.file_repository import get_file_repository, FileRepository


class FileNotFound(Exception):
    pass

class FileExpire(Exception):
    pass

class FileService:
    def __init__(self, repo: FileRepository, repos3: S3Repository):
        self.file_repo = repo
        self.s3_repo = repos3
    async def upload_file(self, filename: str, file: BinaryIO, content_type: str, size: int, downloads_left: int ,expires_at: datetime):
        path = await gen_unique_filename()
        try:
            await self.s3_repo.upload_file(file=file, key=path)
            added_file = await self.file_repo.add_file(filename=filename, content_type=content_type,size=size, path=path,downloads_left=downloads_left ,expires_at=expires_at)

            return added_file
        except Exception:
            await self.s3_repo.delete(key=path)
            raise

    async def get_file_metadata(self, key: str) -> FileORM | None:
        return await self.file_repo.get_file_by_key(key)

    async def get_presigned_url(self, key: str, filename: str) -> str | None:
            return await self.s3_repo.get_presigned_url(key=key, filename=filename)

    async def delete_file(self, key: str):
        await self.file_repo.delete_file(key=key)
        await self.s3_repo.delete(key=key)

    async def stream_file(self, key: str):
        file = await self.file_repo.get_file_by_key(key)
        if not file:
            raise FileNotFound()

        ok = await self.file_repo.try_decrement_downloads(key)
        if not ok:
            raise FileExpire()

        return file, self.s3_repo.stream_file(key)

def get_file_service(repo: FileRepository = Depends(get_file_repository), repos3: S3Repository = Depends(get_s3_repo)):
    return FileService(repo=repo, repos3=repos3)