import pytest
import os
 
from playwright.sync_api import sync_playwright
 
ABSOLUTE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
 
 
@pytest.fixture(scope="session")
def navigate_to_webpage(resp_time: int = 10000):
    with sync_playwright() as p:
        browser = p.webkit.launch(slow_mo=resp_time)
        yield browser
        browser.close()
 
 
@pytest.fixture(scope="function")
def capture_screenshot(page):
    screenshots_dir = ABSOLUTE_PATH
    os.makedirs(screenshots_dir, exist_ok=True)
 
    def _capture_screenshot(tc_name):
        screenshot_path = os.path.join(screenshots_dir, f"{tc_name}.png")
        page.screenshot(path=screenshot_path)
        return screenshot_path
    yield _capture_screenshot
 