"""LaunchX sign-in page: UI, functional, negative, security, responsive and
Excel-driven scenarios.

The site has no public sign-up (invite-only), so the Sign-in page is the testable
surface; post-login checks are kept generic (form disappears / session persists).
"""
import pytest
from selenium.webdriver.common.keys import Keys

import config
from pages.login_page import LoginPage
from utils.excel_reader import users_by_expectation

VALID_USERS = [u for u in users_by_expectation("valid") if not u.is_placeholder]
INVALID_USERS = [u for u in users_by_expectation("invalid") if not u.is_placeholder]


def _ids(users):
    return [u.test_id for u in users]


# =====================================================================================
# 1. UI / page-load scenarios
# =====================================================================================
@pytest.mark.smoke
@pytest.mark.ui
class TestPageLoad:
    def test_TC001_page_loads_with_expected_title(self, login_page):
        assert "launchx" in login_page.driver.title.lower()

    def test_TC002_url_is_correct(self, login_page):
        assert "launchx.inquocv.com" in login_page.driver.current_url

    def test_TC003_heading_and_subtitle_visible(self, login_page):
        assert login_page.exists(login_page.HEADING)
        assert login_page.exists(login_page.SUBTITLE)

    def test_TC004_logo_visible(self, login_page):
        assert login_page.exists(login_page.LOGO)

    def test_TC005_email_and_password_fields_present(self, login_page):
        assert login_page.email_field().is_displayed()
        assert login_page.password_field().is_displayed()

    def test_TC006_sign_in_button_present_and_enabled(self, login_page):
        btn = login_page.sign_in_button()
        assert btn.is_displayed() and btn.is_enabled()

    def test_TC007_invite_only_note_displayed(self, login_page):
        assert login_page.exists(login_page.INVITE_NOTE)

    def test_TC008_no_public_signup_link(self, login_page):
        links = login_page.driver.find_elements(
            "xpath", "//a[contains(translate(.,'SIGNUP','signup'),'sign up') "
                     "or contains(translate(.,'REGISTER','register'),'register')]")
        assert not links, "Public sign-up link should not exist (invite-only)"

    def test_TC009_language_selector_present(self, login_page):
        assert login_page.exists(login_page.LANGUAGE)

    def test_TC010_password_input_is_masked(self, login_page):
        assert login_page.password_field().get_attribute("type") == "password"

    def test_TC011_email_input_type(self, login_page):
        assert login_page.email_field().get_attribute("type") in ("email", "text")

    def test_TC012_fields_accept_typing(self, login_page):
        login_page.type_email("someone@example.com")
        login_page.type_password("abc12345")
        assert login_page.email_field().get_attribute("value") == "someone@example.com"
        assert login_page.password_field().get_attribute("value") == "abc12345"

    def test_TC013_tab_order_email_to_password(self, login_page):
        login_page.email_field().click()
        login_page.email_field().send_keys(Keys.TAB)
        active = login_page.driver.switch_to.active_element
        assert active.get_attribute("type") in ("password", "button")

    def test_TC014_page_refresh_keeps_login_form(self, login_page):
        login_page.driver.refresh()
        assert login_page.is_login_form_visible(timeout=config.TIMEOUT)

    def test_TC015_toggle_show_password_if_available(self, login_page):
        if not login_page.exists(login_page.SHOW_PASSWORD, timeout=2):
            pytest.skip("No show/hide password toggle on this page")
        login_page.type_password("abc12345")
        login_page.find_first(login_page.SHOW_PASSWORD).click()
        assert login_page.password_field().get_attribute("type") == "text"


