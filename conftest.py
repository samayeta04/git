import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
from pages.login_page import LoginPage  # noqa: E402
from utils.driver_factory import create_driver  # noqa: E402


@pytest.fixture
def driver():
    drv = create_driver()
    yield drv
    drv.quit()


@pytest.fixture
def login_page(driver):
    return LoginPage(driver).load()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Save a screenshot whenever a test fails."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        drv = item.funcargs.get("driver")
        if drv:
            name = re.sub(r"[^\w\-]+", "_", item.name)[:100]
            drv.save_screenshot(str(config.SCREENSHOT_DIR / f"{name}.png"))
