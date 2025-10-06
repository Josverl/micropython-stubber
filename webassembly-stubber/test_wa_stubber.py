import re
import tempfile
from pathlib import Path

import pytest
from playwright.sync_api import BrowserContext, Page, expect


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context with necessary permissions and force headed mode."""
    return {
        **browser_context_args,
        # Force headed mode for this test file
        "headless": False,
        # Grant persistent permissions for file system access
        "permissions": ["clipboard-read", "clipboard-write"],
        # Allow file system access
        "accept_downloads": True,
        # Keep browser open longer for debugging
        "slow_mo": 1000,  # 1 second delay between actions
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Force headed mode at browser launch level."""
    return {
        **browser_type_launch_args,
        "headless": False,
        # Optional: Add other browser launch arguments
        "slow_mo": 500,  # Slow down actions for better visibility
    }


def test_page_content_loads(page: Page):
    """Test that the main page content loads properly."""
    page.goto("http://127.0.0.1:8000/createstubs-pyscript-hosted.html")

    # Check for key elements
    expect(page.get_by_role("heading", level=1)).to_contain_text("Hosted Pyscript stubber")
    expect(page.locator("text=Creating type-stubs for MicroPython")).to_be_visible()
    expect(page.locator("text=synchronize the changes to the local file system")).to_be_visible(timeout=30_000)
    expect(page.locator("text=Synced /stubs")).to_be_visible(timeout=30_000)


if __name__ == "__main__":
    # For running individual tests during development
    import subprocess

    subprocess.run(
        [
            "python",
            "-m",
            "pytest",
            __file__,
            "-v",
            "--tb=short",
            "--headed",  # Force headed mode when run directly
        ]
    )
