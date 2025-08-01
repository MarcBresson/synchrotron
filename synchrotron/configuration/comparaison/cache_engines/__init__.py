from typing import Literal

from pydantic import BaseModel


class DatabaseCacheEngine(BaseModel):
    cache_engine: Literal["database"] = "database"
    engine_url: str
    engine_options: dict[str, str] = {}
