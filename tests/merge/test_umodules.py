from stubber import merge_config, stubs_from_docs
from stubber.umodules import public_stub_names, write_umodule_stub


def test_public_stub_names_uses_explicit_all(tmp_path):
    stub = tmp_path / "module.pyi"
    stub.write_text(
        "__all__ = ['visible', '_explicit']\n"
        "def visible() -> None: ...\n"
        "def omitted() -> None: ...\n"
        "_explicit: int\n",
        encoding="utf-8",
    )

    assert public_stub_names(stub) == ["visible", "_explicit"]


def test_write_umodule_stub_reexports_public_surface(tmp_path):
    package = tmp_path / "time"
    package.mkdir()
    (package / "__init__.pyi").write_text(
        "from typing import Final\n"
        "from support import exported as exported\n"
        "EPOCH: Final[int]\n"
        "def time() -> float: ...\n"
        "class Clock: ...\n"
        "def _private() -> None: ...\n",
        encoding="utf-8",
    )

    target = write_umodule_stub(tmp_path, "time")

    assert target.read_text(encoding="utf-8") == (
        "# This umodule is a MicroPython reference to time\n"
        "from time import exported as exported\n"
        "from time import EPOCH as EPOCH\n"
        "from time import time as time\n"
        "from time import Clock as Clock\n"
    )


def test_recreate_umodules_replaces_package_alias(monkeypatch, tmp_path):
    (tmp_path / "os.pyi").write_text("def stat(path: str, /) -> object: ...\n", encoding="utf-8")
    old_alias = tmp_path / "uos"
    old_alias.mkdir()
    (old_alias / "__init__.pyi").write_text("from os import *\n", encoding="utf-8")
    monkeypatch.setattr(merge_config, "U_MODULES", ["os"])

    merge_config.recreate_umodules(tmp_path)

    assert not old_alias.exists()
    assert (tmp_path / "uos.pyi").read_text(encoding="utf-8") == (
        "# This umodule is a MicroPython reference to os\n"
        "from os import stat as stat\n"
    )


def test_make_docstubs_writes_explicit_aliases(monkeypatch, tmp_path):
    package = tmp_path / "binascii"
    package.mkdir()
    (package / "__init__.pyi").write_text("def hexlify(data: bytes, /) -> bytes: ...\n", encoding="utf-8")
    monkeypatch.setattr(stubs_from_docs, "U_MODULES", ["binascii"])

    stubs_from_docs.make_docstubs(tmp_path, "v1.29.0", "1.29.0", ".pyi", [], clean_rst=True)

    assert (tmp_path / "ubinascii.pyi").read_text(encoding="utf-8") == (
        "# This umodule is a MicroPython reference to binascii\n"
        "from binascii import hexlify as hexlify\n"
    )
