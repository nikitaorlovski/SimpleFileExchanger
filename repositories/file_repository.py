from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func, or_
from db.db import get_session
from db.models.file import FileORM
from datetime import datetime


class FileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_file(
        self,
        filename: str,
        content_type: str,
        size: int,
        path: str,
        downloads_left: int,
        expires_at: datetime,
    ):
        file = FileORM(
            filename=filename,
            content_type=content_type,
            size=size,
            path=path,
            downloads_left=downloads_left,
            expires_at=expires_at,
        )
        self.session.add(file)
        await self.session.commit()
        await self.session.refresh(file)
        return file

    async def get_file_by_key(self, key: str):
        result = await self.session.execute(select(FileORM).where(FileORM.path == key))
        return result.scalars().first()

    async def delete_file(self, key: str):
        await self.session.execute(delete(FileORM).where(FileORM.path == key))
        await self.session.commit()

    async def try_decrement_downloads(self, key: str) -> bool:
        result = await self.session.execute(
            update(FileORM)
            .where(
                FileORM.path == key,
                FileORM.downloads_left > 0,
                FileORM.expires_at > func.now(),
            )
            .values(downloads_left=FileORM.downloads_left - 1)
        )
        await self.session.commit()
        return result.rowcount == 1

    async def get_expired_files(self) -> list[FileORM]:
        result = await self.session.execute(
            select(FileORM).where(
                or_(FileORM.expires_at < func.now(), FileORM.downloads_left == 0)
            )
        )
        return result.scalars().all()


def get_file_repository(session: AsyncSession = Depends(get_session)):
    return FileRepository(session=session)
