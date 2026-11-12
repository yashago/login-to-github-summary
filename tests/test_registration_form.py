from datetime import datetime
import re

from playwright.sync_api import Page, expect
from utilities.consts import FILE_PATH, REGISTRATION_FORM
from pages.registration_form_page import RegistrationFormPage


def test_registration_form(page: Page, request):
    # Navigate to the local registration form
    page.pause()
    registration = RegistrationFormPage(page)
    registration.open()
    # page.goto(FILE_PATH)
    page.pause()
    fillInFullForm(page, registration)
    test_name = request.node.name
    date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    page.screenshot(path=f"screenshots/{test_name}_{date}.png")
    page.screenshot(path=f"screenshots/{test_name}_{date}_full.png", full_page=True)
    validateResetForm(page)
    fillInFullForm(page, registration)
    #validateSubmitForm(page)

def test_header(page: Page):
    page.goto(FILE_PATH)
    # testRegistrationLink(page)
    verifyPreferencesLink(page)
    validateGoogleMapsIframe(page)
    # validateHelpLink(page)
    # confirmNativeDialog(page)
    # verifyPlaywrightDocsLink(page)

def verifyPreferencesLink(page):
    preferencesLink = page.get_by_role("link", name="Preferences")
    page.pause()
    preferencesLink.click()
    page.wait_for_url("**#preferences")

def fillInFullForm(page, registrationPage):
    registrationPage.fill_personal_details("first", "last", "email@test.com")

    assert registrationPage.emailsAreIdentical()

    #TODO: Fill in the password
    fillInPassword(page, "yourpassword")

    #TODO: Fill in the phone number
    fillInPhoneNumber(page, "+972-54-4746095")

    #TODO: Fill in the date of birth
    fillInDateOfBirth(page, "1984-03-03")

    #TODO: Select the country
    selectCountry(page, "United Kingdom")

    #TODO: Fill in the city
    # fillInCity(page, "Beer-Sheva")

    #TODO: Select the gender
    selectGender(page, REGISTRATION_FORM.get("formGender"))

    #TODO: Select your interest
    selectInterest(page, REGISTRATION_FORM.get("formInterest"))

def validateResetForm(page):
    resetButton = page.get_by_role("button", name="Reset")
    resetButton.scroll_into_view_if_needed()

    resetButton.screenshot(path="screenshots/reset_button.png")

    resetButton.highlight()
    print("Clicking on the reset button")
    resetButton.click()
    page.get_by_text(REGISTRATION_FORM.get("resetConfirmationText")).wait_for(state="visible")
    page.get_by_text(REGISTRATION_FORM.get("resetConfirmationText")).wait_for(state="hidden")
    

    # Validate that the form fields are reset
    firstNameField = page.get_by_role("textbox", name="First name")
    expect(firstNameField).to_be_empty()

    dateOfBirthField = page.get_by_label("Date of birth")
    expect(dateOfBirthField).to_be_empty()

    genderRadioButtons = page.get_by_role("radio", name=REGISTRATION_FORM.get("formGender"))
    expect(genderRadioButtons).not_to_be_checked()

def printAccessibilityTree(page):
    pageAccesibility = page.locator("body").aria_snapshot()
    print(f"pageAccesibility: {pageAccesibility}")

# def fillInFirstName(page, firstName):
#     #By role, preferred method
#     print(f"Filling in first name: {firstName}")
#     page.get_by_role("textbox", name="First name").fill(firstName)

# def fillInLastName(page, lastName):
#     #By role, preferred method
#     print(f"Filling in last name: {lastName}")
#     page.get_by_role("textbox", name="Last name").fill(lastName)

# def fillInEmail(page, email):
#     #By role, preferred method
#     print(f"Filling in email: {email}")
#     page.get_by_role("textbox", name=re.compile("^"+REGISTRATION_FORM.get("formEmail")), exact=True).fill(email)

def fillInEmailConfirmation(page, emailConfirmation):
    #By role, preferred method
    print(f"Filling in email confirmation: {emailConfirmation}")
    page.get_by_role("textbox", name="Confirm email").fill(emailConfirmation)

def fillInPassword(page, password):
    #By role, preferred method
    print(f"Filling in password: {password}")
    page.get_by_role("textbox", name="Password").fill(password)

