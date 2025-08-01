from abc import ABC
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from .actions import (
    CacheDisabledActions,
    CacheDisabledDateTimeSizeComparaisonActions,
    CacheEnabledActions,
)
from .cache_engines import DatabaseCacheEngine


class CacheDisabledComparaison(BaseModel):
    type: Literal["content", "size"]
    cache: Literal["disabled"]
    actions: CacheDisabledActions


class DateTimeSizeComparaisonABC(BaseModel, ABC):
    type: Literal["datetime_size"]
    time_zone_shift: str = Field(
        pattern=r"^[-+]\d{2}:\d{2}$",
        description="Time zone shift in format -HH:MM or +HH:MM use for synchronization between a FAT system (that uses local time) and a NTFS filesystem (that uses UTC).",
    )


class DateTimeSizeDisabledCacheComparaison(DateTimeSizeComparaisonABC):
    cache: Literal["disabled"]
    actions: CacheDisabledDateTimeSizeComparaisonActions


AllCacheComparaison = DatabaseCacheEngine
AllCacheComparaisonDiscriminator = Annotated[
    AllCacheComparaison, Field(discriminator="cache_engine")
]


class DateTimeSizeCacheComparaison(DateTimeSizeComparaisonABC):
    cache: Literal["enabled"]
    cache_engine: AllCacheComparaisonDiscriminator
    actions: CacheEnabledActions


AllDateTimeSizeComparaison = (
    DateTimeSizeCacheComparaison | DateTimeSizeDisabledCacheComparaison
)
AllDateTimeSizeComparaisonDiscriminator = Annotated[
    AllDateTimeSizeComparaison, Field(discriminator="cache")
]

AllComparaison = AllDateTimeSizeComparaisonDiscriminator | CacheDisabledComparaison
AllComparaisonDiscriminator = Annotated[AllComparaison, Field(discriminator="type")]
