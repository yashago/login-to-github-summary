from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utilities import config
import re


class LoginPage(BasePage):
    PATH = config.GITHUB_URL

    def __init__(self, page: Page):
        super().__init__(page)

    
    @property
    def signInButton(self) -> Locator:
        return self.page.get_by_role("link", name="Sign in")

    @property
    def emailField(self) -> Locator:
        return self.page.get_by_role("textbox", name="Username or email address")

    @property
    def passwordField(self) -> Locator:
        return self.page.get_by_role("textbox", name="Password")

    @property
    def signInButtonWithCredentials(self) -> Locator:
        return self.page.get_by_role("button", name="Sign in", exact=True)
    
    def clickOnSignInButton(self):
        self.signInButton.click()
        

    def waitForLoginPagetoLoad(self):
        self.page.wait_for_url("**/login")