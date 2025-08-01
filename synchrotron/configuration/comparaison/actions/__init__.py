from typing import Literal

from pydantic import BaseModel


class CacheEnabledActions(BaseModel):
    created_left: Literal["copy_to_right", "remove", "nothing"]
    created_right: Literal["copy_to_left", "remove", "nothing"]
    updated_left: Literal["update_in_right", "update_in_left", "nothing"]
    updated_right: Literal["update_in_left", "update_in_right", "nothing"]
    removed_left: Literal["remove_in_right", "copy_right_to_left", "nothing"]
    removed_right: Literal["remove_in_left", "copy_left_to_right", "nothing"]


class CacheDisabledActions(BaseModel):
    only_exist_left: Literal["copy_to_right", "remove", "nothing"]
    only_exist_right: Literal["copy_to_left", "remove", "nothing"]
    file_is_different: Literal["update_in_right", "update_in_left", "nothing"]


class CacheDisabledDateTimeSizeComparaisonActions(BaseModel):
    only_exist_left: Literal["copy_to_right", "remove", "nothing"]
    only_exist_right: Literal["copy_to_left", "remove", "nothing"]
    more_recent_left: Literal["update_in_right", "update_in_left", "nothing"]
    more_recent_right: Literal["update_in_left", "update_in_right", "nothing"]
