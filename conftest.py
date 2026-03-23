import os
import allure

from datetime import datetime

import pytest
from playwright.sync_api import sync_playwright


def pytest_addoption(parser):
    parser.addoption(
        "--browser-matrix",
        action="store",
        default="chromium",
        help="Comma-separated browsers, e.g. chromium,firefox,webkit,chrome,msedge",
    )


def pytest_generate_tests(metafunc):
    if "run_browser" in metafunc.fixturenames:
        browser_matrix = metafunc.config.getoption("browser_matrix")
        browsers = [b.strip() for b in browser_matrix.split(",") if b.strip()]
        metafunc.parametrize("run_browser", browsers, indirect=True)


def pytest_configure(config):
    run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    report_dir = os.path.join("reports", run_id)
    screenshots_dir = os.path.join(report_dir, "screenshots")
    logs_dir = os.path.join(report_dir, "logs")

    os.makedirs(report_dir, exist_ok=True)
    os.makedirs(screenshots_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    config._report_dir = report_dir
    config._screenshots_dir = screenshots_dir
    config._logs_dir = logs_dir

    os.environ["REPORT_DIR"] = report_dir
    os.environ["SCREENSHOTS_DIR"] = screenshots_dir
    os.environ["LOGS_DIR"] = logs_dir


@pytest.fixture
def run_browser(request):
    return request.param


@pytest.fixture
def page(run_browser):
    playwright = sync_playwright().start()
    headless = os.getenv("CI", "false").lower() == "true"

    if run_browser == "chromium":
        browser = playwright.chromium.launch(headless=headless)
    elif run_browser == "firefox":
        browser = playwright.firefox.launch(headless=headless)
    elif run_browser == "webkit":
        browser = playwright.webkit.launch(headless=headless)
    elif run_browser == "chrome":
        browser = playwright.chromium.launch(channel="chrome", headless=headless)
    elif run_browser == "msedge":
        browser = playwright.chromium.launch(channel="msedge", headless=headless)
    else:
        playwright.stop()
        raise ValueError(f"Unsupported browser: {run_browser}")

    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    page.set_default_timeout(10000)

    yield page

    context.close()
    browser.close()
    playwright.stop()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    if report.failed:
        page_obj = item.funcargs.get("page")
        run_browser = item.funcargs.get("run_browser", "unknown")

        if page_obj:
            screenshots_dir = getattr(
                item.config,
                "_screenshots_dir",
                os.environ.get("SCREENSHOTS_DIR", "screenshots"),
            )

            os.makedirs(screenshots_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            screenshot_path = os.path.join(
                screenshots_dir,
                f"{item.name}_{run_browser}_{timestamp}.png",
            )

            page_obj.screenshot(path=screenshot_path, full_page=True)
            allure.attach.file(
                screenshot_path,
                name=f"{item.name}_{run_browser}_failure_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
            print(f"Screenshot saved: {screenshot_path}")
