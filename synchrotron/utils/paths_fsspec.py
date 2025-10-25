"""
Adaptation of fsspec abstract file system methods so that they are compatible
with detail=True and withdirs=False and that returns a generator.

It could prove itself to be a maintenance burden, especially since there can be
backends that do not use this implementation. Nevertheless, the extracted
function is still 100% compatible with all backends because it relies on
common methods.
"""

from glob import has_magic
from typing import Iterator, Literal, Sequence, cast, overload

from fsspec import AbstractFileSystem

from synchrotron.schema.molecules.fsspec_file_info import FileInfo


@overload
def expand_paths(
    fs: AbstractFileSystem,
    paths: Sequence[str] | Iterator[str],
    recursive: bool,
    maxdepth: int | None,
    detail: Literal[True],
    withdirs: bool = False,
    **kwargs,
) -> Iterator[tuple[str, FileInfo]]: ...
@overload
def expand_paths(
    fs: AbstractFileSystem,
    paths: Sequence[str] | Iterator[str],
    recursive: bool,
    maxdepth: int | None,
    detail: Literal[False],
    withdirs: bool = False,
    **kwargs,
) -> Iterator[str]: ...
def expand_paths(
    fs: AbstractFileSystem,
    paths: Sequence[str] | Iterator[str],
    recursive: bool,
    maxdepth: int | None,
    detail: bool,
    withdirs: bool = False,
    **kwargs,
) -> Iterator[tuple[str, FileInfo] | str]:
    paths = (fs._strip_protocol(p) for p in paths)
    for p in paths:
        if has_magic(p):
            expanded_paths = cast(
                dict[str, FileInfo],
                fs.glob(p, maxdepth=maxdepth, detail=True, **kwargs),
            )

            if withdirs is False:
                expanded_paths = {
                    p: info
                    for p, info in sorted(expanded_paths.items())
                    if info["type"] == "file"
                }

            if detail is True:
                yield from expanded_paths.items()
            else:
                yield from expanded_paths.keys()

            if recursive:
                if maxdepth is not None and maxdepth <= 1:
                    continue

                rec_paths = expand_paths(
                    fs,
                    list(expanded_paths),
                    recursive=True,
                    maxdepth=maxdepth - 1 if maxdepth is not None else None,
                    detail=True,
                    **kwargs,
                )
                yield from rec_paths
        elif recursive:
            rec = cast(
                dict[str, dict],
                fs.find(p, maxdepth=maxdepth, detail=True, withdirs=withdirs, **kwargs),
            )

            if detail is True:
                yield from rec.items()
            else:
                yield from rec.keys()
