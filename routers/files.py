from fastapi import APIRouter, UploadFile, Depends, HTTPException, BackgroundTasks, Query

from fastapi.responses import StreamingResponse

from services.file_service import FileService, get_file_service, FileNotFound, FileExpire
from datetime import datetime, timezone, timedelta
router = APIRouter(prefix="/api/files", tags=["Files"])

@router.post("/")
async def upload_file(file: UploadFile, expire_days: int = Query(7, ge=1), downloads_left: int = Query(1, ge=1), file_service: FileService = Depends(get_file_service)):
    expires_at = datetime.now(timezone.utc) + timedelta(days=expire_days)
    filename = file.filename
    size = file.size
    if size >= 524288000:
        raise HTTPException(status_code=400, detail="File size is  bigger than 500MB")
    content_type = file.content_type
    created_file = await file_service.upload_file(filename=filename, file=file.file, content_type=content_type, size=size, downloads_left=downloads_left,expires_at=expires_at)
    return {"key": created_file.path}

@router.get("/download/{key}")
async def download_file(
    key: str,
    file_service: FileService = Depends(get_file_service),
):
    try:
        file, stream = await file_service.stream_file(key)
    except FileNotFound:
        raise HTTPException(status_code=404, detail="File not found")
    except FileExpire:
        raise HTTPException(status_code=410, detail="File expired")

    return StreamingResponse(
        stream,
        media_type=file.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{file.filename}"',
            "Content-Length": str(file.size),
        }
    )


