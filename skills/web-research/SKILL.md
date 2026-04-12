---
name: web-research
description: Agent Reachを使ったWeb検索・YouTube・Twitter・GitHub等のインターネット情報収集
origin: AIDX
tools: Read, Write, Bash
---

# Web情報収集スキル（Agent Reach連携）

## いつ使うか

- 「競合を調べて」「業界のトレンド教えて」→ Web検索
- 「このYouTube動画の内容を教えて」→ YouTube字幕抽出
- 「Twitterでうちの評判見て」→ Twitter検索
- 「GitHubのこのツール評価して」→ リポジトリ読み取り
- 「最新のニュース教えて」→ Web検索

## 前提条件

Agent Reachがインストール済みであること。
未インストールの場合は以下を実行：

```bash
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto
```

インストール確認:
```bash
agent-reach doctor
```

## 使えるツール

### 1. Web検索（全網検索）

```bash
# MCP経由で自動的に使える（設定済みなら）
# または直接Jina Readerで任意のURLを読む
curl -s "https://r.jina.ai/https://example.com" | head -100
```

使い方: 「〇〇について検索して」と言われたら、Web検索で最新情報を取得。

### 2. YouTube

```bash
# 動画の字幕を取得
yt-dlp --write-sub --skip-download --sub-lang ja,en "URL"

# YouTubeで検索
yt-dlp "ytsearch5:検索キーワード" --get-title --get-id
```

使い方:
- 「このYouTube動画を要約して」→ 字幕を取得して要約
- 「〇〇の解説動画を探して」→ 検索して候補を提示

### 3. Twitter / X

```bash
# ツイートを読む
twitter read "URL"

# 検索
twitter search "キーワード" --limit 20
```

使い方:
- 「うちの会社名でTwitter検索して」→ 評判・口コミの収集
- 「業界のトレンドをTwitterで調べて」→ 最新の話題を把握

設定が必要: Twitter Cookie の設定（Recustepがセットアップ代行）

### 4. GitHub

```bash
# リポジトリの情報を取得
gh repo view owner/repo

# Issue/PRを読む
gh issue list -R owner/repo
```

使い方:
- 「このGitHubリポジトリを評価して」→ Stars、Issue数、最終更新日等
- 「競合のOSSを調べて」→ リポジトリの比較

### 5. 任意のWebページ

```bash
# Jina ReaderでWebページをMarkdownに変換
curl -s "https://r.jina.ai/https://target-url.com"
```

使い方: 「この記事の内容を教えて」→ URLからテキスト抽出して要約

## 戦略エージェントとの連携

戦略エージェントが競合調査・市場分析を行う際に、このスキルを使って実データを取得する。

### 競合調査の流れ

1. Web検索で競合企業の最新ニュースを取得
2. 競合のWebサイトをJina Readerで読んで事業内容を把握
3. TwitterやSNSでの評判を収集
4. GitHubで技術力を評価（テック企業の場合）
5. 収集した情報を基に3C分析・SWOT分析を実行

### 市場分析の流れ

1. 業界キーワードでWeb検索
2. 業界レポートや統計情報を取得
3. YouTube上の業界解説動画を要約
4. SNS上の消費者の声を収集
5. 情報を統合してPEST分析・市場規模推定

## 注意事項

- Web検索の結果は最新だが、正確性は保証されない。重要な数字は一次ソースを確認
- Twitter/SNSの情報はバイアスがある。定量データと組み合わせること
- 有料記事・ログイン必須のサイトは読めない場合がある
- 情報収集した結果はGBrainに保存して蓄積すること
