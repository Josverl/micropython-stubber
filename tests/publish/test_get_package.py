import sqlite3
import tempfile
from pathlib import Path

import pytest
from stubber.publish.package import get_package, get_package_info
from stubber.publish.stubpackage import StubPackage


@pytest.mark.parametrize(
    "mpy_version, pkg_name",
    [
        ("1.18", "micropython-esp32-stubs"),
        ("1.20.0", "micropython-rp2-pico-stubs"),
        ("1.22.1", "micropython-rp2-rpi_pico-stubs"),
        # TODO:  Fix naming of these packages
        ("1.23.0", "micropython-esp32-esp32_generic_c3-stubs"),
        ("1.23.0", "micropython-esp32-esp32_generic-stubs"),
    ],
)
# @pytest.mark.parametrize("pkg_name", ["micropython-esp32-stubs"])
def test_get_package_info(test_db_conn, pkg_name, mpy_version):

    pub_path = Path(tempfile.gettempdir())

    package_info = get_package_info(
        test_db_conn, pub_path, pkg_name=pkg_name, mpy_version=mpy_version
    )
    assert package_info is not None
    assert package_info["name"] == pkg_name
    assert package_info["mpy_version"] == mpy_version
    assert package_info["pkg_version"].startswith(mpy_version)
    assert package_info["pkg_version"] > mpy_version
    # Hashes
    assert package_info["stub_hash"], "stub only hash not found"
    assert package_info["hash"], "Hash not found"
    # Stub sources - string
    assert package_info["stub_sources"], "Stub sources not found"
    assert isinstance(package_info["stub_sources"], str), "Stub sources is not a string"


def test_get_package_info_no_match(test_db_conn, tmp_path):
    pub_path = tmp_path
    pkg_name = "micropython-esp32-stubs"
    mpy_version = "1.13.1"

    package_info = get_package_info(
        test_db_conn, pub_path, pkg_name=pkg_name, mpy_version=mpy_version
    )
    assert package_info is None

    def test_get_package_info_invalid_version(test_db_conn):
        pub_path = Path(tempfile.gettempdir())
        pkg_name = "micropython-esp32-stubs"
        mpy_version = "invalid_version"

        with pytest.raises(ValueError):
            get_package_info(test_db_conn, pub_path, pkg_name=pkg_name, mpy_version=mpy_version)


# def test_get_package_info_empty_package_name(test_db_conn):
#     pub_path = Path(tempfile.gettempdir())
#     pkg_name = ""
#     mpy_version = "1.18"

#     with pytest.raises(ValueError):
#         get_package_info(test_db_conn, pub_path, pkg_name=pkg_name, mpy_version=mpy_version)


@pytest.mark.parametrize(
    "mpy_version, port, board",
    [
        ("1.18", "esp32", "generic"),
        ("1.20.0", "rp2", "pico"),
        ("1.22.1", "rp2", "rpi_pico"),
        # ("1.23.0", "esp32", "generic_c3"),
        # ("1.23.0", "esp32", "generic"),
    ],
)
def test_get_package(test_db_conn, mpy_version, port, board):
    package = get_package(test_db_conn, port=port, board=board, version=mpy_version)
    assert package is not None
    assert package.port == port
    assert package.board == board or board == "generic"
    assert package.mpy_version == mpy_version
    assert package.hash, "Hash not found"
    assert package.stub_hash, "Stub only hash not found"


def test_qandd():
    pkg_name = "micropython-esp32-stubs"
    port = "esp32"
    board = "generic"
    version = "1.18"
    package_info = {
        "id": 614587032550805777,
        "name": "micropython-esp32-stubs",
        "description": "MicroPython stubs",
        "mpy_version": "1.18",
        "pkg_version": "1.18.post3",
        "publish": 1,
        "stub_sources": '[["Merged stubs", "micropython-v1_18-esp32-merged"], ["Frozen stubs", "micropython-v1_18-frozen/esp32/GENERIC"], ["Core Stubs", "micropython-core"]]',
        "path": "micropython-v1_18-esp32-stubs",
        "hash": "ea79cc2c8b929dd33ac489fcd882b0272d75b83d",
        "stub_hash": "50ef8cbd42e9599a892217ce1ef16cbed98e2466 ",
        "port": "esp32",
        "board": "",
        "variant": "",
    }

    p_db = StubPackage(
        pkg_name,
        port,
        board=board,
        version=version,
        json_data=package_info,
    )

    assert p_db is not None
    assert p_db.port == port
    assert p_db.hash, "Hash not found"
    assert p_db.stub_hash, "Stub only hash not found"
