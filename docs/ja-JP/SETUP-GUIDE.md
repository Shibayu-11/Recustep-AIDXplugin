# Recustep-AIDXplugin セットアップガイド

企業のDX推進担当者向けの導入手順書です。  
このツールキットを使うことで、Claude Code（AI開発アシスタント）を業務に最適化された状態で導入できます。

---

## 前提条件

以下のツールが必要です。IT部門と連携してインストールしてください。

| ツール | 用途 | インストール方法 |
|--------|------|------------------|
| **Node.js** (v18以上) | ツールキットの実行環境 | https://nodejs.org/ からLTS版をダウンロード |
| **Git** | リポジトリのダウンロード | https://git-scm.com/ |
| **Claude Code** | AI開発アシスタント本体 | `npm install -g @anthropic-ai/claude-code` |
| **Anthropic APIキー** | Claude Codeの利用に必要 | https://console.anthropic.com/ でアカウント作成後に取得 |

### バージョン確認コマンド

ターミナル（Macは「ターミナル」、Windowsは「PowerShell」）を開いて以下を実行してください。

```bash
node --version    # v18.0.0 以上が表示されればOK
git --version     # バージョンが表示されればOK
claude --version  # Claude Codeのバージョンが表示されればOK
```

---

## Step 1: リポジトリをダウンロード

```bash
git clone https://github.com/Shibayu-11/Recustep-AIDXplugin.git
cd Recustep-AIDXplugin
```

---

## Step 2: 依存パッケージをインストール

```bash
npm install
```

---

## Step 3: APIキーを設定

Anthropic APIキーを環境変数として設定します。

**Mac / Linux:**
```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxx..."
```

> 毎回設定するのが面倒な場合は、`~/.zshrc`（Mac）や `~/.bashrc`（Linux）に上記の行を追加してください。

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-xxxxx..."
```

---

## Step 4: ツールキットを適用

プロジェクトのルートディレクトリで以下を実行します。

```bash
# 自動インストール（推奨）
./install.sh

# または手動でnpx経由
npx ecc typescript   # TypeScriptプロジェクト向け
npx ecc python       # Pythonプロジェクト向け
```

これにより、以下が `~/.claude/` 配下にセットアップされます：

- **agents/** - タスクを委任できるAIサブエージェント
- **skills/** - 業務ワークフローの定義
- **hooks/** - 自動化トリガー（ファイル保存時の自動チェックなど）
- **rules/** - コーディング規約・セキュリティルール
- **mcp-configs/** - 外部サービス連携の設定

---

## Step 5: Claude Codeを起動して動作確認

任意のプロジェクトフォルダに移動してClaude Codeを起動します。

```bash
cd ~/your-project
claude
```

起動後、以下のコマンドが使えることを確認してください：

```
/plan          → 実装計画を立てる
/code-review   → コードレビューを実行
/tdd           → テスト駆動開発ワークフロー
/build-fix     → ビルドエラーを自動修正
```

---

## よくある業務での活用例

### 既存コードの理解
```
このプロジェクトの全体構造を説明して
```

### バグ修正
```
○○画面でエラーが出ている。原因を調査して修正して
```

### コードレビュー
```
/code-review
```

### ドキュメント作成
```
このAPIの仕様書を作成して
```

### テスト作成
```
/tdd
```

---

## トラブルシューティング

### `claude` コマンドが見つからない

```bash
npm install -g @anthropic-ai/claude-code
```

を再実行してください。パスが通っていない場合は、ターミナルを再起動してください。

### APIキーのエラーが出る

- APIキーが正しく設定されているか確認: `echo $ANTHROPIC_API_KEY`
- APIキーの残高（クレジット）があるか https://console.anthropic.com/ で確認

### `npm install` でエラーが出る

- Node.jsのバージョンが18以上か確認: `node --version`
- 古い場合は https://nodejs.org/ から最新LTS版をインストール

### Windows環境での注意

- PowerShellを**管理者権限**で起動してください
- `install.sh` の代わりに `install.ps1` を使ってください：
  ```powershell
  .\install.ps1
  ```

---

## セキュリティに関する注意事項

- **APIキーは絶対にGitにコミットしないでください**。`.env` ファイルや環境変数で管理してください。
- Claude Codeはファイルの読み書きやコマンド実行が可能です。**機密情報を含むディレクトリでは慎重に使用**してください。
- 社内のセキュリティポリシーに従い、**APIキーのローテーション**を定期的に行ってください。
- 詳細は [セキュリティガイド](../../the-security-guide.md) を参照してください。

---

## 次のステップ

- [ショートフォームガイド](../../the-shortform-guide.md) - 基本的な使い方と設計思想
- [ロングフォームガイド](../../the-longform-guide.md) - トークン最適化、メモリ永続化、評価手法
- [セキュリティガイド](../../the-security-guide.md) - エージェントセキュリティの包括的ガイド

---

## サポート

問題が発生した場合は、以下に連絡してください：

- GitHub Issues: https://github.com/Shibayu-11/Recustep-AIDXplugin/issues

---

*本ガイドは [everything-claude-code](https://github.com/affaan-m/everything-claude-code) をベースに、企業導入向けにカスタマイズしたものです。*
