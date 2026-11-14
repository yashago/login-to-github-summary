from __future__ import annotations

import re
from enum import Enum
from typing import Any, Optional, Union

from playwright.sync_api import Locator as PwLocator
from playwright.sync_api import Page, expect
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


class Framework(Enum):
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"


Browser = Union[Page, WebDriver]

# Framework-neutral locator: a Selenium-style (By.<strategy>, value) tuple.
# It is translated to a Playwright selector when running under Playwright.
Locator = tuple[str, str]

# Actions also accept a native Playwright Locator (e.g. page.get_by_role(...)),
# which only works when the page object runs under Playwright.
Target = Union[Locator, PwLocator]


def to_playwright_selector(locator: Locator) -> str:
    """Translate a (By.<strategy>, value) tuple into a Playwright selector string."""
    strategy, value = locator
    if strategy == By.ID:
        return f'[id="{value}"]'
    if strategy in (By.CSS_SELECTOR, By.TAG_NAME):
        return value
    if strategy == By.XPATH:
        return f"xpath={value}"
    if strategy == By.NAME:
        return f'[name="{value}"]'
    if strategy == By.CLASS_NAME:
        return f".{value}"
    if strategy == By.LINK_TEXT:
        return f"xpath=//a[normalize-space()='{value}']"
    if strategy == By.PARTIAL_LINK_TEXT:
        return f"xpath=//a[contains(normalize-space(), '{value}')]"
    raise ValueError(f"Unsupported locator strategy for Playwright: {strategy!r}")


