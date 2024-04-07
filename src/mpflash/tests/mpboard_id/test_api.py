import pytest

from mpflash.mpboard_id.api import find_stored_board, known_stored_boards, local_mp_ports, read_stored_boardinfo

pytestmark = [pytest.mark.mpflash]


def test_read_boardinfo():
    boards = read_stored_boardinfo()
    assert isinstance(boards, list)
    assert all(isinstance(board, dict) for board in boards)


def test_known_mp_ports():
    ports = local_mp_ports()
    assert isinstance(ports, list)
    assert all(isinstance(port, str) for port in ports)


@pytest.mark.parametrize(
    "port, versions",
    [
        ("rp2", ["1.20.0"]),
        ("rp2", ["1.20.0", "1.17.3"]),
        ("rp2", ["preview"]),
        ("rp2", ["stable"]),
    ],
)
def test_known_mp_boards(port, versions):
    l = known_stored_boards(port, versions)
    assert isinstance(l, list)
    assert all(isinstance(t, tuple) for t in l)
    assert all(isinstance(t[0], str) and isinstance(t[1], str) for t in l)
    # TODO"check the version
    assert all("[stable]" not in t[0] for t in l)
    assert all("[preview]" not in t[0] for t in l)


def test_find_mp_board():
    board = find_stored_board("PYBV11")
    assert isinstance(board, dict)
    assert "board" in board
    assert "description" in board
    assert "port" in board
    assert "version" in board
    assert "cpu" in board
