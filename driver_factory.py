from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

import config


def create_driver():
    """Builds a WebDriver. Selenium Manager (built into Selenium 4.6+) downloads the driver."""
    if config.BROWSER == "firefox":
        opts = FirefoxOptions()
        if config.HEADLESS:
            opts.add_argument("-headless")
        driver = webdriver.Firefox(options=opts)
    elif config.BROWSER == "edge":
        opts = EdgeOptions()
        if config.HEADLESS:
            opts.add_argument("--headless=new")
        driver = webdriver.Edge(options=opts)
    else:
        opts = ChromeOptions()
        if config.HEADLESS:
            opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1440,900")
        opts.add_argument("--disable-notifications")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=opts)

    driver.set_window_size(*config.VIEWPORTS["desktop"])
    return driver