class WebBasePage:
    """Framework-agnostic root of every page object.

    Pass either a Playwright ``Page`` or a Selenium ``WebDriver``; the base detects
    which one it got and initialises the matching handle:
      * Playwright -> ``self.page``
      * Selenium   -> ``self.driver`` and ``self.wait``
    Accessing the handle of the other framework raises a clear error.

    The action methods below (fill, click, check, ...) take a ``Locator`` tuple and
    work under both frameworks, so a single page object can serve both test suites.

    Subclasses may set ``FRAMEWORK`` to restrict which browser type they accept.
    """

    PATH = "/"
    DEFAULT_TIMEOUT = 10  # seconds; Selenium's WebDriverWait and Playwright's waits/expects
    FRAMEWORK: Optional[Framework] = None  # None = accept either framework

    def __init__(self, browser: Browser, timeout: float = DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout
        self._page: Optional[Page] = None
        self._driver: Optional[WebDriver] = None
        self._wait: Optional[WebDriverWait[WebDriver]] = None

        if isinstance(browser, Page):
            self.framework = Framework.PLAYWRIGHT
            self._page = browser
        elif isinstance(browser, WebDriver):  # pyright: ignore[reportUnnecessaryIsInstance] - runtime guard
            self.framework = Framework.SELENIUM
            self._driver = browser
            self._wait = WebDriverWait(browser, timeout)
        else:
            raise TypeError(
                f"{type(self).__name__} expects a Playwright Page or a Selenium WebDriver, "
                f"got {type(browser).__name__}"
            )

        if self.FRAMEWORK is not None and self.framework is not self.FRAMEWORK:
            raise TypeError(
                f"{type(self).__name__} is a {self.FRAMEWORK.value} page object, "
                f"but was given a {self.framework.value} browser"
            )

    # --- Framework detection ---
    @property
    def is_playwright(self) -> bool:
        return self.framework is Framework.PLAYWRIGHT

    @property
    def is_selenium(self) -> bool:
        return self.framework is Framework.SELENIUM

    # --- Framework handles ---
    @property
    def page(self) -> Page:
        if self._page is None:
            raise AttributeError(f"'page' is only available for Playwright; this page uses {self.framework.value}")
        return self._page

    @property
    def driver(self) -> WebDriver:
        if self._driver is None:
            raise AttributeError(f"'driver' is only available for Selenium; this page uses {self.framework.value}")
        return self._driver

    @property
    def wait(self) -> WebDriverWait[WebDriver]:
        if self._wait is None:
            raise AttributeError(f"'wait' is only available for Selenium; this page uses {self.framework.value}")
        return self._wait

    @property
    def _timeout_ms(self) -> float:
        return self.timeout * 1000

    # --- Element resolution ---
    def locator(self, target: Target) -> PwLocator:
        """Playwright only: resolve the target to a Playwright Locator."""
        if isinstance(target, PwLocator):
            return target
        return self.page.locator(to_playwright_selector(target))

    @staticmethod
    def _se(target: Target) -> Locator:
        if isinstance(target, PwLocator):
            raise TypeError("A Playwright Locator cannot be used with Selenium; use a (By, value) tuple")
        return target

    def _js(self, script: str, *args: Any) -> Any:
        return self.driver.execute_script(script, *args)  # pyright: ignore[reportUnknownMemberType]

    def element(self, target: Target) -> WebElement:
        """Selenium only: wait for the target to be present in the DOM and return the WebElement."""
        return self.wait.until(EC.presence_of_element_located(self._se(target)))

    def _se_visible(self, target: Target) -> WebElement:
        element = self.wait.until(EC.visibility_of_element_located(self._se(target)))
        self._js("arguments[0].scrollIntoView({block: 'center'});", element)
        return element

    def _se_clickable(self, target: Target) -> WebElement:
        element = self.wait.until(EC.element_to_be_clickable(self._se(target)))
        self._js("arguments[0].scrollIntoView({block: 'center'});", element)
        return element

    # --- Navigation ---
    def open(self) -> None:
        if self.is_playwright:
            self.page.goto(self.PATH, wait_until="domcontentloaded")
        else:
            self.driver.get(self.PATH)

    @property
    def current_url(self) -> str:
        return self.page.url if self.is_playwright else self.driver.current_url

    def wait_for_url_contains(self, fragment: str) -> None:
        if self.is_playwright:
            self.page.wait_for_url(re.compile(re.escape(fragment)), timeout=self._timeout_ms)
        else:
            self.wait.until(EC.url_contains(fragment))

    # --- Actions ---
    def click(self, target: Target) -> None:
        if self.is_playwright:
            self.locator(target).click()
        else:
            self._se_clickable(target).click()

    def fill(self, target: Target, value: str) -> None:
        """Clear the field and type the value."""
        if self.is_playwright:
            self.locator(target).fill(value)
        else:
            element = self._se_visible(target)
            element.clear()
            element.send_keys(value)

    def fill_date(self, target: Target, iso_date: str) -> None:
        """Set an <input type="date"> value (YYYY-MM-DD).

        Playwright's fill() handles date inputs natively. Selenium's send_keys depends on
        the browser locale (dd/mm vs mm/dd), so set the value via JS and fire the events
        a real user interaction would.
        """
        if self.is_playwright:
            self.locator(target).fill(iso_date)
        else:
            self._js(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
                "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
                self._se_visible(target),
                iso_date,
            )

    def check(self, target: Target) -> None:
        """Check a checkbox / radio; no-op if it is already checked."""
        if self.is_playwright:
            self.locator(target).check()
        else:
            element = self._se_clickable(target)
            if not element.is_selected():
                element.click()

    def select_option(self, target: Target, label: str) -> None:
        """Select a <select> option by its visible text."""
        if self.is_playwright:
            self.locator(target).select_option(label=label)
        else:
            Select(self._se_visible(target)).select_by_visible_text(label)

    def scroll_into_view(self, target: Target) -> None:
        if self.is_playwright:
            self.locator(target).scroll_into_view_if_needed()
        else:
            self._se_visible(target)

    def screenshot_element(self, target: Target, path: str) -> None:
        if self.is_playwright:
            self.locator(target).screenshot(path=path)
        else:
            self._se_visible(target).screenshot(path)  # pyright: ignore[reportUnknownMemberType]

    # --- Queries ---
    def input_value(self, target: Target) -> str:
        if self.is_playwright:
            return self.locator(target).input_value()
        return self.element(target).get_attribute("value") or ""

    def is_checked(self, target: Target) -> bool:
        if self.is_playwright:
            return self.locator(target).is_checked()
        return self.element(target).is_selected()

    def selected_option_text(self, target: Target) -> str:
        if self.is_playwright:
            text: str = self.locator(target).evaluate("el => el.selectedOptions[0]?.text ?? ''")
            return text.strip()
        return Select(self.element(target)).first_selected_option.text.strip()

    def text(self, target: Target) -> str:
        if self.is_playwright:
            return self.locator(target).inner_text().strip()
        return self.element(target).text.strip()

    def get_attribute(self, target: Target, name: str) -> str:
        if self.is_playwright:
            return self.locator(target).get_attribute(name) or ""
        return self.element(target).get_attribute(name) or ""

    # --- Waits ---
    def wait_for_text(self, target: Target, text: str) -> None:
        """Wait until the element's text contains ``text``."""
        if self.is_playwright:
            expect(self.locator(target)).to_contain_text(text, timeout=self._timeout_ms)
        else:
            self.wait.until(EC.text_to_be_present_in_element(self._se(target), text))

    def wait_for_empty_text(self, target: Target) -> None:
        """Wait until the element's text is empty (whitespace only)."""
        if self.is_playwright:
            expect(self.locator(target)).to_have_text(re.compile(r"^\s*$"), timeout=self._timeout_ms)
        else:
            locator = self._se(target)

            def is_empty(driver: WebDriver) -> bool:
                return driver.find_element(*locator).text.strip() == ""

            self.wait.until(is_empty)
