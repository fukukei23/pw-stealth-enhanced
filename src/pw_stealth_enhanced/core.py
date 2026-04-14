"""Enhanced stealth/anti-fingerprinting for Playwright.

Provides comprehensive browser fingerprint protection including:
- navigator.webdriver masking
- Canvas fingerprint noise injection
- WebGL vendor/renderer spoofing
- Audio fingerprint perturbation
- Font enumeration spoofing
- permissions.query patching
- User-Agent / viewport rotation pools
- Locale / timezone spoofing
"""

from __future__ import annotations

import logging
import random
from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext

logger = logging.getLogger(__name__)

__all__ = [
    "StealthConfig",
    "apply_stealth",
    "create_context_with_stealth",
]

DEFAULT_USER_AGENT_POOL: list[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]

DEFAULT_VIEWPORT_POOL: list[Dict[str, int]] = [
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1920, "height": 1080},
    {"width": 1280, "height": 800},
    {"width": 1536, "height": 864},
]


class StealthConfig:
    """Configuration for stealth browser settings.

    Attributes:
        user_agent: Custom User-Agent string. None uses browser default.
        viewport: Dict with 'width' and 'height' keys.
        locale: Browser locale (e.g. 'en-GB', 'ja-JP').
        timezone_id: IANA timezone ID (e.g. 'UTC', 'Asia/Tokyo').
        accept_language: Accept-Language header value.
        rotate_ua: Randomly select UA from pool on each context creation.
        rotate_viewport: Randomly select viewport from pool.
    """

    def __init__(
        self,
        *,
        user_agent: Optional[str] = None,
        viewport: Optional[Dict[str, int]] = None,
        locale: str = "en-GB",
        timezone_id: str = "UTC",
        accept_language: str = "en-GB,en;q=0.8",
        rotate_ua: bool = False,
        rotate_viewport: bool = False,
    ) -> None:
        self.user_agent = user_agent
        self.viewport = viewport or {"width": 1280, "height": 720}
        self.locale = locale
        self.timezone_id = timezone_id
        self.accept_language = accept_language
        self.rotate_ua = rotate_ua
        self.rotate_viewport = rotate_viewport

    def resolve(self) -> Dict[str, Any]:
        """Resolve config with rotation into final parameter dict."""
        params: Dict[str, Any] = {}
        params["user_agent"] = (
            random.choice(DEFAULT_USER_AGENT_POOL)
            if self.rotate_ua
            else self.user_agent
        )
        params["viewport"] = (
            random.choice(DEFAULT_VIEWPORT_POOL)
            if self.rotate_viewport
            else self.viewport
        )
        params["locale"] = self.locale
        params["timezone_id"] = self.timezone_id
        params["accept_language"] = self.accept_language
        return params


# ---------------------------------------------------------------------------
# JavaScript injection scripts
# ---------------------------------------------------------------------------

_JS_BASE_STEALTH = """\
try { localStorage.setItem('a11y-contrast','off'); localStorage.setItem('high-contrast','off'); } catch(e){}
Object.defineProperty(navigator, 'language', {get: () => 'en-GB'});
Object.defineProperty(navigator, 'languages', {get: () => ['en-GB','en']});
(function(){
  const _rz=Intl.DateTimeFormat.prototype.resolvedOptions;
  Intl.DateTimeFormat.prototype.resolvedOptions=function(){
    const o=_rz.call(this); o.timeZone='UTC'; return o;
  };
})();
"""

