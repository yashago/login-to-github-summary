import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



@pytest.mark.selenium
def test_pw_css(driver):
    driver.set_window_size(800, 800)          # below Docusaurus's 997px breakpoint
    driver.get("https://www.playwright.dev")

    button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Toggle navigation bar"]')
    button.click()
    
    # Relativa path by Class
    cliLink = driver.find_element(By.XPATH, '//*[contains(@class, "theme-layout-navbar")]/div[3]/div[2]/div[1]/ul/li[3]/a')
    # Relative path by id
    # cliLink = driver.find_element(By.XPATH, '//*[@id="__docusaurus"]/nav/div[3]/div[2]/div[1]/ul/li[3]/a')
    # Full path
    # cliLink = driver.find_element(By.XPATH, '/html/body/div[1]/nav/div[3]/div[2]/div[1]/ul/li[3]/a')
    cliLink.click()
    WebDriverWait(driver, 10).until(EC.url_to_be("https://playwright.dev/agent-cli/introduction"))
    assert driver.current_url == "https://playwright.dev/agent-cli/introduction"

@pytest.mark.selenium
def test_google_title(driver):
    driver.get("https://www.google.com")
    print(f"Driver: {driver}")
    assert driver.title == "Google"

@pytest.mark.selenium
def test_google_search(driver):
    driver.get("https://www.google.com")
    # searchField = driver.find_element(By.NAME, "q")
    searchField = driver.find_element(By.CSS_SELECTOR, '[aria-label="חיפוש"]')
    searchField.send_keys("SOXL stock price")
    searchField.clear()
    print(f"Attribute: {searchField.get_attribute("aria-label")}")
    # searchField.submit()
    searchField.send_keys(Keys.ENTER)
