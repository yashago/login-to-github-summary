from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from pages.selenium_base_page import Locator, SeleniumBasePage
from utilities.consts import FILE_PATH


class RegistrationFormSeleniumPage(SeleniumBasePage):
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

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

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
        """Set an <input type="date"> value (YYYY-MM-DD).

        send_keys on a date input depends on the browser's locale (dd/mm vs mm/dd),
        so set the value via JS and fire the events a real user interaction would.
        """
        element = self.scroll_into_view(self.find_visible(self.DATE_OF_BIRTH))
        self.driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
            element,
            iso_date,
        )

    def date_of_birth_value(self) -> str:
        return self.input_value(self.DATE_OF_BIRTH)

    def first_name_value(self) -> str:
        return self.input_value(self.FIRST_NAME)

    def select_country(self, country: str) -> None:
        element = self.scroll_into_view(self.find_visible(self.COUNTRY))
        Select(element).select_by_visible_text(country)

    def selected_country(self) -> str:
        return Select(self.find(self.COUNTRY)).first_selected_option.text

    def select_gender(self, gender: str) -> None:
        self.check(self.gender_radio(gender))

    def is_gender_selected(self, gender: str) -> bool:
        return self.find(self.gender_radio(gender)).is_selected()

    def select_interest(self, interest: str) -> None:
        self.check(self.interest_checkbox(interest))

    def is_interest_selected(self, interest: str) -> bool:
        return self.find(self.interest_checkbox(interest)).is_selected()

    # --- Reset ---
    @property
    def reset_button(self) -> WebElement:
        return self.scroll_into_view(self.find_clickable(self.RESET_BUTTON))

    def reset_form(self, confirmation_text: str) -> None:
        """Click Reset and wait for the status message to appear and then disappear (~3s)."""
        self.reset_button.click()
        self.wait.until(EC.text_to_be_present_in_element(self.STATUS, confirmation_text))
        self.wait.until(lambda d: d.find_element(*self.STATUS).text.strip() == "")

    # --- Header ---
    def click_preferences_link(self) -> None:
        self.find_clickable(self.PREFERENCES_LINK).click()
        self.wait.until(EC.url_contains("#preferences"))

    def click_google_map_link(self) -> None:
        self.find_clickable(self.GOOGLE_MAP_LINK).click()

    @property
    def map_iframe(self) -> WebElement:
        return self.find(self.GOOGLE_MAP_IFRAME)
