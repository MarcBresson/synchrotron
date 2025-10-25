import logging
from pathlib import Path
from typing import Literal, cast

from synchrotron.configuration.comparaison import (
    AllComparaison,
    DateTimeSizeCacheComparaison,
)
from synchrotron.configuration.comparaison.actions import (
    CacheEnabledDateTimeSizeComparaisonState,
)
from synchrotron.configuration.storage import Storage
from synchrotron.database.models.storage_file import StorageFile
from synchrotron.database.utils import session_manager
from synchrotron.schema.molecules.fsspec_file_info import FileInfo
from synchrotron.utils.file_info import get_modifed_time
from synchrotron.utils.github_issue import prefilled_issue_link

logger = logging.getLogger(__name__)


class ComparaisonSvc:
    def __init__(
        self, config: AllComparaison, storage_left: Storage, storage_right: Storage
    ) -> None:
        self.config = config
        self.storage_left = storage_left
        self.fs_left = storage_left.fs
        self.storage_right = storage_right
        self.fs_right = storage_right.fs

    def compare(
        self, path_left: Path, path_right: Path, storage_id: int
    ) -> CacheEnabledDateTimeSizeComparaisonState | None:
        """
        Compare the two files content according to the configuration provided.
        """
        left_file_db = None
        right_file_db = None
        if self.config.cache == "enabled":
            left_file_db = self.get_file_from_db(storage_id, path_left)
            right_file_db = self.get_file_from_db(storage_id, path_right)

        left_file_info = get_file_info(self.storage_left, path_left)
        right_file_info = get_file_info(self.storage_right, path_right)

        if self.config.cache == "enabled" and isinstance(
            self.config, DateTimeSizeCacheComparaison
        ):
            left_file_state = get_file_state_datetime_comparison(
                left_file_info, left_file_db
            )
            right_file_state = get_file_state_datetime_comparison(
                right_file_info, right_file_db
            )

            if left_file_state == "CREATED" and right_file_state == "NOT_EXISTING":
                return "created_left"
            elif right_file_state == "CREATED" and left_file_state == "NOT_EXISTING":
                return "created_right"
            elif left_file_state == "DELETED" and right_file_state == "UNTOUCHED":
                return "removed_left"
            elif right_file_state == "DELETED" and left_file_state == "UNTOUCHED":
                return "removed_right"
            elif left_file_state == "UNTOUCHED" and right_file_state == "UNTOUCHED":
                return None

            if left_file_info is not None and right_file_info is not None:
                left_right_time_dif = get_modifed_time(
                    left_file_info
                ) - get_modifed_time(right_file_info)
                if left_right_time_dif.seconds < 0:
                    return "more_recent_right"
                elif left_right_time_dif.seconds > 0:
                    return "more_recent_left"
                else:
                    logger.warning(
                        "One of the file (at source or destination) was touched, "
                        "but both source and destination have the same timestamp."
                    )
                    return None

            error_msg = (
                f"Unexpected behaviour. Got {left_file_state=} and {right_file_state=}."
            )
            github_url = prefilled_issue_link(
                title="comparaison did not complete", body=error_msg
            )
            logger.error(f"{error_msg}. Please report this error at {github_url}")

            return None

    def get_file_from_db(self, storage_id: int, path: Path) -> StorageFile | None:
        with session_manager() as session:
            storage_file = (
                session.query(StorageFile)
                .filter(
                    StorageFile.relative_path == path,
                    StorageFile.storage_id == storage_id,
                )
                .one_or_none()
            )
            return storage_file


def get_file_info(storage: Storage, file_path: Path) -> FileInfo | None:
    try:
        return cast(FileInfo, storage.fs.info(storage.joinpath(file_path)))
    except FileNotFoundError:
        return None


def get_file_state_datetime_comparison(
    file_info: FileInfo | None, file_db: StorageFile | None
) -> Literal["UPDATED", "CREATED", "DELETED", "UNTOUCHED", "NOT_EXISTING"]:
    """Compare the file info with their cache counterparts.

    Returns
    -------
    Literal["UPDATED", "CREATED", "DELETED", "UNTOUCHED", "NOT_EXISTING"]
        status of the file comapred to the cache.
    """
    if file_info is None and file_db is None:
        return "NOT_EXISTING"
    elif file_info is None:
        return "DELETED"
    elif file_db is None:
        return "CREATED"

    file_modified = get_modifed_time(file_info)

    if file_db.modified_datetime < file_modified:
        return "UPDATED"
    elif file_db.modified_datetime == file_modified:
        return "UNTOUCHED"
    else:
        logger.warning(
            f"File {file_info['name']} is more recent in cache than in the FS. "
            "It could mean that it got replace with an older file."
        )
        return "UPDATED"
