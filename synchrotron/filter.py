"""
For each storage, we walk in the filesystems to find all elements that match the filters.

It builds up a collection of file details for each filesystem.
"""

from collections.abc import Iterator
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Generator, Literal, cast, overload

from synchrotron.configuration.filter import Filter, Filters
from synchrotron.configuration.storage import Storage
from synchrotron.schema.filter_properties import (
    DateTimeProperty,
    NumericalInequalityProperty,
)
from synchrotron.schema.molecules.fsspec_file_info import FileInfo
from synchrotron.utils.paths_fsspec import expand_paths


class FilterSvc:
    def __init__(
        self,
        filters: Filters,
        file_storage: Storage,
    ):
        self.filters = filters

        self.storage = file_storage
        self.fs = file_storage.fs

    def backend_check(self):
        """check if backends support the operations needed by the filters"""
        ...

    def walk(self):
        """Walk through storage and yields file paths for matching files."""
        included_files = self.include_files()

        if self.filters.exclude is None:
            return included_files

        excluded_paths = set(self.exclude_files())

        for included_file_path, included_file_details in included_files:
            if included_file_path in excluded_paths:
                yield included_file_path, included_file_details

    def include_files(self) -> Iterator[tuple[str, FileInfo]]:
        """
        Finds all files that must be included.

        Returns
        -------
        Iterator[tuple[str, FileInfo]]
            generator that iterates over a path name and its associated details.
        """
        return self.meet_filters(self.filters.include, include_file_details=True)

    def exclude_files(self) -> Iterator[str]:
        """
        Finds all file paths that must be excluded.

        Returns
        -------
        Iterator[str]
            generator that iterates over the file paths.
        """
        if self.filters.exclude is None:
            raise ValueError("There are no exclude filters configured.")
        return self.meet_filters(self.filters.exclude, include_file_details=False)

    @overload
    def meet_filters(
        self, filters: list[Filter], include_file_details: Literal[True]
    ) -> Iterator[tuple[str, FileInfo]]: ...
    @overload
    def meet_filters(
        self, filters: list[Filter], include_file_details: Literal[False]
    ) -> Iterator[str]: ...
    def meet_filters(
        self, filters: list[Filter], include_file_details: bool
    ) -> Iterator[tuple[str, FileInfo]] | Iterator[str]:
        base_path = self.storage.base_path

        for filter_ in filters:
            path_gen = assemble_filter_paths(base_path, filter_)
            paths_expanded_details = expand_paths(
                self.fs,
                (path.as_posix() for path in path_gen),
                recursive=True,
                maxdepth=None,
                detail=True,
                withdirs=False,
            )
            for file_path, file_info in paths_expanded_details:
                if meet_filter(file_info, filter_):
                    if include_file_details:
                        yield file_path, file_info
                    else:
                        yield file_path


def assemble_filter_paths(
    base_path: Path | None, filter_: Filter
) -> Generator[Path, None, None]:
    """Generate the full paths from a given filter and the storage base path."""
    path_prefix = assemble_paths(base_path, filter_.path_prefix)

    for path in filter_.paths:
        # because path (from the for loop) is necessarily not None, the new
        # assembled path will never be None either
        path = cast(Path, assemble_paths(path_prefix, path))
        assert path is not None
        yield path


@overload
def assemble_paths(*components: None) -> None: ...
@overload
def assemble_paths(*components: Path) -> Path: ...
@overload
def assemble_paths(*components: Path | None) -> Path: ...
def assemble_paths(*components: Path | None) -> Path | None:
    """Build the path prefix based on the base path and the path prefix.

    If all the components are None, then None will be returned.
    Otherwise, the None components are going to be ignored.
    """
    full_path = Path()
    for path in components:
        if path is not None:
            full_path /= path

    if full_path == Path():
        return None
    return full_path


MAP_PROPERTY_NAME_TO_DETAIL_ATTRIBUTES: dict[str, list[str]] = {
    "size": ["size"],
    "created": ["created"],
    "modified": ["mtime"],
}
"""map property names to the possible attributes in the file details dict"""


def meet_filter(file_details: FileInfo, filter_: Filter) -> bool:
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
        path = Path(file_details["name"])
        if path.suffix.lstrip(".") not in filter_.extensions:
            return False

    return True


def compare_numerical(
    prop: NumericalInequalityProperty, file_details: FileInfo
) -> bool:
    """Compare numerical properties in the file details."""
    value: float = find_prop_in_detail(prop.name, file_details)
    if prop.inequality_direction == "greater_than":
        if value < prop.value:
            return False
    elif prop.inequality_direction == "less_than":
        if value > prop.value:
            return False

    return True


def compare_datetime(prop: DateTimeProperty, file_details: FileInfo) -> bool:
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


def find_prop_in_detail(prop_name: str, file_details: FileInfo) -> Any:
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
