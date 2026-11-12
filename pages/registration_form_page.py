from playwright.sync_api import Page
from pages.base_page import BasePage
from utilities.consts import FILE_PATH, REGISTRATION_FORM
import re

class RegistrationFormPage(BasePage):
    PATH = FILE_PATH

    def __init__(self, page: Page):
        super().__init__(page)
        self.last_name = page.get_by_role("textbox", name="Last name")
        self.email = page.get_by_role("textbox", name=re.compile("^"+REGISTRATION_FORM.get("formEmail")))
        self.confirmEmail = page.get_by_role("textbox", name="Confirm email")

    def fill_personal_details(self, first, last, email):
        self.first_name.fill(first)
        self.last_name.fill(last)
        self.email.fill(email)
        self.confirmEmail.fill(email)

    def emailsAreIdentical(self):
        return self.email.input_value() == self.confirmEmail.input_value()
    
    @property
    def first_name(self):
        return self.page.get_by_role("textbox", name="First name")