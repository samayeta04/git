import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import config
from pages.base_page import BasePage


class LoginPage(BasePage):
    # ---- Locators (fallback lists; first match wins) -----------------------------
    EMAIL = [
        (By.CSS_SELECTOR, "input[type='email']"),
        (By.CSS_SELECTOR, "input[name='email']"),
        (By.CSS_SELECTOR, "input[id*='email' i]"),
        (By.CSS_SELECTOR, "input[placeholder*='email' i]"),
        (By.XPATH, "//label[contains(normalize-space(.),'Email')]/following::input[1]"),
    ]
    PASSWORD = [
        (By.CSS_SELECTOR, "input[type='password']"),
        (By.CSS_SELECTOR, "input[name='password']"),
        (By.CSS_SELECTOR, "input[id*='password' i]"),
        (By.XPATH, "//label[contains(normalize-space(.),'Password')]/following::input[1]"),
    ]
    SIGN_IN_BTN = [
        (By.XPATH, "//button[normalize-space()='Sign in']"),
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.XPATH, "//button[contains(translate(.,'SIGN IN','sign in'),'sign in')]"),
    ]
    HEADING = [
        (By.XPATH, "//h1[contains(.,'Welcome to LaunchX')]"),
        (By.XPATH, "//*[self::h1 or self::h2][contains(.,'LaunchX')]"),
    ]
    SUBTITLE = [(By.XPATH, "//*[contains(.,'Sign in to continue your placement journey')]")]
    INVITE_NOTE = [(By.XPATH, "//*[contains(.,'private invite link')]")]
    LOGO = [(By.CSS_SELECTOR, "img[src*='brand-logo'], img[alt*='InquoCV' i]")]
    LANGUAGE = [
        (By.CSS_SELECTOR, "select"),
        (By.XPATH, "//*[@role='combobox' or @aria-haspopup='listbox']"),
        (By.XPATH, "//*[contains(normalize-space(.),'Language')]/following::*[self::select or self::button][1]"),
    ]
    SHOW_PASSWORD = [
        (By.CSS_SELECTOR, "button[aria-label*='show' i], button[aria-label*='password' i], [data-testid*='toggle']"),
    ]
    ERROR = [
        (By.CSS_SELECTOR, "[role='alert']"),
        (By.CSS_SELECTOR, "[class*='error' i], [class*='toast' i], [class*='invalid' i]"),
        (By.XPATH, "//*[contains(translate(.,'INVALID','invalid'),'invalid') or "
                   "contains(translate(.,'INCORRECT','incorrect'),'incorrect') or "
                   "contains(translate(.,'FAILED','failed'),'failed') or "
                   "contains(translate(.,'REQUIRED','required'),'required')]"
                   "[not(self::script) and not(self::style) and not(*)]"),
    ]
    LOGOUT = [
        (By.XPATH, "//*[self::button or self::a][contains(translate(.,'LOGOUT','logout'),'logout') "
                   "or contains(translate(.,'SIGN OUT','sign out'),'sign out')]"),
        (By.CSS_SELECTOR, "[data-testid*='logout' i], [aria-label*='logout' i]"),
    ]

    # ---- Actions -------------------------------------------------------------------
    def load(self):
        self.open()
        self.find_first(self.EMAIL)
        return self

    def email_field(self):
        return self.find_first(self.EMAIL)

    def password_field(self):
        return self.find_first(self.PASSWORD)

    def sign_in_button(self):
        return self.find_first(self.SIGN_IN_BTN)

    def type_email(self, value):
        el = self.email_field()
        el.clear()
        if value:
            el.send_keys(value)

    def type_password(self, value):
        el = self.password_field()
        el.clear()
        if value:
            el.send_keys(value)

    def click_sign_in(self):
        self.sign_in_button().click()

    def login(self, email, password, via_enter=False):
        self.type_email(email)
        self.type_password(password)
        if via_enter:
            self.password_field().send_keys(Keys.ENTER)
        else:
            self.click_sign_in()

    # ---- State checks ----------------------------------------------------------------
    def is_login_form_visible(self, timeout=2):
        return self.exists(self.PASSWORD, timeout=timeout)

    def wait_for_login_success(self, timeout=None):
        """Success = the sign-in form is gone (SPA navigated to the app)."""
        timeout = timeout or config.TIMEOUT
        end = time.time() + timeout
        while time.time() < end:
            if not self.driver.find_elements(*self.PASSWORD[0]):
                return True
            time.sleep(0.3)
        return False

    def login_was_rejected(self, timeout=None):
        """Rejected = still on the form after the wait (an error message is a bonus)."""
        timeout = timeout or config.NEG_TIMEOUT
        time.sleep(timeout)
        return bool(self.driver.find_elements(*self.PASSWORD[0]))

    def error_text(self):
        try:
            return self.find_first(self.ERROR, timeout=3).text.strip()
        except Exception:
            return ""

    def html5_validation_message(self, which="email"):
        el = self.email_field() if which == "email" else self.password_field()
        return self.driver.execute_script("return arguments[0].validationMessage;", el)

    def logout(self):
        self.find_first(self.LOGOUT, timeout=5).click()
