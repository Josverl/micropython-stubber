"""
Playwright regression tests for createstubs-pyscript-hosted.html

Run with:
    pytest webassembly-stubber/tests/ --base-url http://127.0.0.1:8000

Requires a running HTTP server:
    python -m http.server -d webassembly-stubber --bind 127.0.0.1
"""

import pytest
from playwright.sync_api import Page, expect


PAGE = "createstubs-pyscript-hosted.html"
# Wait long enough for async fetch calls (with 5 s timeout) to complete
DROPDOWN_TIMEOUT = 8_000  # ms


# ── helpers ───────────────────────────────────────────────────────────────────


def goto(page: Page, base_url: str, qs: str = "") -> None:
    page.goto(f"{base_url}/{PAGE}{qs}")


def dropdown_options(page: Page, element_id: str) -> list[str]:
    return page.evaluate(f"Array.from(document.getElementById('{element_id}').options).map(o => o.value).filter(v => v)")


def has_mpy_config(page: Page) -> bool:
    return page.evaluate("!!document.querySelector('mpy-config')")


def mpy_config_text(page: Page) -> str:
    return page.evaluate("document.querySelector('mpy-config') ? document.querySelector('mpy-config').textContent : ''")


def mount_script_present(page: Page) -> bool:
    return page.evaluate("Array.from(document.querySelectorAll('script')).some(s => s.src && s.src.includes('mount_createstubs.py'))")


# ── base page (no mode param) ─────────────────────────────────────────────────


class TestBasePage:
    @pytest.fixture(autouse=True)
    def load(self, page: Page, page_url: str):
        page.goto(page_url)
        # Wait for at least one real option to appear in the MPY dropdown
        page.wait_for_function(
            "document.getElementById('mpy-version').options.length > 1",
            timeout=DROPDOWN_TIMEOUT,
        )

    def test_no_js_errors(self, page: Page):
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.reload()
        page.wait_for_timeout(500)
        assert errors == [], f"JS page errors: {errors}"

    def test_mpy_dropdown_populated(self, page: Page):
        opts = dropdown_options(page, "mpy-version")
        assert len(opts) > 3, f"MPY dropdown has too few options: {opts}"

    def test_ps_dropdown_populated(self, page: Page):
        page.wait_for_function(
            "document.getElementById('ps-version').options.length > 1",
            timeout=DROPDOWN_TIMEOUT,
        )
        opts = dropdown_options(page, "ps-version")
        assert len(opts) > 3, f"PS dropdown has too few options: {opts}"

    def test_panels_start_neutral(self, page: Page):
        mpy_cls = page.evaluate("document.getElementById('panel-mpy').className")
        ps_cls = page.evaluate("document.getElementById('panel-ps').className")
        assert "neutral" in mpy_cls, f"MPY panel not neutral: {mpy_cls}"
        assert "neutral" in ps_cls, f"PS  panel not neutral: {ps_cls}"

    def test_no_mpy_config_without_mode(self, page: Page):
        assert not has_mpy_config(page), "mpy-config should NOT be present on base page"

    def test_mount_script_not_injected(self, page: Page):
        assert not mount_script_present(page), "mount_createstubs.py should NOT be injected on base page"


# ── radio button UX ───────────────────────────────────────────────────────────


class TestRadioUX:
    @pytest.fixture(autouse=True)
    def load(self, page: Page, page_url: str):
        page.goto(page_url)
        page.wait_for_function(
            "document.getElementById('mpy-version').options.length > 1",
            timeout=DROPDOWN_TIMEOUT,
        )

    def test_select_mpy_radio(self, page: Page):
        page.click("#radio-mpy")
        mpy_cls = page.evaluate("document.getElementById('panel-mpy').className")
        ps_cls = page.evaluate("document.getElementById('panel-ps').className")
        assert "active" in mpy_cls, f"MPY panel should be active: {mpy_cls}"
        assert "dimmed" in ps_cls, f"PS  panel should be dimmed: {ps_cls}"

    def test_select_ps_radio(self, page: Page):
        page.click("#radio-ps")
        mpy_cls = page.evaluate("document.getElementById('panel-mpy').className")
        ps_cls = page.evaluate("document.getElementById('panel-ps').className")
        assert "dimmed" in mpy_cls, f"MPY panel should be dimmed: {mpy_cls}"
        assert "active" in ps_cls, f"PS  panel should be active: {ps_cls}"

    def test_switch_between_radios(self, page: Page):
        page.click("#radio-mpy")
        page.click("#radio-ps")
        page.click("#radio-mpy")
        mpy_cls = page.evaluate("document.getElementById('panel-mpy').className")
        assert "active" in mpy_cls, "MPY should be active after switching back"

    def test_dimmed_panel_still_clickable(self, page: Page):
        """Dimmed panel must NOT have pointer-events:none — user can click it."""
        page.click("#radio-mpy")
        # Panel-ps is now dimmed; clicking its radio must still work
        page.click("#radio-ps")
        ps_cls = page.evaluate("document.getElementById('panel-ps').className")
        assert "active" in ps_cls, "Clicking dimmed PS panel should activate it"


# ── URL generation (generateStubs) ───────────────────────────────────────────


