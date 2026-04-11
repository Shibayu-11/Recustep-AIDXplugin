"""法務エージェント - 顧問弁護士の補佐"""

from __future__ import annotations

from pathlib import Path

from .base import BaseAgent

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "contracts"


class LegalAgent(BaseAgent):
    """法務エージェント - 契約書レビュー、コンプライアンスチェック"""

    name = "法務エージェント"
    description = "顧問弁護士補佐：契約書リスク分析・コンプライアンスチェック"
    icon = "⚖️"

    def system_prompt(self) -> str:
        return """あなたはAIDX経営エージェントシステムの法務エージェントです。
顧問弁護士の補佐として、経営者の法務判断をサポートします。

## 人格
- 慎重で、リスクを見逃さない
- 平易な言葉で法的リスクを説明する（法律用語には必ず補足説明を添える）
- 最悪のケースを想定しつつ、実務的な落としどころも提示する

## 専門領域
1. **契約書レビュー** — リスク箇所の抽出、不利な条項の特定
2. **条項解釈** — 各条項の意味と影響の説明
3. **修正提案** — より有利な文言への修正案を提示
4. **雛形作成** — NDA、業務委託契約書等の雛形ドラフト
5. **コンプライアンスチェック** — 法令遵守状況の確認

## 出力ルール
- リスクレベルを明示する（🔴 高リスク / 🟡 中リスク / 🟢 低リスク）
- 該当する法令名・条文を可能な限り引用する
- 「こうすべき」ではなく「こういうリスクがある」という表現を使う
- 必ず「弁護士に確認すべき事項」を最後に列挙する

## 重要な免責事項
このエージェントは法的助言を行うものではありません。
分析結果は参考情報であり、最終判断は必ず弁護士に確認してください。
この注意書きは全ての回答の末尾に必ず記載してください。
"""

    def review_contract(self, file_path: str | Path) -> str:
        """契約書PDFを読み込んでリスク分析を行う"""
        from tools.pdf_reader import read_pdf

        data = read_pdf(file_path)
        prompt = (
            f"以下の契約書を法務レビューしてください。\n\n"
            f"ファイル: {data['filename']}（全{data['total_pages']}ページ）\n\n"
            f"--- 契約書本文 ---\n{data['full_text']}"
        )
        return self.ask(prompt)

    def list_data_files(self) -> list[Path]:
        """data/contracts/ 内のファイル一覧を返す"""
        if not _DATA_DIR.exists():
            return []
        return sorted(
            p for p in _DATA_DIR.iterdir()
            if p.suffix == ".pdf" and not p.name.startswith(".")
        )
