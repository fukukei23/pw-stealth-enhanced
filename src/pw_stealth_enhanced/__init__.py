"""pw-stealth-enhanced: Enhanced stealth/anti-fingerprinting for Playwright."""

from pw_stealth_enhanced.core import (
    StealthConfig,
    apply_stealth,
    create_context_with_stealth,
    DEFAULT_USER_AGENT_POOL,
    DEFAULT_VIEWPORT_POOL,
)

__version__ = "0.1.0"

__all__ = [
    "StealthConfig",
    "apply_stealth",
    "create_context_with_stealth",
    "DEFAULT_USER_AGENT_POOL",
    "DEFAULT_VIEWPORT_POOL",
]