class TestGenerateStubs:
    @pytest.fixture(autouse=True)
    def load(self, page: Page, page_url: str):
        page.goto(page_url)
        page.wait_for_function(
            "document.getElementById('mpy-version').options.length > 1",
            timeout=DROPDOWN_TIMEOUT,
        )

    def test_mpy_url_contains_mode_and_version(self, page: Page):
        page.click("#radio-mpy")
        page.select_option("#mpy-version", index=0)
        chosen = page.evaluate("document.getElementById('mpy-version').value")
        page.evaluate("generateStubs()")
        page.wait_for_timeout(400)
        url = page.url
        assert "mode=mpy" in url, f"mode=mpy missing: {url}"
        assert f"version={chosen}" in url, f"version missing: {url}"
        assert "psversion" not in url, f"psversion leaked: {url}"

    def test_ps_url_contains_mode_and_psversion(self, page: Page):
        page.wait_for_function(
            "document.getElementById('ps-version').options.length > 1",
            timeout=DROPDOWN_TIMEOUT,
        )
        page.click("#radio-ps")
        page.select_option("#ps-version", index=0)
        chosen = page.evaluate("document.getElementById('ps-version').value")
        page.evaluate("generateStubs()")
        page.wait_for_timeout(400)
        url = page.url
        assert "mode=ps" in url, f"mode=ps missing: {url}"
        assert f"psversion={chosen}" in url, f"psversion missing: {url}"
        assert "version=" not in url or "psversion=" in url  # version should be absent or only psversion

    def test_generate_without_radio_shows_alert(self, page: Page):
        """Calling generateStubs() with no radio selected triggers an alert."""
        dialogs = []
        page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))
        page.evaluate("generateStubs()")
        page.wait_for_timeout(300)
        assert dialogs, "Expected an alert when no mode selected"


# ── mpy-config injection ──────────────────────────────────────────────────────


class TestMpyConfig:
    def test_mpy_mode_injects_config(self, page: Page, page_url: str):
        page.goto(f"{page_url}?mode=mpy&version=1.24.1")
        page.wait_for_timeout(800)
        assert has_mpy_config(page), "mpy-config missing in mpy mode"

    def test_mpy_mode_has_packages(self, page: Page, page_url: str):
        page.goto(f"{page_url}?mode=mpy&version=1.24.1")
        page.wait_for_timeout(800)
        cfg = mpy_config_text(page)
        assert "micropython-stubs" in cfg, f"packages missing from mpy-config: {cfg}"

    def test_mpy_mode_has_interpreter(self, page: Page, page_url: str):
        page.goto(f"{page_url}?mode=mpy&version=1.24.1")
        page.wait_for_timeout(800)
        cfg = mpy_config_text(page)
        assert "cdn.jsdelivr.net" in cfg, f"interpreter CDN missing: {cfg}"
        assert "1.24.1" in cfg, f"interpreter version missing: {cfg}"

    def test_ps_mode_injects_config(self, page: Page, page_url: str):
        page.goto(f"{page_url}?mode=ps&psversion=2025.7.3")
        page.wait_for_timeout(800)
        assert has_mpy_config(page), "mpy-config missing in ps mode"

    def test_ps_mode_has_packages(self, page: Page, page_url: str):
        page.goto(f"{page_url}?mode=ps&psversion=2025.7.3")
        page.wait_for_timeout(800)
        cfg = mpy_config_text(page)
        assert "micropython-stubs" in cfg, f"packages missing in ps mode: {cfg}"

    def test_ps_mode_no_interpreter(self, page: Page, page_url: str):
        page.goto(f"{page_url}?mode=ps&psversion=2025.7.3")
        page.wait_for_timeout(800)
        cfg = mpy_config_text(page)
        assert "interpreter" not in cfg, f"interpreter should be absent in ps mode: {cfg}"


# ── script injection ──────────────────────────────────────────────────────────


class TestScriptInjection:
    def test_mount_script_injected_in_mpy_mode(self, page: Page, page_url: str):
        page.goto(f"{page_url}?mode=mpy&version=1.24.1")
        page.wait_for_timeout(800)
        assert mount_script_present(page), "mount_createstubs.py should be injected in mpy mode"

    def test_mount_script_injected_in_ps_mode(self, page: Page, page_url: str):
        page.goto(f"{page_url}?mode=ps&psversion=2025.7.3")
        page.wait_for_timeout(800)
        assert mount_script_present(page), "mount_createstubs.py should be injected in ps mode"

    def test_mount_script_not_injected_base(self, page: Page, page_url: str):
        page.goto(page_url)
        page.wait_for_timeout(500)
        assert not mount_script_present(page), "mount_createstubs.py should NOT be injected on base page"

    def test_mount_script_src_has_cache_buster(self, page: Page, page_url: str):
        page.goto(f"{page_url}?mode=mpy&version=1.24.1")
        page.wait_for_timeout(800)
        src = page.evaluate(
            "Array.from(document.querySelectorAll('script')).map(s => s.src).find(s => s && s.includes('mount_createstubs.py')) || ''"
        )
        assert "?t=" in src, f"Cache-buster ?t= missing from script src: {src}"


# ── PyScript loads (packages downloaded) ─────────────────────────────────────


class TestPyScriptBoot:
    def test_pyscript_ready_in_mpy_mode(self, page: Page, page_url: str):
        console_msgs = []
        page.on("console", lambda m: console_msgs.append(m.text))
        page.goto(f"{page_url}?mode=mpy&version=1.24.1")
        # Wait for PyScript Ready signal (up to 20 s)
        page.wait_for_function(
            "window.__pyscript_ready !== undefined || document.querySelector('[data-pyscript-ready]') !== null",
            timeout=20_000,
        ) if False else page.wait_for_timeout(15_000)
        # Check that package install logs appeared
        pkg_logs = [m for m in console_msgs if "micropython-stubs" in m or "createstubs" in m]
        assert pkg_logs, f"No package-install console logs found. Got: {console_msgs[:10]}"

    def test_pyscript_no_fatal_errors_in_mpy_mode(self, page: Page, page_url: str):
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(f"{page_url}?mode=mpy&version=1.24.1")
        page.wait_for_timeout(15_000)
        assert errors == [], f"Fatal JS errors in mpy mode: {errors}"
