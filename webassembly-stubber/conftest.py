import tempfile
from pathlib import Path

import pytest
from playwright.sync_api import Browser, BrowserContext, Page


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context with necessary permissions."""
    return {
        **browser_context_args,
        # Enable file system access
        "permissions": ["clipboard-read", "clipboard-write"],
        "accept_downloads": True,
        # Disable web security for local file access
        "ignore_https_errors": True,
        # Set a custom user data directory to persist permissions
        "viewport": {"width": 1280, "height": 720},
    }


@pytest.fixture 
def context(browser: Browser):
    """Create browser context with filesystem permissions."""
    context = browser.new_context(
        permissions=["clipboard-read", "clipboard-write"],
        accept_downloads=True,
        ignore_https_errors=True,
    )
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext):
    """Create a page with the configured context."""
    page = context.new_page()
    
    # Add console message logging for debugging
    page.on("console", lambda msg: print(f"Console {msg.type}: {msg.text}"))
    
    yield page
    page.close()


# Add a custom marker for slow tests
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow running")