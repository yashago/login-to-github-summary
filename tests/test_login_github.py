from pages.login_github import LoginPage
from playwright.sync_api import Page, expect
from utilities.config import TEST_EMAIL, TEST_PASSWORD

def test_sign_in_to_gmail(page: Page):
    signInPage = LoginPage(page)
    signInPage.open()
    
    signInPage.clickOnSignInButton()
    signInPage.waitForLoginPagetoLoad()
    
    assert TEST_EMAIL is not None
    assert TEST_PASSWORD is not None

    signInPage.emailField.fill(TEST_EMAIL)
    signInPage.passwordField.fill(TEST_PASSWORD)

    expect(signInPage.signInButtonWithCredentials).to_be_visible()