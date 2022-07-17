import re
from pathlib import Path

from playwright.async_api import async_playwright, BrowserContext
import asyncio

async def coro(websiteName, websiteUrl, browser: BrowserContext) -> None:
    print(websiteName)
    page = await browser.new_page()
    await page.goto(websiteUrl)
    await page.screenshot(path=f'imgs/{websiteName}.jpg', type="jpeg")


async def main() -> None:
    async with async_playwright() as p:

        # Setup Browser
        browser: BrowserContext = await p.chromium.launch_persistent_context(
            headless=False,
            user_data_dir=f"{Path.home()}/.config/chromium",
            viewport={
                "width": 1920,
                "height": 1080
            },
        )
        data = {
            "google": "https://www.google.com/",
            "geeks": "https://www.geeksforgeeks.org/how-to-scrape-the-web-with-playwright-in-python/",
            "1": "https://stackoverflow.com/questions/50757497/simplest-async-await-example-possible-in-python",
            "2": "https://www.google.com/",
            "3": "https://www.geeksforgeeks.org/how-to-scrape-the-web-with-playwright-in-python/",
            "4": "https://stackoverflow.com/questions/50757497/simplest-async-await-example-possible-in-python",
            "5": "https://www.google.com/",
            "6": "https://www.geeksforgeeks.org/how-to-scrape-the-web-with-playwright-in-python/",
            "7": "https://stackoverflow.com/questions/50757497/simplest-async-await-example-possible-in-python",
            "8": "https://www.google.com/",
            "9": "https://www.geeksforgeeks.org/how-to-scrape-the-web-with-playwright-in-python/",
            "10": "https://stackoverflow.com/questions/50757497/simplest-async-await-example-possible-in-python",
            "11": "https://www.google.com/",
            "12": "https://www.geeksforgeeks.org/how-to-scrape-the-web-with-playwright-in-python/",
            "13": "https://stackoverflow.com/questions/50757497/simplest-async-await-example-possible-in-python",
        }
        await asyncio.gather(*(coro(websiteName, websiteUrl, browser) for websiteName, websiteUrl in data.items()))
        await browser.close()

if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())