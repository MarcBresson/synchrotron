from collections.abc import Mapping, Sequence
from typing import Any


def get_one_of(data: Mapping[str, Any], possible_attributes: Sequence[str]) -> Any:
    """Get the first attribute that is not None in the data.

    Parameters
    ----------
    data : dict[str, Any]
        Data to get the attributes from.
    possible_attributes : Sequence[str]
        List of attributes to look for in the data.

    Returns
    -------
    Any
        The first attribute that is not None.

    Raises
    ------
    KeyError
        If none of the attributes are in the data.
    """
    for attribute in possible_attributes:
        if attribute in data:
            return data[attribute]

    raise KeyError(f"None of the attributes {possible_attributes} are in the data.")