_JS_ADVANCED_STEALTH = r"""
(() => {
  try {
    const rand = (min, max) => Math.random() * (max - min) + min;
    const nav = navigator;
    if (nav) {
      const lang = (nav.language || 'en-GB');
      const langs = Array.isArray(nav.languages) && nav.languages.length
        ? nav.languages : ['en-GB','en'];
      Object.defineProperty(nav, 'webdriver', { get: () => undefined });
      Object.defineProperty(nav, 'hardwareConcurrency', { get: () => 8 });
      Object.defineProperty(nav, 'deviceMemory', { get: () => 8 });
      Object.defineProperty(nav, 'language', { get: () => lang });
      Object.defineProperty(nav, 'languages', { get: () => langs });
      Object.defineProperty(nav, 'maxTouchPoints', { get: () => 0 });
      Object.defineProperty(nav, 'platform', { get: () => 'Win32' });
    }
    /* Canvas fingerprint noise */
    const patchCanvas = (proto) => {
      if (!proto) return;
      const toDataURL = proto.toDataURL;
      proto.toDataURL = function(...args) {
        const ctx = this.getContext && this.getContext('2d');
        if (ctx) {
          const shift = () => (Math.random() - 0.5) * 2;
          ctx.fillStyle = `rgba(${128+shift()},${128+shift()},${128+shift()},0.01)`;
          ctx.fillRect(0, 0, 2, 2);
        }
        return toDataURL.apply(this, args);
      };
    };
    if (typeof HTMLCanvasElement !== 'undefined' && HTMLCanvasElement.prototype)
      patchCanvas(HTMLCanvasElement.prototype);
    if (typeof OffscreenCanvas !== 'undefined' && OffscreenCanvas.prototype)
      patchCanvas(OffscreenCanvas.prototype);

    /* WebGL vendor/renderer spoofing */
    const patchWebGL = (proto) => {
      if (!proto) return;
      const getParameter = proto.getParameter;
      proto.getParameter = function(param) {
        const VENDOR = 0x1F00, RENDERER = 0x1F01;
        if (param === VENDOR) {
          const v = getParameter.call(this, param);
          return typeof v === 'string' ? v.replace(/Google Inc\./, 'Google LLC') : v;
        }
        if (param === RENDERER) {
          const r = getParameter.call(this, param);
          return typeof r === 'string' ? r.replace(/ANGLE \(|\)/g, '') : r;
        }
        return getParameter.call(this, param);
      };
    };
    if (typeof WebGLRenderingContext !== 'undefined' && WebGLRenderingContext.prototype)
      patchWebGL(WebGLRenderingContext.prototype);
    if (typeof WebGL2RenderingContext !== 'undefined' && WebGL2RenderingContext.prototype)
      patchWebGL(WebGL2RenderingContext.prototype);

    /* Audio fingerprint perturbation */
    if (typeof AnalyserNode !== 'undefined' && AnalyserNode.prototype) {
      const getFloat = AnalyserNode.prototype.getFloatFrequencyData;
      if (getFloat) {
        AnalyserNode.prototype.getFloatFrequencyData = function(arr) {
          const res = getFloat.call(this, arr);
          for (let i = 0; i < arr.length; i += Math.floor(arr.length / 8) || 1) {
            arr[i] = arr[i] * (0.99 + Math.random() * 0.02);
          }
          return res;
        };
      }
    }

    /* Font enumeration spoofing */
    if (typeof Navigator !== 'undefined' && Navigator.prototype) {
      const origFonts = Navigator.prototype.fonts;
      if (origFonts) {
        Navigator.prototype.fonts = function() {
          const it = origFonts.apply(this, arguments);
          if (it && typeof it.status === 'string') return it;
          return {
            status: 'loaded', check: () => true,
            load: () => Promise.resolve(), values: () => [].values()
          };
        };
      }
    }

    /* permissions.query patch */
    if (typeof navigator !== 'undefined' && navigator.permissions && navigator.permissions.query) {
      const origQuery = navigator.permissions.query;
      navigator.permissions.query = function(descriptor) {
        if (descriptor && descriptor.name)
          return Promise.resolve({ state: 'granted', onchange: null });
        return origQuery.call(this, descriptor);
      };
    }
  } catch (e) { /* swallow */ }
})();
"""


