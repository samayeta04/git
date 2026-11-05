# LaunchX Selenium Automation (Python + pytest)

Tests the sign-in page at https://launchx.inquocv.com/launchx-app.
User IDs (e-mails) and passwords are read from `test_data/users.xlsx`.

## Setup
```bash
pip install -r requirements.txt
```
Chrome (or Firefox/Edge) must be installed. Selenium Manager downloads the driver automatically.

## Fill in the Excel file
`test_data/users.xlsx` → sheet **Users**

| TestID | Email | Password | Expected | Description |
|---|---|---|---|---|
| U001 | real.user@college.edu | ******** | valid | Valid student |
| U003 | nobody@example.com | Wrong@123 | invalid | Unregistered |

- `Expected = valid` → login must succeed; `invalid` → login must be rejected.
- Rows whose values still start with `REPLACE_` are skipped automatically.
- Each row becomes its own test case.

## Run
```bash
pytest                          # everything, HTML report in reports/report.html
pytest -m smoke                 # quick sanity only
pytest -m datadriven            # only Excel-driven tests
pytest -m "negative or security"
HEADLESS=true pytest            # no browser window
BROWSER=firefox pytest          # chrome | firefox | edge
USERS_XLSX=path/to/other.xlsx pytest
```
Failure screenshots go to `reports/screenshots/`.

## Scenarios covered (≈70 test cases)
| Group | IDs | What is checked |
|---|---|---|
| Page load / UI | TC001–TC015 | title, heading, logo, fields, button, invite-only note, no sign-up link, language selector, masked password, tab order, refresh, show/hide toggle |
| Negative | TC020–TC031 | empty fields, bad e-mail formats, unregistered user, whitespace, long input, special chars, unicode, error message, no password in URL, repeated failures |
| Security | TC040–TC043 | SQL-injection strings, XSS payloads, HTTPS, direct access to inner route |
| Responsive | TC050 | mobile / tablet / desktop usability, no horizontal scroll |
| Excel-driven | TC060–TC070 | valid login, Enter-key login, session after refresh, wrong password, e-mail case, logout, back button after logout, invalid users |

## Adjusting locators
The sign-in page is rendered client-side, so each element uses a list of fallback locators in
`pages/login_page.py`. If a test fails with "None of the locators matched", open DevTools, inspect the
element, and add its id/name/CSS to the matching list (EMAIL, PASSWORD, SIGN_IN_BTN, LOGOUT, ERROR …).
Post-login tests treat "sign-in form disappears" as success; add a dashboard-specific check in
`wait_for_login_success()` once you know what the landing page shows.

## Project layout
```
config.py              URL, browser, timeouts, viewports
pages/                 Page objects (BasePage, LoginPage)
utils/                 driver_factory, excel_reader
tests/                 conftest.py (fixtures, screenshot-on-fail), test_login.py
test_data/users.xlsx   User IDs / passwords
reports/               HTML report + screenshots
```
