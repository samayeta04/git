"""Central configuration. Override anything via environment variables."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

BASE_URL = os.getenv("LAUNCHX_URL", "https://launchx.inquocv.com/launchx-app")
BROWSER = os.getenv("BROWSER", "chrome").lower()          # chrome | firefox | edge
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
TIMEOUT = int(os.getenv("TIMEOUT", "15"))                 # explicit-wait seconds
NEG_TIMEOUT = int(os.getenv("NEG_TIMEOUT", "4"))          # wait used when expecting "nothing happens"

EXCEL_PATH = Path(os.getenv("USERS_XLSX", BASE_DIR / "test_data" / "users.xlsx"))
EXCEL_SHEET = os.getenv("USERS_SHEET", "Users")

SCREENSHOT_DIR = BASE_DIR / "reports" / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Values in the Excel file that mean "not filled in yet" -> those rows are skipped.
PLACEHOLDER_PREFIXES = ("REPLACE_", "CHANGE_ME", "<")

VIEWPORTS = {
    "mobile": (390, 844),
    "tablet": (820, 1180),
    "desktop": (1440, 900),
}
