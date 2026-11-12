import os
import re
from datetime import datetime

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.registration_form_selenium_page import RegistrationFormSeleniumPage
from utilities.consts import REGISTRATION_FORM

SCREENSHOTS_DIR = "screenshots"


@pytest.mark.selenium
def test_registration_form_selenium(driver, request):
    registration = RegistrationFormSeleniumPage(driver)
    registration.open()

    fillInFullForm(registration)

    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    test_name = request.node.name
    date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Selenium's Chrome driver only captures the viewport (no full_page option like Playwright).
    driver.save_screenshot(f"{SCREENSHOTS_DIR}/{test_name}_{date}.png")

    validateResetForm(registration)
    fillInFullForm(registration)


@pytest.mark.selenium
def test_header_selenium(driver):
    registration = RegistrationFormSeleniumPage(driver)
    registration.open()

    registration.click_preferences_link()
    # validateGoogleMapsIframe(registration)


def fillInFullForm(registration: RegistrationFormSeleniumPage):
    registration.fill_personal_details("first", "last", "email@test.com")
    assert registration.emailsAreIdentical()

    registration.fill_password("yourpassword")
    registration.fill_phone_number("+972-54-4746095")

    registration.fill_date_of_birth("1984-03-03")
    assert registration.date_of_birth_value() == "1984-03-03"

    registration.select_country("United Kingdom")
    assert registration.selected_country() == "United Kingdom"

    registration.select_gender(REGISTRATION_FORM["formGender"])
    assert registration.is_gender_selected(REGISTRATION_FORM["formGender"])

    registration.select_interest(REGISTRATION_FORM["formInterest"])
    assert registration.is_interest_selected(REGISTRATION_FORM["formInterest"])


def validateResetForm(registration: RegistrationFormSeleniumPage):
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    registration.reset_button.screenshot(f"{SCREENSHOTS_DIR}/reset_button_selenium.png")

    print("Clicking on the reset button")
    registration.reset_form(REGISTRATION_FORM["resetConfirmationText"])

    # Validate that the form fields are reset
    assert registration.first_name_value() == ""
    assert registration.date_of_birth_value() == ""
    assert not registration.is_gender_selected(REGISTRATION_FORM["formGender"])


def validateGoogleMapsIframe(registration: RegistrationFormSeleniumPage):
    driver = registration.driver
    registration.click_google_map_link()

    mapIframe = registration.scroll_into_view(registration.map_iframe)
    assert re.search(r"\?q=Tel\+Aviv,\+Israel", mapIframe.get_attribute("src") or "")

    # Selenium must explicitly switch context into the iframe
    registration.wait.until(EC.frame_to_be_available_and_switch_to_it(mapIframe))
    try:
        # The link lives inside the shadow DOM of <embed-place-card-element>. Unlike Playwright,
        # Selenium locators don't pierce shadow roots, and shadow roots only accept CSS selectors.
        placeCard = registration.find((By.CSS_SELECTOR, "embed-place-card-element"))
        navButton = registration.wait.until(
            lambda d: placeCard.shadow_root.find_element(By.CSS_SELECTOR, "a[aria-label^='Open in Maps']")
        )
        assert navButton.is_displayed()
        assert navButton.is_enabled()
        assert re.match(r"^https://maps\.google\.com/", navButton.get_attribute("href") or "")

        original_window = driver.current_window_handle
        existing_windows = set(driver.window_handles)
        navButton.click()
    finally:
        driver.switch_to.default_content()

    # Equivalent of Playwright's expect_popup(): wait for a new window handle and switch to it
    registration.wait.until(lambda d: len(set(d.window_handles) - existing_windows) == 1)
    new_window = (set(driver.window_handles) - existing_windows).pop()
    driver.switch_to.window(new_window)
    registration.wait.until(EC.url_matches(r"https://www\.google\.com/maps.*"))

    driver.close()
    driver.switch_to.window(original_window)
