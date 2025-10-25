from datetime import datetime

from synchrotron.schema.molecules.fsspec_file_info import FileInfo
from synchrotron.utils.get_one_of import get_one_of


def get_modifed_time(file_info: FileInfo) -> datetime:
    return datetime.fromtimestamp(get_one_of(file_info, ["LastModified", "mtime"]))
