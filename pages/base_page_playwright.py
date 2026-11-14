from playwright.sync_api import Page
from pages.web_base_page import Framework, WebBasePage


class PlaywrightBasePage(WebBasePage):
    """Base for Playwright page objects."""

    FRAMEWORK = Framework.PLAYWRIGHT

    def __init__(self, page: Page) -> None:
        super().__init__(page)
