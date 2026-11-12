from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

Locator = tuple[str, str]


class SeleniumBasePage:
    PATH = "/"
    DEFAULT_TIMEOUT = 10

    def __init__(self, driver: WebDriver, timeout: float = DEFAULT_TIMEOUT) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self) -> None:
        self.driver.get(self.PATH)

    def find(self, locator: Locator) -> WebElement:
        """Wait for the element to be present in the DOM and return it."""
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_visible(self, locator: Locator) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_clickable(self, locator: Locator) -> WebElement:
        return self.wait.until(EC.element_to_be_clickable(locator))

    def scroll_into_view(self, element: WebElement) -> WebElement:
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        return element

    def fill(self, locator: Locator, value: str) -> None:
        """Selenium equivalent of Playwright's fill(): clear, then type."""
        element = self.find_visible(locator)
        element.clear()
        element.send_keys(value)

    def input_value(self, locator: Locator) -> str:
        return self.find(locator).get_attribute("value") or ""

    def check(self, locator: Locator) -> None:
        """Selenium equivalent of Playwright's check(): click only if not already selected."""
        element = self.scroll_into_view(self.find_clickable(locator))
        if not element.is_selected():
            element.click()
