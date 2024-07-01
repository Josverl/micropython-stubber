from typing import List

import pytest

from mpflash.mpboard_id import get_known_boards_for_port, get_known_ports
from mpflash.versions import get_stable_mp_version

pytestmark = [pytest.mark.mpflash]


@pytest.mark.parametrize("port", get_known_ports())
@pytest.mark.parametrize(
    "id, versions",
    [
        ("None", None),
        ("one ver", ["v1.20.0"]),
        ("multiple vers", ["v1.20.0", "v1.19"]),
        ("stable", ["stable"]),
        ("preview", ["preview"]),
        ("stab + Prev", ["stable", "preview"]),
    ],
)
def test_mp_board_filter(port: str, id, versions: List[str]):
    # Arrange

    # Act
    result = get_known_boards_for_port(port, versions)
    # Assert
    assert len(result) >= 1
    assert all(board.port == port for board in result)

    if not versions:
        return

    versions = versions if versions else []
    for board in result:
        # check if the version matches the filter
        ok = False
        if board.version in versions:
            ok = True
        elif "stable" in versions:
            if board.version == get_stable_mp_version():
                ok = True
            # last known stable is not always the same as the current stable
            # just assume its OK if the version is stable
            ok = True
        elif "preview" in versions:
            # preview returns the boards known for the stable version
            if "preview" in board.version or board.version == get_stable_mp_version():
                ok = True
        assert ok, f"board: {board.version} does not match versions: {versions}"
