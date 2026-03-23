"""Tests for the manifest creation utilities."""
import json
from pathlib import Path

from stubber.utils.manifest import make_manifest, manifest


class TestManifestFunction:
    """Tests for the manifest() function."""

    def test_manifest_with_board_includes_board_field(self):
        """manifest() should include a 'board' field when board is provided."""
        result = manifest(family="micropython", port="esp32", board="GENERIC", version="1.20.0")
        assert "board" in result["firmware"]
        assert result["firmware"]["board"] == "GENERIC"

    def test_manifest_without_board_excludes_board_field(self):
        """manifest() should not include a 'board' field when board is not provided."""
        result = manifest(family="micropython", port="esp32", version="1.20.0")
        assert "board" not in result["firmware"]

    def test_manifest_firmware_string_includes_board(self):
        """manifest() firmware string should include board when provided."""
        result = manifest(family="micropython", port="esp32", board="GENERIC", version="1.20.0")
        assert "GENERIC" in result["firmware"]["firmware"]
        assert result["firmware"]["firmware"] == "micropython-esp32-GENERIC-v1_20_0"

    def test_manifest_firmware_string_without_board(self):
        """manifest() firmware string should not include board when not provided."""
        result = manifest(family="micropython", port="esp32", version="1.20.0")
        assert result["firmware"]["firmware"] == "micropython-esp32-v1_20_0"

    def test_manifest_port_and_version(self):
        """manifest() should correctly set port and version."""
        result = manifest(family="micropython", port="rp2", board="RPI_PICO", version="1.24.1")
        assert result["firmware"]["port"] == "rp2"
        assert result["firmware"]["version"] == "1.24.1"
        assert result["firmware"]["board"] == "RPI_PICO"

    def test_manifest_machine_set_to_board(self):
        """manifest() should set machine to board when board is provided via machine."""
        result = manifest(family="micropython", port="rp2", machine="RPI_PICO", board="RPI_PICO", version="1.24.1")
        assert result["firmware"]["machine"] == "RPI_PICO"

    def test_manifest_machine_and_board_can_differ(self):
        """manifest() allows machine and board to have different values - machine is the CPU, board is the board name."""
        result = manifest(family="micropython", port="rp2", machine="RP2040", board="RPI_PICO", version="1.24.1")
        assert result["firmware"]["machine"] == "RP2040"
        assert result["firmware"]["board"] == "RPI_PICO"


class TestMakeManifestFunction:
    """Tests for the make_manifest() function."""

    def test_make_manifest_creates_modules_json(self, tmp_path: Path):
        """make_manifest() should create a modules.json file."""
        # Create some .py files
        (tmp_path / "module_a.py").write_text("# module a")
        (tmp_path / "module_b.py").write_text("# module b")

        result = make_manifest(tmp_path, family="micropython", port="esp32", version="1.20.0", stubtype="frozen", board="GENERIC")

        assert result is True
        assert (tmp_path / "modules.json").exists()

    def test_make_manifest_includes_board(self, tmp_path: Path):
        """make_manifest() should include board field in modules.json."""
        (tmp_path / "neopixel.py").write_text("# neopixel")

        make_manifest(tmp_path, family="micropython", port="esp32", version="1.20.0", stubtype="frozen", board="TINYPICO")

        with open(tmp_path / "modules.json") as f:
            data = json.load(f)

        assert data["firmware"]["board"] == "TINYPICO"
        assert "TINYPICO" in data["firmware"]["firmware"]

    def test_make_manifest_lists_py_files(self, tmp_path: Path):
        """make_manifest() should list all .py files in the modules list."""
        (tmp_path / "mod1.py").write_text("# mod1")
        (tmp_path / "mod2.py").write_text("# mod2")
        subdir = tmp_path / "sub"
        subdir.mkdir()
        (subdir / "mod3.py").write_text("# mod3")

        make_manifest(tmp_path, family="micropython", port="rp2", version="1.24.1", stubtype="frozen", board="RPI_PICO")

        with open(tmp_path / "modules.json") as f:
            data = json.load(f)

        module_files = [m["file"] for m in data["modules"]]
        assert "mod1.py" in module_files
        assert "mod2.py" in module_files
        assert "sub/mod3.py" in module_files

    def test_make_manifest_port_in_firmware(self, tmp_path: Path):
        """make_manifest() should include correct port in firmware info."""
        (tmp_path / "test.py").write_text("# test")

        make_manifest(tmp_path, family="micropython", port="stm32", version="1.20.0", stubtype="frozen", board="PYBV11")

        with open(tmp_path / "modules.json") as f:
            data = json.load(f)

        assert data["firmware"]["port"] == "stm32"
        assert data["firmware"]["board"] == "PYBV11"
        assert data["stubber"]["stubtype"] == "frozen"

    def test_make_manifest_without_board(self, tmp_path: Path):
        """make_manifest() without board should not include board field."""
        (tmp_path / "test.py").write_text("# test")

        make_manifest(tmp_path, family="micropython", port="esp32", version="1.20.0", stubtype="frozen")

        with open(tmp_path / "modules.json") as f:
            data = json.load(f)

        assert "board" not in data["firmware"]
