from typing import Literal

from pydantic import BaseModel

CacheEnabledState = Literal[
    "created_left",
    "created_right",
    "updated_left",
    "updated_right",
    "removed_left",
    "removed_right",
]


class CacheEnabledActions(BaseModel):
    created_left: Literal["copy_to_right", "remove", "nothing"]
    created_right: Literal["copy_to_left", "remove", "nothing"]
    updated_left: Literal["update_in_right", "update_in_left", "nothing"]
    updated_right: Literal["update_in_left", "update_in_right", "nothing"]
    removed_left: Literal["remove_in_right", "copy_right_to_left", "nothing"]
    removed_right: Literal["remove_in_left", "copy_left_to_right", "nothing"]


CacheDisabledState = Literal[
    "only_exist_left",
    "only_exist_right",
    "file_is_different",
]


class CacheDisabledActions(BaseModel):
    only_exist_left: Literal["copy_to_right", "remove", "nothing"]
    only_exist_right: Literal["copy_to_left", "remove", "nothing"]
    file_is_different: Literal["update_in_right", "update_in_left", "nothing"]


CacheDisabledDateTimeSizeComparaisonState = Literal[
    "only_exist_left",
    "only_exist_right",
    "more_recent_left",
    "more_recent_right",
]


class CacheDisabledDateTimeSizeComparaisonActions(BaseModel):
    only_exist_left: Literal["copy_to_right", "remove", "nothing"]
    only_exist_right: Literal["copy_to_left", "remove", "nothing"]
    more_recent_left: Literal["update_in_right", "update_in_left", "nothing"]
    more_recent_right: Literal["update_in_left", "update_in_right", "nothing"]


CacheEnabledDateTimeSizeComparaisonState = Literal[
    "created_left",
    "created_right",
    "more_recent_left",
    "more_recent_right",
    "removed_left",
    "removed_right",
]


class CacheEnabledDateTimeSizeComparaisonActions(BaseModel):
    created_left: Literal["copy_to_right", "remove", "nothing"]
    created_right: Literal["copy_to_left", "remove", "nothing"]
    more_recent_left: Literal["update_in_right", "update_in_left", "nothing"]
    more_recent_right: Literal["update_in_left", "update_in_right", "nothing"]
    removed_left: Literal["remove_in_right", "copy_right_to_left", "nothing"]
    removed_right: Literal["remove_in_left", "copy_left_to_right", "nothing"]
