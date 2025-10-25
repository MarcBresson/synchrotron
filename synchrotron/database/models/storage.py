from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from .base import PersistentBase


class Storage(PersistentBase):
    __tablename__ = "storage"

    id: Mapped[int] = mapped_column(nullable=False, primary_key=True)
    type: Mapped[str]
    base_path: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
