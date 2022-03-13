from typing import Dict
from pathlib import Path
import stubber
from stubber.utils.config import StubberConfig


def test_toplevel_config():
    # exists on top-level
    assert stubber.config
    assert isinstance(stubber.config, StubberConfig )
    
    print(stubber.config)
    assert isinstance(stubber.config.stub_path, Path )
    assert isinstance(stubber.config.repo_path, Path )
    # assert isinstance(stubber.config.fallback_path, Path )
    # assert isinstance(stubber.config.mpy_path, Path )
    # assert isinstance(stubber.config.mpy_lib_path, Path )