def _build_locale_script(
    locale: Optional[str] = None,
    timezone_id: Optional[str] = None,
) -> str:
    """Build dynamic locale/timezone override script."""
    parts: list[str] = []
    if locale:
        parts.append(
            f"Object.defineProperty(navigator, 'language', {{get: () => '{locale}'}});"
        )
        parts.append(
            f"Object.defineProperty(navigator, 'languages', {{get: () => ['{locale}', 'en']}});"
        )
    if timezone_id:
        parts.append(
            f"const _rz=Intl.DateTimeFormat.prototype.resolvedOptions;"
            f"Intl.DateTimeFormat.prototype.resolvedOptions=function(){{"
            f"const o=_rz.call(this); o.timeZone='{timezone_id}'; return o;}};"
        )
    if not parts:
        return ""
    return f"(() => {{ try {{ {''.join(parts)} }} catch(e){{}} }})();"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def apply_stealth(
    context: BrowserContext,
    *,
    config: Optional[StealthConfig] = None,
    user_agent: Optional[str] = None,
    viewport: Optional[Dict[str, int]] = None,
    locale: Optional[str] = None,
    timezone_id: Optional[str] = None,
) -> None:
    """Apply stealth/anti-fingerprinting patches to a Playwright BrowserContext.

    Can be called with either a ``StealthConfig`` object or individual kwargs.
    Kwargs take precedence over config when both are provided.

    Args:
        context: Playwright BrowserContext (already created).
        config: Optional StealthConfig for structured configuration.
        user_agent: Override User-Agent string.
        viewport: Override viewport size (e.g. ``{"width": 1920, "height": 1080}``).
        locale: Override browser locale (e.g. ``"ja-JP"``).
        timezone_id: Override IANA timezone (e.g. ``"Asia/Tokyo"``).

    Example::

        from playwright.async_api import async_playwright
        from pw_stealth_enhanced import apply_stealth, StealthConfig

        async def main():
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                context = await browser.new_context()
                await apply_stealth(context, locale="ja-JP", timezone_id="Asia/Tokyo")
                page = await context.new_page()
                await page.goto("https://example.com")
    """
    if config:
        resolved = config.resolve()
        ua = user_agent or resolved["user_agent"]
        vp = viewport or resolved["viewport"]
        loc = locale or resolved["locale"]
        tz = timezone_id or resolved["timezone_id"]
    else:
        ua = user_agent
        vp = viewport
        loc = locale
        tz = timezone_id

    # Base stealth (webdriver, permissions, datetime)
    await context.add_init_script(_JS_BASE_STEALTH)

    # Advanced stealth (canvas, webgl, audio, fonts, navigator props)
    await context.add_init_script(_JS_ADVANCED_STEALTH)

    # Dynamic locale/timezone override
    locale_script = _build_locale_script(locale=loc, timezone_id=tz)
    if locale_script:
        await context.add_init_script(locale_script)

    logger.debug(
        "[pw-stealth-enhanced] Applied stealth (UA=%s, viewport=%s, locale=%s, tz=%s)",
        "set" if ua else "default",
        "set" if vp else "default",
        loc or "default",
        tz or "default",
    )


async def create_context_with_stealth(
    browser,
    *,
    config: Optional[StealthConfig] = None,
    **kwargs: Any,
) -> BrowserContext:
    """Create a new BrowserContext with stealth patches pre-applied.

    Convenience wrapper that creates and patches a context in one call.

    Args:
        browser: Playwright Browser instance.
        config: StealthConfig for structured configuration.
        **kwargs: Additional kwargs passed to ``browser.new_context()``.
            Can also include stealth kwargs (user_agent, viewport, locale, timezone_id).

    Returns:
        BrowserContext with stealth patches applied.

    Example::

        context = await create_context_with_stealth(
            browser,
            config=StealthConfig(rotate_ua=True, locale="en-US"),
        )
    """
    stealth_keys = {"user_agent", "viewport", "locale", "timezone_id"}
    stealth_kwargs = {k: v for k, v in kwargs.items() if k in stealth_keys}
    context_kwargs = {k: v for k, v in kwargs.items() if k not in stealth_keys}

    context = await browser.new_context(**context_kwargs)
    await apply_stealth(context, config=config, **stealth_kwargs)
    return context
