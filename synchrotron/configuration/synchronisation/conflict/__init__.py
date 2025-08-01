from string import Template
from typing import Literal

from pydantic import BaseModel, ConfigDict


class VersionedConflict(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    file_name_suffix: Template = Template("${conflict_type}_${datetime}_${id}")
    side_of_the_version: Literal["both", "left", "right"]


class ForceResolveConflict(BaseModel):
    truth: Literal["left", "right"]
