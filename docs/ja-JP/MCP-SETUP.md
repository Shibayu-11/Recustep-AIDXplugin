# MCP外部連携セットアップガイド

MCP（Model Context Protocol）を使って、AIDXエージェントをGmail・Google Calendar・Slack・Chatwork等の外部サービスと連携させることができます。

---

## MCP設定ファイル

AIDX用のMCP設定は `mcp-configs/aidx-business.json` にまとまっています。
使いたいサーバーの設定を `~/.claude.json` の `mcpServers` セクションにコピーしてください。

---

## Google連携（Gmail / Calendar / Drive）

### 1. Google Cloud Console でプロジェクトを作成

1. <https://console.cloud.google.com/> にアクセス
2. 「新しいプロジェクト」を作成
3. プロジェクト名: `AIDX` など任意

### 2. APIを有効化

以下のAPIを有効化してください：
- Gmail API
- Google Calendar API
- Google Drive API

「APIとサービス」→「ライブラリ」から検索して有効化

### 3. OAuth 2.0認証情報を作成

1. 「APIとサービス」→「認証情報」→「認証情報を作成」→「OAuthクライアントID」
2. アプリケーションの種類: 「ウェブアプリケーション」
3. 承認済みリダイレクトURI: `http://localhost:3000/oauth/callback`
4. 作成後、**クライアントID** と **クライアントシークレット** をメモ

### 4. .env に追加

```
GOOGLE_CLIENT_ID=あなたのクライアントID
GOOGLE_CLIENT_SECRET=あなたのクライアントシークレット
```

### 5. ~/.claude.json に設定を追加

```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-gmail"],
      "env": {
        "GOOGLE_CLIENT_ID": "あなたのクライアントID",
        "GOOGLE_CLIENT_SECRET": "あなたのクライアントシークレット",
        "GOOGLE_REDIRECT_URI": "http://localhost:3000/oauth/callback"
      }
    },
    "google-calendar": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-google-calendar"],
      "env": {
        "GOOGLE_CLIENT_ID": "あなたのクライアントID",
        "GOOGLE_CLIENT_SECRET": "あなたのクライアントシークレット",
        "GOOGLE_REDIRECT_URI": "http://localhost:3000/oauth/callback"
      }
    }
  }
}
```

### できるようになること

| 機能 | エージェント | 例 |
|------|-------------|-----|
| メール送信 | 秘書 | 「田中さんに会議の案内メールを送って」 |
| メール検索 | 秘書 | 「先週の田中さんからのメールを探して」 |
| 予定作成 | 秘書 | 「来週月曜10時に経営会議を入れて」 |
| 予定確認 | 秘書 | 「明日のスケジュールを教えて」 |
| ファイル検索 | 全員 | 「Driveにある先月の売上データを探して」 |

---

## Slack連携

### 1. Slack Appを作成

1. <https://api.slack.com/apps> にアクセス
2. 「Create New App」→「From scratch」
3. App Name: `AIDX Agent`、Workspace: 対象のワークスペースを選択

### 2. Bot Token Scopesを追加

「OAuth & Permissions」→「Bot Token Scopes」に以下を追加：
- `chat:write` — メッセージ送信
- `channels:read` — チャンネル一覧取得
- `channels:history` — チャンネル履歴の読み取り
- `users:read` — ユーザー情報取得

### 3. ワークスペースにインストール

「Install to Workspace」をクリックして承認

### 4. Bot Tokenをメモ

`xoxb-` で始まるBot User OAuth Tokenをコピー

### 5. ~/.claude.json に設定を追加

```json
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-あなたのトークン",
        "SLACK_TEAM_ID": "あなたのチームID"
      }
    }
  }
}
```

### できるようになること

| 機能 | 例 |
|------|-----|
| 議事録の自動投稿 | 議事録作成後に #meeting チャンネルに自動投稿 |
| アクション通知 | アクションアイテムの担当者にDMで通知 |
| 日報送信 | 「今日の日報を #daily に投稿して」 |

---

## Chatwork連携

### 1. APIトークンを取得

1. <https://www.chatwork.com/service/packages/chatwork/subpackages/api/token.php> にアクセス
2. APIトークンをコピー

### 2. ~/.claude.json に設定を追加

```json
{
  "mcpServers": {
    "chatwork": {
      "command": "npx",
      "args": ["-y", "chatwork-mcp-server"],
      "env": {
        "CHATWORK_API_TOKEN": "あなたのAPIトークン"
      }
    }
  }
}
```

### できるようになること

| 機能 | 例 |
|------|-----|
| メッセージ送信 | 「経営会議の議事録をChatworkに送って」 |
| タスク作成 | 「佐藤さんにタスクを追加して」 |

---

## 推奨構成

### 最小構成（すぐ始められる）

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./data"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

### 標準構成（Google + Slack）

filesystem + memory + gmail + google-calendar + slack

### フル構成

全サーバー有効化（MCPサーバーは同時10個以下を推奨）

---

## トラブルシューティング

### MCPサーバーが起動しない

- Node.js 18以上がインストールされているか確認
- `npx` コマンドが使えるか確認: `npx --version`

### Google認証でエラーが出る

- リダイレクトURIが正確に `http://localhost:3000/oauth/callback` になっているか確認
- APIが有効化されているか確認
- OAuth同意画面が設定されているか確認

### Slackでメッセージが送れない

- Botが対象チャンネルに招待されているか確認（`/invite @AIDX Agent`）
- Bot Token Scopesに `chat:write` が含まれているか確認
