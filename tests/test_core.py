"""Tests for pw_stealth_enhanced."""

import pytest
from pw_stealth_enhanced import StealthConfig, apply_stealth, DEFAULT_USER_AGENT_POOL


class TestStealthConfig:
    """Tests for StealthConfig resolution."""

    def test_default_values(self):
        config = StealthConfig()
        params = config.resolve()
        assert params["locale"] == "en-GB"
        assert params["timezone_id"] == "UTC"
        assert params["viewport"] == {"width": 1280, "height": 720}

    def test_custom_values(self):
        config = StealthConfig(
            user_agent="TestAgent/1.0",
            locale="ja-JP",
            timezone_id="Asia/Tokyo",
        )
        params = config.resolve()
        assert params["user_agent"] == "TestAgent/1.0"
        assert params["locale"] == "ja-JP"
        assert params["timezone_id"] == "Asia/Tokyo"

    def test_ua_rotation(self):
        config = StealthConfig(rotate_ua=True)
        params = config.resolve()
        assert params["user_agent"] in DEFAULT_USER_AGENT_POOL

    def test_viewport_rotation(self):
        from pw_stealth_enhanced import DEFAULT_VIEWPORT_POOL
        config = StealthConfig(rotate_viewport=True)
        params = config.resolve()
        assert params["viewport"] in DEFAULT_VIEWPORT_POOL


class TestApplyStealth:
    """Tests for apply_stealth function."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock BrowserContext."""
        class MockContext:
            def __init__(self):
                self.scripts = []

            async def add_init_script(self, script):
                self.scripts.append(script)

        return MockContext()

    @pytest.mark.asyncio
    async def test_apply_stealth_injects_scripts(self, mock_context):
        await apply_stealth(mock_context)
        assert len(mock_context.scripts) >= 2

    @pytest.mark.asyncio
    async def test_apply_stealth_with_locale(self, mock_context):
        await apply_stealth(mock_context, locale="ja-JP")
        # 3 scripts: base + advanced + locale override
        assert len(mock_context.scripts) == 3
        assert "ja-JP" in mock_context.scripts[2]

    @pytest.mark.asyncio
    async def test_apply_stealth_with_timezone(self, mock_context):
        await apply_stealth(mock_context, timezone_id="Asia/Tokyo")
        assert len(mock_context.scripts) == 3
        assert "Asia/Tokyo" in mock_context.scripts[2]

    @pytest.mark.asyncio
    async def test_apply_stealth_with_config(self, mock_context):
        config = StealthConfig(locale="de-DE", timezone_id="Europe/Berlin")
        await apply_stealth(mock_context, config=config)
        assert len(mock_context.scripts) == 3

    @pytest.mark.asyncio
    async def test_webdriver_masking_in_base_script(self, mock_context):
        await apply_stealth(mock_context)
        # Advanced script should contain webdriver masking
        advanced = mock_context.scripts[1]
        assert "webdriver" in advanced

    @pytest.mark.asyncio
    async def test_canvas_fingerprint_in_advanced_script(self, mock_context):
        await apply_stealth(mock_context)
        advanced = mock_context.scripts[1]
        assert "patchCanvas" in advanced

    @pytest.mark.asyncio
    async def test_webgl_spoofing_in_advanced_script(self, mock_context):
        await apply_stealth(mock_context)
        advanced = mock_context.scripts[1]
        assert "patchWebGL" in advanced
