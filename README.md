# pw-stealth-enhanced

[![CI](https://github.com/fukukei23/pw-stealth-enhanced/actions/workflows/ci.yml/badge.svg)](https://github.com/fukukei23/pw-stealth-enhanced/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

<!-- English: Enhanced stealth/anti-fingerprinting library for Python Playwright, successor to the deprecated playwright-stealth. Provides navigator.webdriver masking, canvas/WebGL/audio fingerprint protection, font enumeration spoofing, and UA/viewport rotation pools. Requires Python 3.10+ and Playwright >= 1.40. -->

`playwright-stealth` の後継。Python Playwright向けの包括的なステルス/アンチフィンガープリントライブラリ。

---

## 開発背景

`playwright-stealth` は2025年以降メンテナンスされておらず、現代のボット検出技術に対応できない。本パッケージは以下を提供する:

- **navigator.webdriver** マスキング（ボット検出で最も重要）
- **Canvas** フィンガープリントのノイズ注入
- **WebGL** ベンダー/レンダラー偽装
- **Audio** フィンガープリント摂動
- **フォント列挙** 偽装
- **permissions.query** パッチ
- **User-Agent / ビューポート** ローテーションプール
- **ロケール / タイムゾーン** 偽装

---

## アーキテクチャ

```
┌──────────────────────────────────────────────┐
│              ユーザーコード                     │
│  from pw_stealth_enhanced import apply_stealth │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│              __init__.py                       │
│     StealthConfig / apply_stealth              │
│     create_context_with_stealth                │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│              core.py                           │
│                                                │
│  ┌─────────────────────────────────────────┐  │
│  │        StealthConfig                     │  │
│  │  UA pool / viewport pool / locale / tz   │  │
│  └─────────────────┬───────────────────────┘  │
│                    │ resolve()                  │
│  ┌─────────────────▼───────────────────────┐  │
│  │     apply_stealth(context)               │  │
│  │  1. _JS_BASE_STEALTH                     │  │
│  │     webdriver / language / timezone      │  │
│  │  2. _JS_ADVANCED_STEALTH                 │  │
│  │     canvas / webgl / audio / fonts       │  │
│  │     navigator props / permissions        │  │
│  │  3. _build_locale_script()               │  │
│  │     動的ロケール/タイムゾーン上書き         │  │
│  └─────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

### ステルス注入の流れ

`apply_stealth()` は3段階のJavaScriptを `context.add_init_script()` で注入する:

1. **Base Stealth**: `navigator.webdriver` の無効化、`language`/`languages` の上書き、`DateTimeFormat` のタイムゾーン偽装
2. **Advanced Stealth**: Canvas の `toDataURL` にノイズ注入、WebGL の `getParameter` でベンダー/レンダラー偽装、AnalyserNode の周波数データ摂動、フォント列挙の偽装、`permissions.query` のパッチ
3. **Dynamic Locale**: ユーザー指定のロケール・タイムゾーンで動的に上書き

---

## 他パッケージとの比較

| 機能 | pw-stealth-enhanced | playwright-stealth | puppeteer-extra-plugin-stealth |
|------|:-------------------:|:------------------:|:-----------------------------:|
| navigator.webdriver マスキング | o | o | o |
| Canvas フィンガープリントノイズ | o | x | o |
| WebGL vendor/renderer 偽装 | o | x | o |
| Audio フィンガープリント摂動 | o | x | o |
| フォント列挙偽装 | o | x | o |
| permissions.query パッチ | o | x | o |
| UA ローテーションプール | o | x | x |
| ビューポートローテーションプール | o | x | x |
| Python Playwright 対応 | o | o | x |
| メンテナンス状態 | 活発 | 停止 | 活発（JSのみ） |
| Python バージョン | 3.10+ | 3.8+ | -- |
| Playwright バージョン | >=1.40 | >=1.20 | -- |

> `playwright-stealth` は navigator.webdriver のマスキングのみを提供し、Canvas/WebGL/Audio等の高度なフィンガープリント対策は含まれていない。

---

## インストール

```bash
pip install pw-stealth-enhanced
```

要件: Python >= 3.10, Playwright >= 1.40

開発用:

```bash
pip install pw-stealth-enhanced[dev]
```

---

## 使い方

### 基本的な使用例

```python
import asyncio
from playwright.async_api import async_playwright
from pw_stealth_enhanced import apply_stealth

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()

        # ステルスパッチを適用
        await apply_stealth(context, locale="ja-JP", timezone_id="Asia/Tokyo")

        page = await context.new_page()
        await page.goto("https://example.com")
        # ... スクレイピング処理 ...

asyncio.run(main())
```

### StealthConfigによる設定

```python
from pw_stealth_enhanced import apply_stealth, StealthConfig

config = StealthConfig(
    rotate_ua=True,           # コンテキストごとにランダムUA
    rotate_viewport=True,     # ランダムビューポートサイズ
    locale="en-US",
    timezone_id="America/New_York",
)
await apply_stealth(context, config=config)
```

### コンテキスト作成と同時に適用

```python
from pw_stealth_enhanced import create_context_with_stealth, StealthConfig

context = await create_context_with_stealth(
    browser,
    config=StealthConfig(rotate_ua=True, locale="en-US"),
)
# この時点でステルスパッチが適用済み
page = await context.new_page()
```

---

## API リファレンス

### `apply_stealth(context, *, config=None, user_agent=None, viewport=None, locale=None, timezone_id=None)`

既存の `BrowserContext` にステルスパッチを適用する。

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `context` | BrowserContext | Playwrightのブラウザコンテキスト |
| `config` | StealthConfig | 構造化設定（任意） |
| `user_agent` | str | User-Agent文字列の上書き |
| `viewport` | dict | `{"width": int, "height": int}` |
| `locale` | str | ブラウザロケール（例: `"ja-JP"`） |
| `timezone_id` | str | IANAタイムゾーン（例: `"Asia/Tokyo"`） |

> `config` と個別kwargsを同時に指定した場合、kwargsが優先される。

### `create_context_with_stealth(browser, *, config=None, **kwargs) -> BrowserContext`

新しい `BrowserContext` を作成し、ステルスパッチを事前適用して返す。

### `StealthConfig`

| 属性 | 型 | デフォルト | 説明 |
|------|-----|----------|------|
| `user_agent` | str / None | None | カスタムUA（Noneならブラウザデフォルト） |
| `viewport` | dict / None | `{"width":1280,"height":720}` | ビューポートサイズ |
| `locale` | str | `"en-GB"` | ブラウザロケール |
| `timezone_id` | str | `"UTC"` | IANAタイムゾーン |
| `accept_language` | str | `"en-GB,en;q=0.8"` | Accept-Languageヘッダー |
| `rotate_ua` | bool | False | プールからランダムUAを選択 |
| `rotate_viewport` | bool | False | プールからランダムビューポートを選択 |

### 組み込みプール

- `DEFAULT_USER_AGENT_POOL`: 5種類の最新Chrome/Edge UA
- `DEFAULT_VIEWPORT_POOL`: 5種類の一般的な解像度（1366x768, 1440x900, 1920x1080, 1280x800, 1536x864）

---

## 動作確認

ステルス設定をテスト可能なサイト:

- https://bot.sannysoft.com/ -- webdriver検出
- https://abrahamjuliot.github.io/creepjs/ -- 総合フィンガープリント
- https://browserleaks.com/canvas -- Canvas フィンガープリント

---

## テストの実行

```bash
pip install pw-stealth-enhanced[dev]
pytest
```

---

## License

MIT
