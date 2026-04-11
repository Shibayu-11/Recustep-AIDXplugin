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
| **Supabase** | データベース（Postgres + pgvector） | $25/月 |
| **OpenAI APIキー** | ベクトル検索用のembedding生成 | $4-5/初回、以降微量 |
| **Bun** | GBrainの実行環境 | 無料 |

> 合計: 月額約$25（約3,700円）で社内の全ナレッジを検索可能に。

---

## セットアップ手順

### Step 1: Bunをインストール

```bash
# Mac
curl -fsSL https://bun.sh/install | bash

# Windows (PowerShell)
powershell -c "irm bun.sh/install.ps1 | iex"
```

### Step 2: Supabaseプロジェクトを作成

1. https://supabase.com/ にアクセスしてアカウント作成
2. 「New Project」をクリック
3. プロジェクト名: `aidx-brain` など任意
4. パスワードを設定（メモしておく）
5. リージョン: `Northeast Asia (Tokyo)` を選択
6. 作成完了まで約2分待つ

### Step 3: 接続文字列を取得

1. Supabaseダッシュボード → 「Settings」→「Database」
2. 「Connection string」→「URI」タブ
3. **Shared Pooler**（Session mode、ポート6543）の接続文字列をコピー
4. `[YOUR-PASSWORD]` を Step 2 で設定したパスワードに置き換え

### Step 4: GBrainを初期化

```bash
cd gbrain

# 依存パッケージをインストール
bun install

# データベースを初期化
bun run src/cli.ts init --non-interactive --url "YOUR_CONNECTION_STRING"
```

### Step 5: OpenAI APIキーを設定

```bash
# .envに追加（gbrain/ディレクトリ内）
echo 'OPENAI_API_KEY=sk-xxxxxxxx' >> .env
echo 'DATABASE_URL=YOUR_CONNECTION_STRING' >> .env
```

### Step 6: Claude CodeにMCP接続

```bash
# 認証トークンを生成
bun run src/commands/auth.ts create "aidx-agent"

# Claude CodeにGBrainを追加（ローカルMCP）
claude mcp add gbrain -- bun run src/mcp/server.ts
```

または `~/.claude.json` に手動追加：

```json
{
  "mcpServers": {
    "gbrain": {
      "command": "bun",
      "args": ["run", "./gbrain/src/mcp/server.ts"],
      "env": {
        "DATABASE_URL": "YOUR_CONNECTION_STRING",
        "OPENAI_API_KEY": "YOUR_OPENAI_KEY"
      }
    }
  }
}
```

### Step 7: ブレインリポジトリを初期化

```bash
# テンプレートからブレインを作成
cp -r brain-template/ brain/
cd brain
git init
git add -A
git commit -m "Initial brain setup"
```

### Step 8: 動作確認

Claude Codeを起動して：

```
社長 > 株式会社サンプルの情報を登録して。
       大阪の製造業、従業員120名、年商10億円。
       担当は田中太郎社長。
```

エージェントがGBrainに自動で保存します。次に：

```
社長 > 株式会社サンプルについて教えて
```

保存した情報が返ってくれば成功です。

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

---

## GBrainの仕組み

### 二層構造ページ

各ページは「上半分」と「下半分」に分かれます：

- **上半分（コンパイルされた真実）**: 最新の状態。新情報が入ったら上書き
- **下半分（タイムライン）**: 時系列の事実記録。追記のみ、削除しない

### ハイブリッド検索

- **キーワード検索**: 「田中社長」「NDA契約」等の固有名詞
- **ベクトル検索**: 「最近の売上が好調な取引先」等の意味検索
- 両方を組み合わせて最適な結果を返す

### エージェントが自動でやること

1. 会議後 → 関連する人・会社のページを自動更新
2. 分析完了 → 結果をanalysesに保存、関連企業ページにリンク
3. 契約レビュー → 要約をcontractsに保存、リスク項目をタイムラインに追記

---

## トラブルシューティング

### `gbrain init` でエラーが出る

- 接続文字列のパスワードが正しいか確認
- Supabaseのプロジェクトが「Active」状態か確認
- ポート番号が `6543`（Shared Pooler）になっているか確認

### 検索結果が返らない

- `gbrain sync` を実行してインデックスを更新
- OpenAI APIキーが有効か確認

### Bunが見つからない

```bash
source ~/.bashrc  # または ~/.zshrc
bun --version
```

---

## セキュリティに関する注意

- Supabaseのデータベースパスワードは厳重に管理してください
- GBrainに保存されるデータはSupabaseの暗号化されたストレージに格納されます
- オンプレミス要件がある場合は、ローカルPostgres + pgvectorでも動作可能です（`gbrain-local` MCP設定を使用）
