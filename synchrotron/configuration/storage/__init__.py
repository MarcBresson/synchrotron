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

    @cached_property
    def fs(self) -> AbstractFileSystem:
        """Return the filesystem object."""
        return filesystem(self.name, **self.options.model_dump())
