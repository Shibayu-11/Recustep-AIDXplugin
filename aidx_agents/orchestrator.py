"""オーケストレーター（司令塔） - 指示を解析して専門エージェントに振り分ける"""

from __future__ import annotations

from .base import BaseAgent

# 振り分けキーワードマッピング
_ROUTING_KEYWORDS: dict[str, list[str]] = {
    "finance": [
        "売上", "利益", "コスト", "予算", "PL", "BS", "CF", "資金繰り",
        "KPI", "財務", "経費", "決算", "キャッシュフロー", "損益",
        "貸借", "収支", "投資", "ROI", "原価", "粗利", "営業利益",
    ],
    "legal": [
        "契約", "規約", "コンプライアンス", "NDA", "法律", "訴訟",
        "法務", "免責", "賠償", "知的財産", "特許", "商標", "秘密保持",
        "業務委託", "利用規約", "個人情報", "GDPR",
    ],
    "hr": [
        "採用", "退職", "給与", "残業", "就業規則", "評価", "人事",
        "労務", "36協定", "有給", "社会保険", "雇用", "解雇", "休職",
        "勤怠", "賞与", "昇給", "研修", "オンボーディング",
    ],
    "secretary": [
        "議事録", "メール", "スケジュール", "報告書", "提案書", "ToDo",
        "秘書", "会議", "アジェンダ", "日程", "調整", "連絡", "案内",
        "お礼", "挨拶", "文書", "レター",
    ],
    "strategy": [
        "戦略", "事業計画", "SWOT", "競合", "市場", "新規事業",
        "KPI設計", "OKR", "ビジョン", "ミッション", "3C", "PEST",
        "ポジショニング", "差別化", "ターゲット", "セグメント",
        "ビジネスモデル", "スケール",
    ],
}


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
2. 要点を先に — 結論から述べ、詳細は後に続ける
3. アクション提示 — 分析結果には必ず「次に何をすべきか」を添える
4. 誠実さ — 分からないことは正直に伝え、専門家への相談を推奨する

## 応答フォーマット
経営者への報告は以下の形式で行ってください：

### 📋 要約
[1-2文で結論を述べる]

### 📊 詳細
[分析結果や提案内容]

### ✅ 推奨アクション
[具体的な次のステップを箇条書きで]
"""

    def classify(self, message: str) -> list[str]:
        """メッセージを解析して、振り分け先のエージェント名リストを返す"""
        scores: dict[str, int] = {key: 0 for key in _ROUTING_KEYWORDS}

        for agent_key, keywords in _ROUTING_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in message.lower():
                    scores[agent_key] += 1

        matched = [k for k, v in scores.items() if v > 0]

        if not matched:
            return []

        # スコア順にソート
        matched.sort(key=lambda k: scores[k], reverse=True)
        return matched

    def route(self, message: str) -> str:
        """メッセージを適切なエージェントにルーティングして結果を返す"""
        targets = self.classify(message)

        if not targets:
            # どのエージェントにも該当しない場合は自身が汎用アシスタントとして回答
            return self.ask(message)

        if len(targets) == 1 and targets[0] in self.agents:
            # 単一エージェントに振り分け
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
            # オーケストレーター自身が統合レポートを作成
            summary_prompt = (
                f"以下は各専門エージェントの分析結果です。"
                f"経営者向けに統合レポートとしてまとめてください。\n\n{combined}"
            )
            return self.ask(summary_prompt)

        return self.ask(message)
