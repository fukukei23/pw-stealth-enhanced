"""Basic usage example for pw-stealth-enhanced."""

import asyncio
from playwright.async_api import async_playwright
from pw_stealth_enhanced import apply_stealth, StealthConfig


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Option 1: Apply stealth to an existing context
        context = await browser.new_context()
        await apply_stealth(context, locale="ja-JP", timezone_id="Asia/Tokyo")

        page = await context.new_page()
        await page.goto("https://bot.sannysoft.com/")
        await page.screenshot(path="stealth_test.png")
        print("Screenshot saved to stealth_test.png")

        await context.close()

        # Option 2: Use config object with UA rotation
        config = StealthConfig(
            rotate_ua=True,
            rotate_viewport=True,
            locale="en-US",
            timezone_id="America/New_York",
        )
        context2 = await browser.new_context()
        await apply_stealth(context2, config=config)

        page2 = await context2.new_page()
        await page2.goto("https://bot.sannysoft.com/")
        await page2.screenshot(path="stealth_test_rotated.png")

        await context2.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
