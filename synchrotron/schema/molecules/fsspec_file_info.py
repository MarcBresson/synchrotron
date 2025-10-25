from datetime import datetime
from typing import Literal, Optional, TypedDict


class FileInfo(TypedDict):
    name: str
    """full path of file"""
    size: int | None
    """size in bytes"""
    type: Literal["file", "directory"] | str
    LastModified: Optional[datetime]
    mtime: Optional[datetime]
