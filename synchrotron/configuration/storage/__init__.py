from functools import cached_property
from pathlib import Path

from fsspec import AbstractFileSystem, filesystem
from pydantic import BaseModel, ConfigDict


class StorageParameters(BaseModel):
    model_config = ConfigDict(extra="allow")


class Storage(BaseModel):
    name: str = "file"
    """See https://filesystem-spec.readthedocs.io/en/latest/api.html#built-in-implementations
    and https://filesystem-spec.readthedocs.io/en/latest/api.html#other-known-implementations
    for all the existing implementation.
    """
    options: StorageParameters = StorageParameters()
    base_path: Path | None = None
    """Base path for the storage. If not set, the root of the filesystem is used."""
    id: int
    """
    Unique identifier for the storage. It is used for the cache DB to identify
    to which storage the record belonged to.
    """

    @cached_property
    def fs(self) -> AbstractFileSystem:
        """Return the filesystem object."""
        return filesystem(self.name, **self.options.model_dump())

    def joinpath(self, path: str | Path) -> str:
        base_path = self.base_path or ""
        return str(base_path) + self.fs.sep + str(path)
