# GBrain 社内記憶システム セットアップガイド

GBrainは、AIDXエージェントに「記憶」を与えるナレッジベースシステムです。
取引先情報、会議記録、分析結果を自動で蓄積し、使うほどエージェントが賢くなります。

---

## GBrainとは

通常のAIは毎回記憶がリセットされます。GBrainを導入すると：

| GBrainなし | GBrainあり |
|-----------|-----------|
| 「A社って誰？」→ 毎回説明が必要 | 「A社って誰？」→ 過去の取引履歴含めて即答 |
| 先月の分析結果を覚えていない | 先月の分析と比較して報告 |
| 会議の内容が消える | 全会議を横断検索、関連情報を自動リンク |

---

## 必要なもの

| 項目 | 説明 | コスト |
|------|------|--------|
| **Docker** | ローカルPostgresの実行環境 | 無料 |
| **OpenAI APIキー** | ベクトル検索用のembedding生成 | 初回$4-5、以降微量 |
| **Bun** | GBrainの実行環境 | 無料 |

> 完全ローカル構成: **月額コストほぼゼロ**（OpenAI embedding費用のみ、月数百円程度）。
> データは一切外部に出ません。

---

## セットアップ手順

### Step 1: Dockerをインストール

- Mac: https://docs.docker.com/desktop/install/mac-install/
- Windows: https://docs.docker.com/desktop/install/windows-install/
- Linux: https://docs.docker.com/engine/install/

インストール後、Docker Desktopを起動してください。

### Step 2: ローカルPostgres + pgvectorを起動

```bash
docker run -d \
  --name aidx-brain \
  -e POSTGRES_USER=aidx \
  -e POSTGRES_PASSWORD=aidx_secure_password \
  -e POSTGRES_DB=aidx_brain \
  -p 5432:5432 \
  --restart unless-stopped \
  pgvector/pgvector:pg16
```

起動確認：

```bash
docker exec aidx-brain pg_isready -U aidx
# 「accepting connections」と表示されればOK
```

> `--restart unless-stopped` により、PC再起動後も自動で立ち上がります。

### Step 3: Bunをインストール

```bash
# Mac / Linux
curl -fsSL https://bun.sh/install | bash

# Windows (PowerShell)
powershell -c "irm bun.sh/install.ps1 | iex"
```

### Step 4: GBrainをセットアップ

```bash
cd gbrain

# 依存パッケージをインストール
bun install

# .envを作成
cat > .env << 'EOF'
DATABASE_URL=postgresql://aidx:aidx_secure_password@localhost:5432/aidx_brain
OPENAI_API_KEY=sk-xxxxxxxx
EOF

# データベースを初期化
bun run src/cli.ts init --non-interactive --url "postgresql://aidx:aidx_secure_password@localhost:5432/aidx_brain"
```

### Step 5: Claude CodeにMCP接続

```bash
claude mcp add gbrain -- bun run ./gbrain/src/mcp/server.ts
```

または `~/.claude.json` に手動追加：

```json
{
  "mcpServers": {
    "gbrain": {
      "command": "bun",
      "args": ["run", "./gbrain/src/mcp/server.ts"],
      "env": {
        "DATABASE_URL": "postgresql://aidx:aidx_secure_password@localhost:5432/aidx_brain",
        "OPENAI_API_KEY": "sk-xxxxxxxx"
      }
    }
  }
}
```

### Step 6: ブレインリポジトリを初期化

```bash
cp -r brain-template/ brain/
cd brain
git init
git add -A
git commit -m "Initial brain setup"
```

### Step 7: 動作確認

Claude Codeを起動して：

```
社長 > 株式会社サンプルの情報を登録して。
       大阪の製造業、従業員120名、年商10億円。
       担当は田中太郎社長。
```

次に：

```
社長 > 株式会社サンプルについて教えて
```

保存した情報が返ってくれば成功です。

---

## なぜローカルPostgresなのか

| | ローカルPostgres | クラウド（Supabase等） |
|---|---|---|
| **セキュリティ** | データは完全にPC内 | クラウドサーバーに保存 |
| **検索速度** | 即レス（ネットワーク遅延ゼロ） | 数十msの遅延あり |
| **コスト** | 無料 | $25/月〜 |
| **データ量** | ディスク容量次第 | プランで上限あり |
| **可用性** | PC起動中のみ | 24時間 |

AIDXは「情報漏洩ゼロ」を掲げています。機密性の高い経営データをクラウドに出さないために、ローカルPostgresを標準構成としています。

---

## AIDX用ブレインスキーマ

`brain-template/` にテンプレートを用意しています。

| ディレクトリ | 用途 | 使うエージェント |
|------------|------|-----------------|
| `clients/` | 顧客・取引先情報 | 全員 |
| `companies/` | 競合・パートナー企業 | 戦略 |
| `meetings/` | 会議記録・議事録 | 秘書 |
| `analyses/` | 財務分析・市場分析結果 | 財務・戦略 |
| `contracts/` | 契約レビューの要約 | 法務 |
| `employees/` | 社員情報・評価記録 | 労務 |
| `projects/` | 進行中プロジェクト | 全員 |
| `org/` | 経営方針・社内規程 | 全員 |
| `inbox/` | 未整理の情報 | 秘書 |

### ページの書き方（二層構造）

#### 上半分：コンパイルされた真実（最新の状態）
新しい情報が入ったら上書き更新。常に「今の正確な状態」を反映。

#### 下半分：タイムライン（追記のみ）
時系列で事実を記録。絶対に編集・削除しない。証拠の積み重ね。

---

## データのバックアップ

ローカルPostgresのバックアップは定期的に行ってください。

```bash
# バックアップ（週1回推奨）
docker exec aidx-brain pg_dump -U aidx aidx_brain > backup_$(date +%Y%m%d).sql

# 復元（必要な場合）
docker exec -i aidx-brain psql -U aidx aidx_brain < backup_20260411.sql
```

brainリポジトリはGit管理されているので、`git push` で社内Gitサーバーにもバックアップできます。

---

## トラブルシューティング

### Dockerが起動しない
- Docker Desktopが起動しているか確認
- Macの場合、システム設定 → プライバシーとセキュリティで許可が必要な場合あり

### ポート5432が使用中
```bash
# 別のポートで起動
docker run -d --name aidx-brain \
  -e POSTGRES_USER=aidx \
  -e POSTGRES_PASSWORD=aidx_secure_password \
  -e POSTGRES_DB=aidx_brain \
  -p 5433:5432 \
  --restart unless-stopped \
  pgvector/pgvector:pg16
```
接続文字列のポートも `5433` に変更してください。

### 検索結果が返らない
- `bun run src/cli.ts sync` を実行してインデックスを更新
- OpenAI APIキーが有効か確認
- `docker ps` でPostgresコンテナが起動中か確認

### PCを再起動したらGBrainが動かない
```bash
# Dockerコンテナの状態を確認
docker ps -a

# 停止していたら起動
docker start aidx-brain
```

---

## エンタープライズ向け：社内サーバー構成

複数人で使う場合は、社内サーバーにPostgresを立てて共有できます。

```
┌──────────┐     ┌──────────┐     ┌───────────────┐
│ 社長PC   │────>│          │     │               │
│ (Claude) │     │  社内LAN │────>│ 社内サーバー    │
│          │     │          │     │ Postgres+      │
├──────────┤     │          │     │ pgvector       │
│ 部長PC   │────>│          │     │               │
│ (Claude) │     │          │     │ GBrain MCP     │
└──────────┘     └──────────┘     └───────────────┘
```

この構成ではTier 3（エンタープライズ）プランで対応します。
