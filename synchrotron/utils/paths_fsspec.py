"""
Adaptation of fsspec abstract file system methods so that they are compatible
with detail=True and withdirs=False.

It could prove itself to be a maintenance burden, especially since there are
many backends that do not necessarily use this implementation. Nevertheless,
the two extracted functions are still 100% compatible with all backends
because it relies on .find method of each backend.
"""

from glob import has_magic
from typing import Literal, overload

from fsspec import AbstractFileSystem


def expand_paths(
    fs: AbstractFileSystem,
    paths: list[str],
    recursive: bool,
    maxdepth: int | None,
    detail: bool,
    **kwargs,
) -> dict[str, dict] | list[str]:
    if detail is True:
        out_details = {}
    else:
        out_list = []

    paths = [fs._strip_protocol(p) for p in paths]
    for p in paths:
        if has_magic(p):
            expanded_paths = glob(fs, p, maxdepth=maxdepth, detail=detail, **kwargs)

            if detail is True:
                out_details.update(expanded_paths)
            else:
                out_list.extend(expanded_paths)

            if recursive:
                if maxdepth is not None and maxdepth <= 1:
                    continue

                rec_paths = expand_paths(
                    fs,
                    list(expanded_paths),
                    recursive=True,
                    maxdepth=maxdepth - 1 if maxdepth is not None else None,
                    detail=detail,
                    **kwargs,
                )
                if detail is True:
                    out_details.update(rec_paths)
                else:
                    out_list.extend(rec_paths)
        elif recursive:
            rec = fs.find(p, maxdepth=maxdepth, detail=detail, **kwargs)

            if detail is True:
                out_details.update(rec)
            else:
                out_list.extend(rec)

    if detail is True:
        return out_details
    else:
        return out_list


@overload
def glob(
    fs: AbstractFileSystem,
    path: str,
    detail: Literal[True],
    maxdepth=None,
    **kwargs,
) -> dict[str, dict]: ...
@overload
def glob(
    fs: AbstractFileSystem,
    path: str,
    detail: Literal[False],
    maxdepth=None,
    **kwargs,
) -> list[str]: ...
def glob(
    fs: AbstractFileSystem, path: str, detail: bool, maxdepth=None, **kwargs
) -> dict[str, dict] | list[str]:
    """Find files by glob-matching.

    Pattern matching capabilities for finding files that match the given pattern.

    Parameters
    ----------
    path: str
        The glob pattern to match against
    maxdepth: int or None
        Maximum depth for ``'**'`` patterns. Applied on the first ``'**'`` found.
        Must be at least 1 if provided.
    kwargs:
        Additional arguments passed to ``find`` (e.g., detail=True)

    Returns
    -------
    List of matched paths, or dict of paths and their info if detail=True

    Notes
    -----
    Supported patterns:
    - '*': Matches any sequence of characters within a single directory level
    - ``'**'``: Matches any number of directory levels (must be an entire path component)
    - '?': Matches exactly one character
    - '[abc]': Matches any character in the set
    - '[a-z]': Matches any character in the range
    - '[!abc]': Matches any character NOT in the set

    Special behaviors:
    - If the path ends with '/', only folders are returned
    - Consecutive '*' characters are compressed into a single '*'
    - Empty brackets '[]' never match anything
    - Negated empty brackets '[!]' match any single character
    - Special characters in character classes are escaped properly

    Limitations:
    - ``'**'`` must be a complete path component (e.g., ``'a/**/b'``, not ``'a**b'``)
    - No brace expansion ('{a,b}.txt')
    - No extended glob patterns ('+(pattern)', '!(pattern)')
    """
    if maxdepth is not None and maxdepth < 1:
        raise ValueError("maxdepth must be at least 1")

    path = fs._strip_protocol(path)
    idx_star = path.find("*") if path.find("*") >= 0 else len(path)
    idx_qmark = path.find("?") if path.find("?") >= 0 else len(path)
    idx_brace = path.find("[") if path.find("[") >= 0 else len(path)

    min_idx = min(idx_star, idx_qmark, idx_brace)

    if not has_magic(path):
        if fs.exists(path, **kwargs):
            if not detail:
                return [path]
            else:
                return {path: fs.info(path, **kwargs)}
        else:
            if not detail:
                return []  # glob of non-existent returns empty
            else:
                return {}
    elif "/" in path[:min_idx]:
        min_idx = path[:min_idx].rindex("/")
        root = path[: min_idx + 1]
        depth = path[min_idx + 1 :].count("/") + 1
    else:
        root = ""
        depth = path[min_idx + 1 :].count("/") + 1

    if "**" in path:
        if maxdepth is not None:
            idx_double_stars = path.find("**")
            depth_double_stars = path[idx_double_stars:].count("/") + 1
            depth = depth - depth_double_stars + maxdepth
        else:
            depth = None

    allpaths = fs.find(root, maxdepth=depth, detail=detail, **kwargs)

    return allpaths