# =====================================================================================
# 2. Negative / validation scenarios (static data)
# =====================================================================================
@pytest.mark.negative
@pytest.mark.functional
class TestNegativeLogin:
    def test_TC020_both_fields_empty(self, login_page):
        login_page.click_sign_in()
        assert login_page.login_was_rejected()

    def test_TC021_empty_email_valid_looking_password(self, login_page):
        login_page.login("", "Password@123")
        assert login_page.login_was_rejected()

    def test_TC022_empty_password(self, login_page):
        login_page.login("student@example.com", "")
        assert login_page.login_was_rejected()

    @pytest.mark.parametrize("bad_email", [
        "plainaddress", "missing-at.com", "@nodomain.com", "user@", "user@@example.com",
        "user name@example.com", "user@example..com",
    ])
    def test_TC023_invalid_email_format(self, login_page, bad_email):
        login_page.login(bad_email, "Password@123")
        assert login_page.login_was_rejected()

    def test_TC024_unregistered_email(self, login_page):
        login_page.login("no.such.user.98765@example.com", "Password@123")
        assert login_page.login_was_rejected()

    def test_TC025_whitespace_only_credentials(self, login_page):
        login_page.login("     ", "     ")
        assert login_page.login_was_rejected()

    def test_TC026_very_long_inputs(self, login_page):
        login_page.login("a" * 300 + "@example.com", "P@" + "x" * 1000)
        assert login_page.login_was_rejected()

    def test_TC027_special_chars_in_password(self, login_page):
        login_page.login("student@example.com", "!@#$%^&*()_+{}|:<>?~`")
        assert login_page.login_was_rejected()

    def test_TC028_unicode_inputs(self, login_page):
        login_page.login("उपयोगकर्ता@उदाहरण.भारत", "पासवर्ड123")
        assert login_page.login_was_rejected()

    def test_TC029_error_message_shown_on_bad_credentials(self, login_page):
        login_page.login("no.such.user.98765@example.com", "WrongPass#1")
        assert login_page.login_was_rejected()
        assert login_page.error_text() or login_page.is_login_form_visible(), \
            "Expected an error message or to remain on the sign-in form"

    def test_TC030_password_not_leaked_in_url(self, login_page):
        login_page.login("student@example.com", "SuperSecret#1")
        login_page.login_was_rejected()
        url = login_page.driver.current_url
        assert "SuperSecret" not in url and "password" not in url.lower()

    def test_TC031_multiple_failed_attempts_do_not_crash(self, login_page):
        for i in range(3):
            login_page.login(f"bad{i}@example.com", f"Wrong#{i}")
            assert login_page.login_was_rejected(timeout=2)


# =====================================================================================
# 3. Basic security / input-hardening
# =====================================================================================
@pytest.mark.security
class TestSecurity:
    @pytest.mark.parametrize("payload", [
        "' OR '1'='1", "' OR 1=1 --", "admin'--", "\" OR \"\"=\"",
    ])
    def test_TC040_sql_injection_rejected(self, login_page, payload):
        login_page.login(payload, payload)
        assert login_page.login_was_rejected(timeout=2)

    @pytest.mark.parametrize("payload", [
        "<script>alert(1)</script>", "\"><img src=x onerror=alert(1)>",
    ])
    def test_TC041_xss_payload_not_executed(self, login_page, payload):
        from selenium.common.exceptions import NoAlertPresentException
        login_page.login(payload, payload)
        login_page.login_was_rejected(timeout=2)
        with pytest.raises(NoAlertPresentException):
            login_page.driver.switch_to.alert

    def test_TC042_page_served_over_https(self, login_page):
        assert login_page.driver.current_url.startswith("https://")

    def test_TC043_direct_access_to_inner_route_requires_login(self, driver):
        driver.get(config.BASE_URL.rstrip("/") + "/dashboard")
        page = LoginPage(driver)
        # Must either redirect to sign-in / show 404, never expose app content without auth
        assert page.is_login_form_visible(timeout=5) or "404" in driver.page_source \
            or "not found" in driver.page_source.lower()


# =====================================================================================
# 4. Responsive checks
# =====================================================================================
@pytest.mark.responsive
@pytest.mark.ui
@pytest.mark.parametrize("name,size", list(config.VIEWPORTS.items()))
def test_TC050_form_usable_on_viewport(login_page, name, size):
    login_page.driver.set_window_size(*size)
    assert login_page.email_field().is_displayed()
    assert login_page.password_field().is_displayed()
    assert login_page.sign_in_button().is_displayed()
    overflow = login_page.driver.execute_script(
        "return document.documentElement.scrollWidth > document.documentElement.clientWidth + 1;")
    assert not overflow, f"Horizontal scroll on {name} viewport"


