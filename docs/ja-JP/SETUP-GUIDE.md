# AIDX経営エージェントシステム セットアップガイド

企業の経営者・経営幹部向けの導入手順書です。
AIツールの知識がなくても、この手順通りに進めれば5分で全エージェントが稼働します。

---

## 必要なもの

| 項目 | 説明 | 入手方法 |
|------|------|---------|
| **PC** | Mac / Windows / Linux いずれか | — |
| **Python 3.9以上** | プログラムの実行環境 | <https://www.python.org/downloads/> |
| **Git** | リポジトリのダウンロードに使用 | <https://git-scm.com/downloads> |
| **Anthropic APIキー** | AI（Claude）を動かすための鍵 | 下記「APIキーの取得方法」参照 |

### APIキーの取得方法

1. <https://console.anthropic.com/> にアクセス
2. アカウントを作成（メールアドレスで登録）
3. クレジットカードを登録してAPIプランに加入
4. 「API Keys」ページで「Create Key」をクリック
5. 表示されたキー（`sk-ant-...`）をコピーして保管

> APIの利用料金は従量課金です。目安として月額 $20〜$100 程度（使用量による）。

---

## セットアップ手順

### Step 1: リポジトリをダウンロード

ターミナル（Macは「ターミナル」、Windowsは「PowerShell」）を開いて：

```bash
git clone https://github.com/Shibayu-11/Recustep-AIDXplugin.git
cd Recustep-AIDXplugin
```

### Step 2: APIキーを設定

```bash
cp .env.example .env
```

コピーした `.env` ファイルをテキストエディタで開き、`sk-ant-xxxxx` の部分を自分のAPIキーに書き換えてください。

```
ANTHROPIC_API_KEY=sk-ant-あなたのキーをここに貼り付け
```

### Step 3: 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

### Step 4: 起動

```bash
python main.py
```

以下の画面が表示されれば成功です：

```
  ╔═══════════════════════════════════════════════╗
  ║     AIDX 経営エージェントシステム v0.1        ║
  ║     Powered by Rikustep × Claude API          ║
  ╚═══════════════════════════════════════════════╝

利用可能なAI部下:
   財務エージェント     法務エージェント
   労務エージェント     秘書エージェント
   経営戦略エージェント

社長 >
```

あとは日本語で話しかけるだけです。

---

## 基本的な使い方

### 話しかけるだけでOK

```
社長 > 今月の売上を分析して
```
→ 自動的に財務エージェントに振り分けられます

```
社長 > この契約書のリスクを教えて
```
→ 自動的に法務エージェントに振り分けられます

### データを分析させる

1. `data/financial/` フォルダにExcelファイルを置く
2. 「data/financial/売上表.xlsx を分析して」と話しかける
3. 財務エージェントが分析レポートを生成

契約書PDFも同様に `data/contracts/` に置くだけで分析できます。

### 終了方法

```
社長 > 終了
```
または `Ctrl + C`

---

## トラブルシューティング

### `python` コマンドが見つからない

Macの場合は `python3` を使ってください：
```bash
python3 main.py
```

### `pip install` でエラーが出る

```bash
pip3 install -r requirements.txt
```
または：
```bash
python3 -m pip install -r requirements.txt
```

### APIキーのエラーが出る

- `.env` ファイルが存在するか確認
- APIキーが正しくコピーされているか確認（前後にスペースがないか）
- Anthropicアカウントにクレジットが残っているか確認

### Windows環境での注意

- PowerShellを「管理者として実行」してください
- パスに日本語が含まれるとエラーになる場合があります。英数字のみのフォルダに配置してください

---

## サポート

問題が発生した場合は、Rikustepの担当者にお問い合わせください。

- GitHub Issues: <https://github.com/Shibayu-11/Recustep-AIDXplugin/issues>

---

*本システムは [everything-claude-code](https://github.com/affaan-m/everything-claude-code) をベースに、企業経営支援向けにカスタマイズしたものです。*
