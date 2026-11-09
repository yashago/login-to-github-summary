from playwright.sync_api import Page


class BasePage:
    PATH = "/"

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self) -> None:
        self.page.goto(self.PATH, wait_until="domcontentloaded")
