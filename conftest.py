from selenium import webdriver  # type: ignore[reportUnknownVariableType]
import pytest

@pytest.fixture
def driver():
    # options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    # driver = webdriver.Chrome(options)
    driver = webdriver.Chrome()
    yield driver
    driver.quit()  # runs even if the test fails