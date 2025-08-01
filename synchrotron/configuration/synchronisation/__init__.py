from typing import Literal

from pydantic import BaseModel

from .conflict import ForceResolveConflict, VersionedConflict


class Synchronisation(BaseModel):
    conflict_handling: (
        VersionedConflict
        | ForceResolveConflict
        | Literal["warn"]
        | Literal["cancel_synchronisation"]
    ) = "warn"
