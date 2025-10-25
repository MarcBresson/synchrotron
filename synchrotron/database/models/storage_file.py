from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import PersistentBase


class StorageFile(PersistentBase):
    __tablename__ = "storage_file"

    id: Mapped[int] = mapped_column(nullable=False, primary_key=True)
    storage_id: Mapped[int] = mapped_column(ForeignKey("storage.id"))
    relative_path: Mapped[str] = mapped_column(index=True)

    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())

    modified_datetime: Mapped[datetime] = mapped_column(nullable=True)
    size: Mapped[datetime] = mapped_column(nullable=True)
    content_hash: Mapped[str] = mapped_column(nullable=True)
