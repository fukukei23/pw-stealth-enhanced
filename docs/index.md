---
title: 概要
nav_order: 1
---

# pw-stealth-enhanced

> 📂 **[GitHub リポジトリ →](https://github.com/fukukei23/pw-stealth-enhanced)**{: .btn .btn-blue } — ソースコード・技術詳細はこちらから

`playwright-stealth` の後継。Python Playwright向けの包括的なステルス/アンチフィンガープリントライブラリ。

## できること

- **navigator.webdriver** マス킹（ボット検出で最も重要）
- **Canvas** フィンガープリントのノイズ注入
- **WebGL** ベンダー/レンダラー偽装
- **Audio** フィンガープリント摂動
- **フォント列挙** 偽装
- **User-Agent / ビューポート** ローテーションプール
- **ロケール / タイムゾーン** 偽装

## アーキテクチャ

```
ユーザーコード
  → apply_stealth(context)
     ├─ _JS_BASE_STEALTH: webdriver / language / timezone
     ├─ _JS_ADVANCED_STEALTH: canvas / webgl / audio / fonts / permissions
     └─ _build_locale_script(): 動的ロケール/タイムゾーン上書き
```

## 技術スタック

| カテゴリ | 技術 |
|---|---|
| 言語 | Python 3.10+ |
| 依存 | Playwright >= 1.40 |
| テスト | pytest |

---

> 👉 各機能の詳細はサイドバーの **機能ショーケース** をご覧ください。
