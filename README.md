# pw-stealth-enhanced

Enhanced stealth/anti-fingerprinting for Playwright. Successor to the deprecated `playwright-stealth`.

## Why?

`playwright-stealth` has been unmaintained since 2025 and doesn't handle modern bot detection techniques. This package provides comprehensive fingerprint protection with:

- **navigator.webdriver** masking (most critical for bot detection)
- **Canvas** fingerprint noise injection
- **WebGL** vendor/renderer spoofing
- **Audio** fingerprint perturbation
- **Font enumeration** spoofing
- **permissions.query** patching
- **User-Agent / viewport rotation** pools
- **Locale / timezone** spoofing

## Install

```bash
pip install pw-stealth-enhanced
```

Requires [Playwright](https://playwright.dev/python/) >= 1.40.

## Quick Start

```python
import asyncio
from playwright.async_api import async_playwright
from pw_stealth_enhanced import apply_stealth

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()

        # Apply stealth patches
        await apply_stealth(context, locale="ja-JP", timezone_id="Asia/Tokyo")

        page = await context.new_page()
        await page.goto("https://example.com")
        # ... your scraping logic ...

asyncio.run(main())
```

## Configuration

```python
from pw_stealth_enhanced import apply_stealth, StealthConfig

config = StealthConfig(
    rotate_ua=True,           # Random UA on each context
    rotate_viewport=True,     # Random viewport size
    locale="en-US",
    timezone_id="America/New_York",
)
await apply_stealth(context, config=config)
```

## API

### `apply_stealth(context, *, config=None, user_agent=None, viewport=None, locale=None, timezone_id=None)`

Apply stealth patches to an existing `BrowserContext`.

### `create_context_with_stealth(browser, *, config=None, **kwargs)`

Create a new `BrowserContext` with stealth pre-applied.

### `StealthConfig`

Configuration object with rotation pools for UA and viewport.

## Verification

Test your stealth setup at:
- https://bot.sannysoft.com/
- https://abrahamjuliot.github.io/creepjs/
- https://browserleaks.com/canvas

## License

MIT
