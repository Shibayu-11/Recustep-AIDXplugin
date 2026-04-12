# AIDX 経営エージェントシステム

**GitHubをクローンして、APIキーを貼るだけ。5人のAI部下チームが即日稼働する。**

---

## これは何か

中小〜中堅企業の経営者に向けた、AIによる経営支援システムです。

| AI部下 | 役割 |
|--------|------|
|  財務エージェント | PL/BS/CF分析、KPIモニタリング、資金繰り予測 |
|  法務エージェント | 契約書リスク分析、コンプライアンスチェック |
|  労務エージェント | 就業規則Q&A、残業管理、採用・評価制度設計 |
|  秘書エージェント | 議事録作成、メール・提案書・報告書作成 |
|  戦略エージェント | SWOT/3C/PEST分析、事業計画、競合調査 |

オーケストレーター（司令塔）があなたの指示を解析し、最適なエージェントに自動で振り分けます。

---

## セットアップ（5分）

### 前提条件

- [Claude Max プラン](https://claude.ai/)（$200/月推奨 — 使い放題）
- Git

### 手順

```bash
# 1. クローン
git clone https://github.com/Shibayu-11/Recustep-AIDXplugin.git
cd Recustep-AIDXplugin

# 2. Claude Codeを起動
claude
```

これだけ。CLAUDE.mdを自動で読み込むので、起動した瞬間から5人のAI部下が使えます。

```
> 今月の売上を分析して
→ 財務エージェントが自動で対応
```

詳しい手順は [セットアップガイド](docs/ja-JP/SETUP-GUIDE.md) を参照。

---

## 使い方

### 財務分析

`data/financial/` にExcel/CSVを置いて：

```
社長 > data/financial/202603_PL.xlsx を分析して
```

### 契約書レビュー

`data/contracts/` にPDFを置いて：

```
社長 > data/contracts/業務委託契約書.pdf をチェックして
```

### 議事録作成

```
社長 > 今日の経営会議の議事録を作って。参加者は田中、佐藤、鈴木。
       議題は新規事業の予算承認。結論は2,000万円で承認。
       佐藤が来週末までに事業計画書の最終版を作成する。
```

### 戦略分析

```
社長 > うちの会社のSWOT分析をして。
       製造業、従業員50人、売上10億円、
       強みは技術力、弱みは営業力。
```

---

## あなたが触るフォルダ

**3つだけ覚えてください。残りは全部システムが使います。**

```
data/
├── financial/    ← Excelや CSVを置くだけで財務分析が動く
├── contracts/    ← 契約書PDFを置くだけで法務チェックが動く
└── knowledge/    ← 社内マニュアルや規程を置くと記憶に使われる

.env              ← APIキー設定（最初に一度だけ）
```

他のフォルダ（`aidx_agents/`, `tools/`, `templates/`, `skills/` 等）は
**システム内部なので触らないでください。**

詳細は [フォルダガイド](docs/ja-JP/FOLDER-GUIDE.md) を参照してください。

---

## セキュリティ

- **APIキー**: `.env` で管理。Gitにはコミットされません
- **機密データ**: `data/` はGit管理対象外。財務・契約・人事データはローカルに留まります
- **API通信**: Claude APIへの送信のみ。データ本体ではなく質問・要約を送信
- 詳細は [rules/business/confidentiality.md](rules/business/confidentiality.md)

---

## 内蔵リソース

Claude Code利用時には access to 47 agents, 196 skills, and 79 legacy command shims が利用可能です。

| カテゴリ | 数 |
|---------|-----|
| **Agents** | 47 agents |
| **Skills** | 196 skills |
| **Commands** | 79 commands |

---

## 技術スタック

| レイヤー | 技術 |
|---------|------|
| コアエンジン | Anthropic Claude API (claude-sonnet) |
| 言語 | Python 3.9+ |
| データ処理 | pandas, openpyxl, pdfplumber |
| 出力 | Jinja2 (HTML/CSS), Rich (CLI) |
| PDF解析 | OpenDataLoader PDF (精度0.907) |

---

## ロードマップ

- [x] Phase 1: CLAUDE.md + リポジトリ構造
- [x] Phase 2: 5エージェント + オーケストレーター (Python)
- [x] Phase 3: ビジネスルール・スキル・HTMLテンプレート
- [ ] Phase 4: MCP連携（Gmail, Google Calendar, Slack）
- [ ] Phase 5: ChromaDB / RAG（社内記憶）
- [ ] Phase 6: WebUI（React / Vite）

---

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照

---

*Developed by [Recustep](https://github.com/Shibayu-11) — Powered by Anthropic Claude API*
