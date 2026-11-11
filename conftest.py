import os

from selenium import webdriver  # type: ignore[reportUnknownVariableType]
from selenium.webdriver.chrome.options import Options  # type: ignore[reportUnknownVariableType]
import pytest

@pytest.fixture
def driver():
    options = Options()
    if os.getenv("CI"):
        # CI runners have no display, so Chrome must run headless there.
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()  # runs even if the test fails