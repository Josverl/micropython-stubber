"""
Shared fixtures for webassembly-stubber playwright tests.

Run with:
    pytest webassembly-stubber/tests/ --base-url http://127.0.0.1:8000

Requires a running HTTP server:
    python -m http.server -d webassembly-stubber --bind 127.0.0.1
"""

import pytest


@pytest.fixture(scope="session")
def page_url(base_url):
    return f"{base_url}/createstubs-pyscript-hosted.html"
