import os
from tempfile import mkdtemp
from faker import Faker
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

from src.utils.env import checkIsDocker

isDocker = checkIsDocker()

def configureChromeOptions():

    # Create new chrome options
    options = webdriver.ChromeOptions()

    # Create fake user agent
    fake_user_agent = Faker()

    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_argument('--no-first-run')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--user-agent=' + fake_user_agent.user_agent())
    options.add_argument('--no-sandbox')
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")

    # Disables
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-client-side-phishing-detection')
    options.add_argument('--disable-web-security')
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")

    if isDocker:
        options.binary_location = '/opt/chrome/chrome'
        options.add_argument('--headless')

    options.add_argument('--headless')

    return options

def initDriver(options):
    capabilities = DesiredCapabilities.CHROME
    capabilities["pageLoadStrategy"] = "none"
    driver = webdriver.Chrome("/opt/chromedriver", options=options)
    driver.maximize_window()

    return driver

def getTimeout():
    return int(os.getenv('SEL_WAIT_TIME'))