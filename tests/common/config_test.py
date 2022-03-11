from typing import Dict
import stubber


def test_toplevel_config():
    # exists on top-level
    assert stubber.config
    assert isinstance(stubber.config, Dict)
    assert len(stubber.config) >= 4
