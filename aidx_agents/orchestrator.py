"""オーケストレーター（司令塔） - 指示を解析して専門エージェントに振り分ける"""

from __future__ import annotations

import json

from .base import BaseAgent

# キーワードベースのフォールバック用マッピング
_ROUTING_KEYWORDS: dict[str, list[str]] = {
    "finance": [
        "売上", "利益", "コスト", "予算", "PL", "BS", "CF", "資金繰り",
        "KPI", "財務", "経費", "決算", "キャッシュフロー", "損益",
        "貸借", "収支", "投資", "ROI", "原価", "粗利", "営業利益",
        "見積", "請求", "融資", "借入", "銀行",
    ],
    "legal": [
        "契約", "規約", "コンプライアンス", "NDA", "法律", "訴訟",
        "法務", "免責", "賠償", "知的財産", "特許", "商標", "秘密保持",
        "業務委託", "利用規約", "個人情報", "GDPR",
    ],
    "hr": [
        "採用", "退職", "給与", "残業", "就業規則", "評価", "人事",
        "労務", "36協定", "有給", "社会保険", "雇用", "解雇", "休職",
        "勤怠", "賞与", "昇給", "研修", "オンボーディング", "事業承継",
        "後継者",
    ],
    "secretary": [
        "議事録", "メール", "スケジュール", "報告書", "提案書", "ToDo",
        "秘書", "会議", "アジェンダ", "日程", "調整", "連絡", "案内",
        "お礼", "挨拶", "文書", "レター", "月次レポート",
    ],
    "strategy": [
        "戦略", "事業計画", "SWOT", "競合", "市場", "新規事業",
        "KPI設計", "OKR", "ビジョン", "ミッション", "3C", "PEST",
        "ポジショニング", "差別化", "ターゲット", "セグメント",
        "ビジネスモデル", "スケール", "補助金", "助成金",
    ],
}

_CLASSIFY_PROMPT = """あなたは経営エージェントシステムの振り分け担当です。
経営者からのメッセージを分析し、どの専門エージェントに振り分けるべきか判断してください。

## 利用可能なエージェント
- finance: 財務エージェント（売上分析、PL/BS/CF、KPI、資金繰り、見積書、請求書、融資準備）
- legal: 法務エージェント（契約書レビュー、コンプライアンス、NDA、法的リスク）
- hr: 労務エージェント（就業規則、残業管理、採用、評価制度、給与、事業承継）
- secretary: 秘書エージェント（議事録、メール作成、提案書、報告書、スケジュール、月次レポート）
- strategy: 経営戦略エージェント（SWOT分析、事業計画、競合調査、市場分析、補助金・助成金）

## ルール
- 1つまたは複数のエージェントを選択できます
- 複数領域にまたがる場合は全て含めてください
- どれにも該当しない場合は空リストを返してください
- JSONのみを返してください。説明は不要です

## 出力形式
{"agents": ["finance", "legal"]}

## メッセージ
"""


class Orchestrator(BaseAgent):
    """オーケストレーター - 経営者の指示を解析して最適なエージェントに振り分ける"""

    name = "オーケストレーター"
    description = "司令塔：指示を解析して専門エージェントに振り分ける"
    icon = "🎯"

    def __init__(self, agents: dict[str, BaseAgent] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.agents = agents or {}

    def system_prompt(self) -> str:
        agent_list = "\n".join(
            f"- {a.icon} {a.name}: {a.description}" for a in self.agents.values()
        )
        return f"""あなたはAIDX経営エージェントシステムのオーケストレーター（司令塔）です。

## 役割
経営者からの指示を受け取り、内容を解析して最適な専門エージェントに振り分けます。
複数の領域にまたがる場合は、関連する全エージェントに依頼し、結果を統合して報告します。

## 利用可能なエージェント
{agent_list}

## 行動原則
1. 経営者ファースト — 技術用語を避け、経営判断に直結する情報を提供する
2. 結論から — 最初の1文で答えを言い切る
3. 数字で話す — 「大幅に増加」は禁止。「前月比+12%」と言え
4. アクション必須 — 分析で終わらない。「次に何をすべきか」を必ず提示する
5. 悪いニュースも直球 — 「御社の解約率は月8%。このままでは9ヶ月で顧客ゼロです」
6. 誠実さ — 分からないことは正直に伝え、専門家への相談を推奨する

## 応答フォーマット
### 📋 要約
[1-2文で結論を述べる]

### 📊 詳細
[分析結果や提案内容]

### ✅ 推奨アクション
[具体的な次のステップを箇条書きで]
"""

    def classify(self, message: str) -> list[str]:
        """メッセージをClaude APIで意図分類し、振り分け先を返す。
        API失敗時はキーワードマッチングにフォールバック。
        """
        try:
            return self._classify_with_ai(message)
        except Exception:
            return self._classify_with_keywords(message)

    def _classify_with_ai(self, message: str) -> list[str]:
        """Claude APIで意図分類する"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=100,
            system="JSONのみを返してください。説明は不要です。",
            messages=[{
                "role": "user",
                "content": _CLASSIFY_PROMPT + message,
            }],
        )

        text = response.content[0].text.strip()
        # JSON部分を抽出（余計なテキストがあっても対応）
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON found in response")

        data = json.loads(text[start:end])
        agents = data.get("agents", [])

        # 有効なエージェント名のみ返す
        valid = [a for a in agents if a in self.agents]
        return valid

    def _classify_with_keywords(self, message: str) -> list[str]:
        """キーワードマッチングで意図分類する（フォールバック）"""
        scores: dict[str, int] = {key: 0 for key in _ROUTING_KEYWORDS}

        for agent_key, keywords in _ROUTING_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in message.lower():
                    scores[agent_key] += 1

        matched = [k for k, v in scores.items() if v > 0]
        matched.sort(key=lambda k: scores[k], reverse=True)
        return matched

    def route(self, message: str) -> str:
        """メッセージを適切なエージェントにルーティングして結果を返す"""
        targets = self.classify(message)

        if not targets:
            return self.ask(message)

        if len(targets) == 1 and targets[0] in self.agents:
            agent = self.agents[targets[0]]
            return agent.ask(message)

        # 複数エージェントに振り分けて結果を統合
        results: list[str] = []
        for target in targets:
            if target in self.agents:
                agent = self.agents[target]
                result = agent.ask(message)
                results.append(f"## {agent.icon} {agent.name}の分析\n\n{result}")

        if results:
            combined = "\n\n---\n\n".join(results)
            summary_prompt = (
                f"以下は各専門エージェントの分析結果です。"
                f"経営者向けに統合レポートとしてまとめてください。"
                f"結論から述べ、数字を使い、次のアクションを必ず提示してください。\n\n{combined}"
            )
            return self.ask(summary_prompt)

        return self.ask(message)
