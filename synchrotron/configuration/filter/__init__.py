from pathlib import Path

from pydantic import BaseModel, ByteSize, PastDate, field_validator, model_validator

from synchrotron.schema.filter_properties import (
    DateTimeProperty,
    NumericalInequalityProperty,
)
from synchrotron.utils.pydantic_extra_types import Duration


class Filter(BaseModel):
    max_size: ByteSize | None = None
    min_size: ByteSize | None = None
    created_after: Duration | PastDate | None = None
    created_before: Duration | PastDate | None = None
    modified_after: Duration | PastDate | None = None
    modified_before: Duration | PastDate | None = None
    extensions: list[str] | None = None
    """
    List of file extensions to filter by. See pathlib.Path.suffix for more details.
    If not set, all extensions are considered.
    """
    path_prefix: Path | None = None
    """Path prefix to filter files by their path. If not set, all paths are considered."""
    paths: list[Path] = []
    regex_paths: list[Path] = []

    def used_filters(self) -> list[NumericalInequalityProperty | DateTimeProperty]:
        """translate the config into a list of properties that can be used by the filter engine."""
        properties = []
        if self.max_size is not None:
            properties.append(
                NumericalInequalityProperty(
                    name="size",
                    value=self.max_size,
                    inequality_direction="less_than",
                )
            )
        if self.min_size is not None:
            properties.append(
                NumericalInequalityProperty(
                    name="size",
                    value=self.min_size,
                    inequality_direction="greater_than",
                )
            )
        if self.created_after is not None:
            properties.append(
                DateTimeProperty(
                    name="created",
                    value=self.created_after,
                    inequality_direction="greater_than",
                )
            )
        if self.created_before is not None:
            properties.append(
                DateTimeProperty(
                    name="created",
                    value=self.created_before,
                    inequality_direction="less_than",
                )
            )
        if self.modified_after is not None:
            properties.append(
                DateTimeProperty(
                    name="modified",
                    value=self.modified_after,
                    inequality_direction="greater_than",
                )
            )
        if self.modified_before is not None:
            properties.append(
                DateTimeProperty(
                    name="modified",
                    value=self.modified_before,
                    inequality_direction="less_than",
                )
            )
        return properties

    @field_validator("extensions", mode="after")
    @classmethod
    def extensions_field_validator(cls, v: list[str] | None) -> list[str] | None:
        """Ensure that extensions do not contain the leading period."""
        if v is not None:
            return [ext.lstrip(".") for ext in v]
        return v

    @model_validator(mode="after")
    def validate_paths(self):
        if self.paths == [] and self.regex_paths == []:
            raise ValueError("At least one of 'paths' or 'regex_paths' must be set.")

        return self


class Filters(BaseModel):
    exclude: list[Filter] | None = None
    include: list[Filter]
