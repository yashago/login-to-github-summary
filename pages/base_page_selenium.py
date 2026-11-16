from selenium.webdriver.remote.webdriver import WebDriver
from pages.web_base_page import Framework, Locator, WebBasePage

__all__ = ["Locator", "SeleniumBasePage"]


class SeleniumBasePage(WebBasePage):
    """Base for Selenium-only page objects."""

    FRAMEWORK = Framework.SELENIUM

    def __init__(self, driver: WebDriver, timeout: float = WebBasePage.DEFAULT_TIMEOUT) -> None:
        super().__init__(driver, timeout)
