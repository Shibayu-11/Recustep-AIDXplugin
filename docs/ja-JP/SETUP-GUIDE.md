# AIDX経営エージェントシステム セットアップガイド

企業の経営者・経営幹部向けの導入手順書です。
AIツールの知識がなくても、この手順通りに進めれば5分で全エージェントが稼働します。

---

## 必要なもの

| 項目 | 説明 | 費用 |
|------|------|------|
| PC | Mac / Windows / Linux いずれか | — |
| Anthropicアカウント | Claude Max プラン（$100 or $200/月） | 月額固定 |
| Claude Code | Anthropicの開発ツール（Max プランに含まれる） | 無料 |
| Git | リポジトリのダウンロードに使用 | 無料 |

### Anthropic Max プランについて

Claude Max プラン（$200/月）を推奨します。

- 月額固定で使い放題（従量課金の心配なし）
- Claude Codeが利用可能
- 「今月いくらかかるか分からない」がない

登録方法：

1. <https://claude.ai/> にアクセス
2. アカウントを作成
3. 「Upgrade」→「Max」プランを選択（$100 or $200/月）
4. Claude Codeが使えるようになります

### Claude Codeのインストール

Mac/Linuxの場合：

```bash
npm install -g @anthropic-ai/claude-code
```

Windowsの場合：

```powershell
npm install -g @anthropic-ai/claude-code
```

> Node.jsが必要です。入ってない場合は <https://nodejs.org/> からインストールしてください。

---

## セットアップ手順

### Step 1: リポジトリをダウンロード

ターミナル（Macは「ターミナル」、Windowsは「PowerShell」）を開いて：

```bash
git clone https://github.com/Shibayu-11/Recustep-AIDXplugin.git
cd Recustep-AIDXplugin
```

### Step 2: Claude Codeを起動

```bash
claude
```

初回起動時にAnthropicアカウントでのログインを求められます。
ログインが完了すると、AIDXの経営エージェントとして動き始めます。

### これだけです。

CLAUDE.mdを自動で読み込むので、起動した瞬間から5人のAI部下が使えます。

---

## 基本的な使い方

### 話しかけるだけでOK

```
> 今月の売上を分析して
```
→ 自動的に財務エージェントに振り分けられます

```
> この契約書のリスクを教えて
```
→ 自動的に法務エージェントに振り分けられます

```
> 議事録を作って
```
→ 秘書エージェントが議事録を生成します

```
> うちの会社のSWOT分析して
```
→ 戦略エージェントがフレームワーク分析を実行します

### データを分析させる

1. `data/financial/` フォルダにExcelファイルを置く
2. 「data/financial/売上表.xlsx を分析して」と話しかける
3. 財務エージェントが分析レポートを生成

契約書PDFも同様に `data/contracts/` に置くだけで分析できます。

### 終了方法

```
> /exit
```
または `Ctrl + C`

---

## あなたが触るフォルダ

3つだけ覚えてください。

```
data/
├── financial/    ← Excelや CSVを置くだけで財務分析が動く
├── contracts/    ← 契約書PDFを置くだけで法務チェックが動く
└── knowledge/    ← 社内マニュアルや規程を置くと記憶に使われる
```

他のフォルダは全部システム内部です。触らないでください。
詳しくは [フォルダガイド](FOLDER-GUIDE.md) を参照。

---

## トラブルシューティング

### `claude` コマンドが見つからない

```bash
npm install -g @anthropic-ai/claude-code
```

を再実行してください。それでもダメならターミナルを再起動。

### ログインできない

- Anthropicアカウントが Max プランか確認
- ブラウザでのログインが完了しているか確認

### 応答が遅い / エラーが出る

- Anthropicのサービス状況を確認: <https://status.anthropic.com/>
- インターネット接続を確認

### Windows環境での注意

- PowerShellを「管理者として実行」してください
- パスに日本語が含まれるとエラーになる場合があります。英数字のみのフォルダに配置してください

---

## 上級者向け: API直接実行

Claude Codeを使わず、Anthropic APIを直接叩く方法もあります。
API従量課金になりますが、より細かい制御が可能です。

```bash
# APIキーを設定
cp .env.example .env
# .env を編集して ANTHROPIC_API_KEY を記入

# Python依存パッケージをインストール
pip install -r requirements.txt

# 起動
python main.py
```

---

## サポート

問題が発生した場合は、Recustepの担当者にお問い合わせください。

- GitHub Issues: <https://github.com/Shibayu-11/Recustep-AIDXplugin/issues>