# =====================================================================================
# 5. Excel-driven scenarios  (user IDs / passwords come from test_data/users.xlsx)
# =====================================================================================
@pytest.mark.datadriven
@pytest.mark.functional
class TestExcelDriven:
    @pytest.mark.skipif(not VALID_USERS, reason="No valid users filled in users.xlsx")
    @pytest.mark.parametrize("user", VALID_USERS, ids=_ids(VALID_USERS))
    def test_TC060_valid_login(self, login_page, user):
        login_page.login(user.email, user.password)
        assert login_page.wait_for_login_success(), \
            f"{user.test_id}: login failed for {user.email}. Error: {login_page.error_text()}"

    @pytest.mark.skipif(not VALID_USERS, reason="No valid users filled in users.xlsx")
    @pytest.mark.parametrize("user", VALID_USERS[:1], ids=_ids(VALID_USERS[:1]))
    def test_TC061_login_with_enter_key(self, login_page, user):
        login_page.login(user.email, user.password, via_enter=True)
        assert login_page.wait_for_login_success()

    @pytest.mark.skipif(not VALID_USERS, reason="No valid users filled in users.xlsx")
    @pytest.mark.parametrize("user", VALID_USERS[:1], ids=_ids(VALID_USERS[:1]))
    def test_TC062_session_persists_after_refresh(self, login_page, user):
        login_page.login(user.email, user.password)
        assert login_page.wait_for_login_success()
        login_page.driver.refresh()
        assert not login_page.is_login_form_visible(timeout=5), "Session lost after refresh"

    @pytest.mark.skipif(not VALID_USERS, reason="No valid users filled in users.xlsx")
    @pytest.mark.parametrize("user", VALID_USERS[:1], ids=_ids(VALID_USERS[:1]))
    def test_TC063_wrong_password_for_valid_user(self, login_page, user):
        login_page.login(user.email, user.password + "_wrong")
        assert login_page.login_was_rejected()

    @pytest.mark.skipif(not VALID_USERS, reason="No valid users filled in users.xlsx")
    @pytest.mark.parametrize("user", VALID_USERS[:1], ids=_ids(VALID_USERS[:1]))
    def test_TC064_email_case_insensitive(self, login_page, user):
        login_page.login(user.email.upper(), user.password)
        # Informational: most systems treat e-mail case-insensitively
        assert login_page.wait_for_login_success(timeout=8), \
            "E-mail in upper-case was rejected (confirm whether this is intended)"

    @pytest.mark.skipif(not VALID_USERS, reason="No valid users filled in users.xlsx")
    @pytest.mark.parametrize("user", VALID_USERS[:1], ids=_ids(VALID_USERS[:1]))
    def test_TC065_logout_returns_to_signin(self, login_page, user):
        login_page.login(user.email, user.password)
        assert login_page.wait_for_login_success()
        try:
            login_page.logout()
        except Exception:
            pytest.skip("Logout control not found; update LoginPage.LOGOUT locator")
        assert login_page.is_login_form_visible(timeout=config.TIMEOUT)

    @pytest.mark.skipif(not VALID_USERS, reason="No valid users filled in users.xlsx")
    @pytest.mark.parametrize("user", VALID_USERS[:1], ids=_ids(VALID_USERS[:1]))
    def test_TC066_back_button_after_logout_does_not_restore_session(self, login_page, user):
        login_page.login(user.email, user.password)
        assert login_page.wait_for_login_success()
        try:
            login_page.logout()
        except Exception:
            pytest.skip("Logout control not found; update LoginPage.LOGOUT locator")
        login_page.driver.back()
        assert login_page.is_login_form_visible(timeout=5)

    @pytest.mark.skipif(not INVALID_USERS, reason="No invalid users in users.xlsx")
    @pytest.mark.parametrize("user", INVALID_USERS, ids=_ids(INVALID_USERS))
    def test_TC070_invalid_login(self, login_page, user):
        login_page.login(user.email, user.password)
        assert login_page.login_was_rejected(), \
            f"{user.test_id}: login unexpectedly succeeded for {user.email}"
