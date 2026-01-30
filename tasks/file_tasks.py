from db.db import new_session
from repositories.file_repository import FileRepository
from repositories.s3_repository import S3Repository
from services.file_service import FileService


async def delete_expired_files():
    async with new_session() as session:
        file_service = FileService(
            repo=FileRepository(session=session), repos3=S3Repository()
        )
        expired_files = await file_service.get_expired_files()
        for file in expired_files:
            await file_service.delete_file(file.path)
