from pathlib import Path

from pytest_mock import MockerFixture

from stubber.freeze.freeze_manifest_2 import _warn_ignored_c_modules
from stubber.tools.manifestfile import MODE_FREEZE, ManifestFile


def test_c_module_is_collected_and_manifest_processing_continues(tmp_path: Path):
    c_module = tmp_path / "native"
    c_module.mkdir()
    (c_module / "micropython.cmake").touch()
    module = tmp_path / "frozen.py"
    module.write_text("value = 1")
    manifest = ManifestFile(MODE_FREEZE, {"MPY_LIB_DIR": None})

    manifest.execute('c_module({!r}); module("frozen.py", base_path={!r})'.format(str(c_module), str(tmp_path)))

    assert manifest.c_modules() == [str(c_module)]
    assert [result.full_path for result in manifest.files()] == [str(module)]


def test_ignored_c_module_emits_warning(tmp_path: Path, mocker: MockerFixture):
    c_module = tmp_path / "native"
    c_module.mkdir()
    (c_module / "micropython.mk").touch()
    manifest = ManifestFile(MODE_FREEZE, {"MPY_LIB_DIR": None})
    manifest.c_module(str(c_module))
    warning = mocker.patch("stubber.freeze.freeze_manifest_2.log.warning", autospec=True)

    _warn_ignored_c_modules(manifest)

    warning.assert_called_once_with(f"C module is not processed: {c_module}")
