from selenium.webdriver.common.by import By

from pages.web_base_page import Browser, Locator, WebBasePage
from utilities.consts import FILE_PATH


class RegistrationFormPage(WebBasePage):
    """Registration form page object; works with a Playwright Page or a Selenium WebDriver."""

    PATH = FILE_PATH

    # Personal details
    FIRST_NAME: Locator = (By.ID, "firstName")
    LAST_NAME: Locator = (By.ID, "lastName")
    EMAIL: Locator = (By.ID, "email")
    CONFIRM_EMAIL: Locator = (By.ID, "confirmEmail")
    PASSWORD: Locator = (By.ID, "password")
    PHONE: Locator = (By.ID, "phone")
    DATE_OF_BIRTH: Locator = (By.ID, "birthday")
    COUNTRY: Locator = (By.ID, "country")
    CITY: Locator = (By.ID, "city")

    # Actions / status
    RESET_BUTTON: Locator = (By.XPATH, "//button[@type='reset']")
    SUBMIT_BUTTON: Locator = (By.XPATH, "//button[@type='submit']")
    STATUS: Locator = (By.ID, "status")

    # Header links
    PREFERENCES_LINK: Locator = (By.LINK_TEXT, "Preferences")
    GOOGLE_MAP_LINK: Locator = (By.LINK_TEXT, "Google Map")
    GOOGLE_MAP_IFRAME: Locator = (By.CSS_SELECTOR, 'iframe[title="Google Map showing Tel Aviv, Israel"]')

    def __init__(self, browser: Browser) -> None:
        super().__init__(browser)

    # --- Dynamic locators (radio / checkbox are wrapped by their label) ---
    @staticmethod
    def gender_radio(gender: str) -> Locator:
        return (By.XPATH, f"//label[normalize-space()='{gender}']/input[@type='radio' and @name='gender']")

    @staticmethod
    def interest_checkbox(interest: str) -> Locator:
        return (By.XPATH, f"//label[normalize-space()='{interest}']/input[@type='checkbox' and @name='topics']")

    # --- Personal details ---
    def fill_personal_details(self, first: str, last: str, email: str) -> None:
        self.fill(self.FIRST_NAME, first)
        self.fill(self.LAST_NAME, last)
        self.fill(self.EMAIL, email)
        self.fill(self.CONFIRM_EMAIL, email)

    def emailsAreIdentical(self) -> bool:
        return self.input_value(self.EMAIL) == self.input_value(self.CONFIRM_EMAIL)

    def fill_password(self, password: str) -> None:
        self.fill(self.PASSWORD, password)

    def fill_phone_number(self, phone: str) -> None:
        self.fill(self.PHONE, phone)

    def fill_city(self, city: str) -> None:
        self.fill(self.CITY, city)

    def fill_date_of_birth(self, iso_date: str) -> None:
        self.fill_date(self.DATE_OF_BIRTH, iso_date)

    def date_of_birth_value(self) -> str:
        return self.input_value(self.DATE_OF_BIRTH)

    def first_name_value(self) -> str:
        return self.input_value(self.FIRST_NAME)

    def select_country(self, country: str) -> None:
        self.select_option(self.COUNTRY, country)

    def selected_country(self) -> str:
        return self.selected_option_text(self.COUNTRY)

    def select_gender(self, gender: str) -> None:
        self.check(self.gender_radio(gender))

    def is_gender_selected(self, gender: str) -> bool:
        return self.is_checked(self.gender_radio(gender))

    def select_interest(self, interest: str) -> None:
        self.check(self.interest_checkbox(interest))

    def is_interest_selected(self, interest: str) -> bool:
        return self.is_checked(self.interest_checkbox(interest))

    # --- Reset ---
    def screenshot_reset_button(self, path: str) -> None:
        self.screenshot_element(self.RESET_BUTTON, path)

    def reset_form(self, confirmation_text: str) -> None:
        """Click Reset and wait for the status message to appear and then disappear (~3s)."""
        self.click(self.RESET_BUTTON)
        self.wait_for_text(self.STATUS, confirmation_text)
        self.wait_for_empty_text(self.STATUS)

    # --- Header ---
    def click_preferences_link(self) -> None:
        self.click(self.PREFERENCES_LINK)
        self.wait_for_url_contains("#preferences")

    def click_google_map_link(self) -> None:
        self.click(self.GOOGLE_MAP_LINK)

    def map_iframe_src(self) -> str:
        return self.get_attribute(self.GOOGLE_MAP_IFRAME, "src")
