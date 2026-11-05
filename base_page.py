from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config.TIMEOUT)

    def open(self, url=None):
        self.driver.get(url or config.BASE_URL)

    def find_first(self, locators, timeout=None, visible=True):
        """Try several locators in order and return the first element found.

        The target site renders client-side, so each field gets a list of fallback
        locators (type -> name -> id -> label text). Edit them in the page class if
        the markup differs.
        """
        timeout = timeout or config.TIMEOUT
        cond = EC.visibility_of_element_located if visible else EC.presence_of_element_located
        per_try = max(1, timeout // max(1, len(locators)))
        for loc in locators:
            try:
                return WebDriverWait(self.driver, per_try).until(cond(loc))
            except TimeoutException:
                continue
        raise NoSuchElementException(f"None of the locators matched: {locators}")

    def exists(self, locators, timeout=2):
        try:
            self.find_first(locators, timeout=timeout)
            return True
        except NoSuchElementException:
            return False

    def screenshot(self, name):
        path = config.SCREENSHOT_DIR / f"{name}.png"
        self.driver.save_screenshot(str(path))
        return path
