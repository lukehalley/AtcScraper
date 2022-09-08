from tempfile import mkdtemp
from faker import Faker


def getBrowsersArgs():

    # Create fake user agent
    fakerInstance = Faker()
    fakeUserAgent = fakerInstance.user_agent()

    args = ['--no-first-run',
    '--ignore-certificate-errors',
    '--allow-running-insecure-content',
    f'--user-agent={fakeUserAgent}',
    '--no-sandbox',
    "--single-process",
    "--no-zygote",
    f"--data-path={mkdtemp()}",
    f"--disk-cache-dir={mkdtemp()}",
    "--remote-debugging-port=9222",
    '--disable-infobars',
    '--disable-extensions',
    '--disable-client-side-phishing-detection',
    '--disable-web-security',
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-dev-tools"]

    return args