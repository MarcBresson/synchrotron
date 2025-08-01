from pathlib import Path

import pytest

from synchrotron.filter import assemble_paths


@pytest.mark.parametrize(
    "components, expected_results",
    [
        ([Path("a"), Path("b"), Path("c")], Path("a/b/c")),
        ([Path("a"), None, Path("c")], Path("a/c")),
        ([None, None, None], None),
    ],
)
def test_build_path_prefix(
    components: list[Path | None], expected_results: Path | None
):
    results = assemble_paths(*components)
    assert expected_results == results