def fillInPhoneNumber(page, phoneNumber):
    #By role, preferred method
    print(f"Filling in phone number: {phoneNumber}")
    page.get_by_role("textbox", name="Phone number").fill(phoneNumber)

def fillInDateOfBirth(page, dateOfBirth):
    #By label, preferred method
    datePicker = page.get_by_label("Date of birth")
    datePicker.fill(dateOfBirth)
    datePicker.scroll_into_view_if_needed()
    datePicker.highlight()

def selectCountry(page, country):
    #By role, preferred method
    countryDropdown = page.get_by_role("combobox", name="Country")
    countryDropdown.scroll_into_view_if_needed()
    countryDropdown.highlight()
    print(f"Selecting country: {country}")
    countryDropdown.select_option(country)  

def validateRegistrationLink(page):
    registrationLink = page.get_by_role("link", name="Registration")
    registrationLink.scroll_into_view_if_needed()
    registrationLink.highlight()
    registrationLink.click()
    # printAccessibilityTree(page)

def validateGoogleMapsIframe(page):
    page.pause()
    page.get_by_role("link", name="Google Map").click()
    mapIframe = page.locator("iframe[title=\"Google Map showing Tel Aviv, Israel\"]")
    expect(mapIframe).to_have_attribute("src", re.compile(r"\?q=Tel\+Aviv,\+Israel"))
    # The iframe has loading="lazy", so it only loads once scrolled into view
    mapIframe.scroll_into_view_if_needed()
    navButton = mapIframe.content_frame.get_by_role("link", name="Open in Maps (opens in new")
    expect(navButton).to_be_visible()
    expect(navButton).to_be_enabled()
    expect(navButton).to_have_attribute("href", re.compile(r"^https://maps\.google\.com/"))

    with page.expect_popup() as newWindowsContext:
        navButton.click()

    newPage = newWindowsContext.value
    expect(newPage).to_have_url(re.compile("https://www.google.com/maps.*"))

def validateHelpLink(page):
    helpLink = page.get_by_role("link", name="Help")
    helpLink.scroll_into_view_if_needed()
    page.pause()
    helpLink.highlight()
    helpLink.click()

    printAccessibilityTree(page)
    dialog = page.get_by_role("dialog", name=REGISTRATION_FORM["modalHeaderText"])
    expect(dialog).to_be_visible()
    expect(dialog.get_by_role("heading", level=2, name=REGISTRATION_FORM.get("modalHeaderText"))).to_be_visible()

    dialogOkButton = dialog.get_by_role("button", name=REGISTRATION_FORM.get("modalButtonText"))
    expect(dialogOkButton).to_be_visible()
    expect(dialogOkButton).to_be_enabled()
    dialogOkButton.click()

def selectGender(page, gender):
    #By label, preferred method
    genderRadioButtons = page.get_by_role("radio", name=gender)
    genderRadioButtons.scroll_into_view_if_needed()
    print(f"Checking gender: {gender}")
    genderRadioButtons.check()

def selectInterest(page, interest):
    interestCheckbox = page.get_by_role("checkbox", name=interest)
    interestCheckbox.scroll_into_view_if_needed()
    print(f"Checking interest: {interest}")
    interestCheckbox.check()

def confirmNativeDialog(page):
    page.pause()

    # Accept the alert dialog
    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("link", name="Native confirm dialog").click()

    # Dismiss the alert dialog
    page.once("dialog", lambda dialog: dialog.dismiss())
    page.get_by_role("link", name="Native confirm dialog").click()

    # Replace the alert dialog with a custom message
    page.once("dialog", lambda dialog: readDialogMessageAndDismiss(dialog))
    page.get_by_role("link", name="Native confirm dialog").click()

def readDialogMessageAndDismiss(dialog):
    print(f"Custom message: {dialog.message}")
    print(f"Dialog type: {dialog.type}")
    print('Dismissing the dialog')
    dialog.dismiss()

def verifyPlaywrightDocsLink(page):
    page.pause()
    with page.expect_popup() as newWindowsContext:
        page.get_by_role("link", name="Playwright documentation").click()

    newPage = newWindowsContext.value
    expect(newPage).to_have_url(re.compile("https://playwright.dev/.*"))
    expect(newPage.get_by_role("heading", name="Playwright", level=1)).to_be_visible()