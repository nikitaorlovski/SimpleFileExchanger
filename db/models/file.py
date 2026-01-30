from sqlalchemy.orm import Mapped, mapped_column
from db.db import Base
from datetime import datetime
from sqlalchemy import DateTime, func

class FileORM(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str]
    content_type: Mapped[str]
    size: Mapped[int] = mapped_column()
    path: Mapped[str] = mapped_column(unique=True, index=True)
    downloads_left: Mapped[int] = mapped_column(index=True)
    upload_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
