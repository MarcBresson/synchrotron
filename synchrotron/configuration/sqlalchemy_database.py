from typing import Annotated

from pydantic import AnyUrl, BaseModel, BeforeValidator, ConfigDict, SecretStr

AnyURLAsStr = Annotated[
    str,
    BeforeValidator(lambda value: AnyUrl(value) and str(value)),
]


class PostgresEngineOptionsConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    pool_size: int = 1
    """
    Number of connection to keep open with the DB. This is the largest number
    of connections that will be kept persistently in the pool.
    """
    max_overflow: int = 1
    """
    The maximum overflow size of the pool. When the number of checked-out
    connections reaches the size set in pool_size, additional connections will
    be returned up to this limit. When those additional connections are
    returned to the pool, they are disconnected and discarded. It follows then
    that the total number of simultaneous connections the pool will allow is
    pool_size + max_overflow, and the total number of “sleeping” connections the
    pool will allow is pool_size.
    """


class EngineAnyOptionsConfig(BaseModel):
    model_config = ConfigDict(extra="allow")


class EngineCredentialConfig(BaseModel):
    host: str
    db_name: str
    username: str
    password: SecretStr
    port: int
    dialect: str
    key_value: dict[str, str] | None = None

    def _url(self) -> str:
        protocol = f"{self.dialect}"
        credentials = f"{self.username}:{self.password.get_secret_value()}"
        address = f"{self.host}:{self.port}/{self.db_name}"

        args = ""
        if self.key_value:
            args = "?" + "&".join([f"{k}={v}" for k, v in self.key_value.items()])

        return f"{protocol}://{credentials}@{address}{args}"

    def __str__(self) -> str:
        return self._url()


class SQLAlchemyDBConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    engine_options: PostgresEngineOptionsConfig | EngineAnyOptionsConfig = (
        EngineAnyOptionsConfig()
    )
    """use `str(config.engine_url)` to get the actual URL string whatever the underlying type is."""
    engine_url: EngineCredentialConfig | AnyURLAsStr
