"""
For each storage, we walk in the filesystems to find all elements that match the filters.

It builds up a collection of file details for each filesystem.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from synchrotron.configuration.filter import Filter, Filters
from synchrotron.configuration.storage import Storage
from synchrotron.schema.filter_properties import (
    DateTimeProperty,
    NumericalInequalityProperty,
)
from synchrotron.utils.paths_fsspec import expand_paths


class FilterSvc:
    def __init__(
        self,
        filters: Filters,
        left_storage: Storage,
        right_storage: Storage,
    ):
        self.filters = filters

        self.left_storage = left_storage
        self.right_storage = right_storage
        self.left_fs = left_storage.fs
        self.right_fs = right_storage.fs

    def backend_check(self):
        """check if backends support the operations needed by the filters"""
        ...

    def walk_left(
        self, include_details: bool = False, with_right_details: bool = False
    ):
        """Walk through the left storage and apply filters."""
        base_path = self.left_storage.base_path
        for filter_ in self.filters.include:
            path_prefix = assemble_paths(base_path, filter_.path_prefix)

            for path in filter_.paths:
                path = assemble_paths(path_prefix, path)

                expand_paths(
                    self.left_fs,
                    [path],
                    recursive=True,
                    maxdepth=None,
                    detail=True,
                    withdirs=False,
                )
                for left_file_details in self.left_fs.walk(
                    path, on_error="raise", detail=include_details
                ):
                    # see if it matches the filter criteria
                    ...

            for regex_path in filter_.regex_paths:
                regex_path = assemble_paths(path_prefix, regex_path)
                for left_file_details in self.left_fs.glob(
                    assemble_paths(base_path, regex_path), detail=include_details
                ):
                    # see if it matches the filter criteria
                    ...

    def meet_left_filter(self, file_details): ...


def assemble_paths(*components: Path | None) -> Path | None:
    """Build the path prefix based on the base path and the path prefix."""
    full_path = Path()
    for path in components:
        if path is not None:
            full_path /= path

    if full_path == Path():
        return None
    return full_path


def include_or_exclude_file(file_details: dict[str, Any], filters: Filters) -> bool:
    """Check if the file details should be included or excluded based on the filters.

    If one of the include filters matches, the file is included.
    If one of the exclude filters matches, the file is excluded.
    """
    for include_filter in filters.include:
        if meet_filter(file_details, include_filter):
            return True

    if filters.exclude is None:
        return False

    for exclude_filter in filters.exclude:
        if meet_filter(file_details, exclude_filter):
            return False

    return False


MAP_PROPERTY_NAME_TO_DETAIL_ATTRIBUTES: dict[str, list[str]] = {
    "size": ["size"],
    "created": ["created"],
    "modified": ["mtime"],
}
"""map property names to the possible attributes in the file details dict"""


def meet_filter(file_details: dict, filter_: Filter) -> bool:
    """Check if the file details meet the filter criteria."""
    filter_properties = filter_.used_filters()
    filter_result = True

    for prop in filter_properties:
        if isinstance(prop, NumericalInequalityProperty):
            filter_result = filter_result & compare_numerical(prop, file_details)
        elif isinstance(prop, DateTimeProperty):
            filter_result = filter_result & compare_datetime(prop, file_details)

        if filter_result is False:
            return False

    if filter_.extensions is not None:
        path = Path(file_details["path"])
        if path.suffix.lstrip(".") not in filter_.extensions:
            return False

    return True


def compare_numerical(prop: NumericalInequalityProperty, file_details: dict) -> bool:
    """Compare numerical properties in the file details."""
    value: float = find_prop_in_detail(prop.name, file_details)
    if prop.inequality_direction == "greater_than":
        if value < prop.value:
            return False
    elif prop.inequality_direction == "less_than":
        if value > prop.value:
            return False

    return True


def compare_datetime(prop: DateTimeProperty, file_details: dict) -> bool:
    """Compare datetime properties in the file details."""
    value: float = find_prop_in_detail(prop.name, file_details)
    dt_value = datetime.fromtimestamp(value)
    if prop.inequality_direction == "greater_than":
        if isinstance(prop.value, timedelta) and dt_value - datetime.now() > prop.value:
            return False
        if isinstance(prop.value, datetime) and dt_value < prop.value:
            return False
    elif prop.inequality_direction == "less_than":
        if isinstance(prop.value, timedelta) and dt_value - datetime.now() < prop.value:
            return False
        if isinstance(prop.value, datetime) and dt_value > prop.value:
            return False

    return True


def find_prop_in_detail(prop_name: str, file_details: dict) -> Any:
    """Find the property in the file details."""
    if prop_name in MAP_PROPERTY_NAME_TO_DETAIL_ATTRIBUTES:
        for attr in MAP_PROPERTY_NAME_TO_DETAIL_ATTRIBUTES[prop_name]:
            if attr in file_details:
                return file_details[attr]

        raise ValueError(
            f"Property '{prop_name}' not found in file details. Specified left "
            "or right storage might not be compatible. Available attributes: "
            f"{file_details.keys()}"
        )
    else:
        if prop_name in file_details:
            return file_details[prop_name]

        raise ValueError(
            f"Property '{prop_name}' not found in file details. Available "
            f"attributes: {file_details.keys()}"
        )
