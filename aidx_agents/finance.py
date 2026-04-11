"""財務エージェント - CFOの補佐"""

from __future__ import annotations

import json
from pathlib import Path

from .base import BaseAgent

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "financial"


class FinanceAgent(BaseAgent):
    """財務エージェント - PL/BS/CF分析、KPIモニタリング、資金繰り予測"""

    name = "財務エージェント"
    description = "CFO補佐：財務分析・KPIモニタリング・資金繰り予測"
    icon = "💰"

    def system_prompt(self) -> str:
        return """あなたはAIDX経営エージェントシステムの財務エージェントです。
CFO（最高財務責任者）の補佐として、経営者の財務判断をサポートします。

## 人格
- 数字に厳密で、根拠のない推測をしない
- リスクに敏感で、早期警告を心がける
- 経営者目線で要点を伝える（専門用語は必ず説明を添える）

## 専門領域
1. **PL（損益計算書）分析** — 売上・原価・販管費・営業利益の構造分析
2. **BS（貸借対照表）分析** — 資産構成・負債比率・自己資本比率
3. **CF（キャッシュフロー計算書）分析** — 営業CF・投資CF・財務CF
4. **KPIモニタリング** — 予算vs実績の差異分析、トレンド把握
5. **資金繰り予測** — 今後3-6ヶ月のキャッシュフロー予測
6. **投資対効果分析** — ROI計算、回収期間の試算

## 出力ルール
- 数値には必ず単位を付ける（円、%、倍など）
- 前年比・前月比がある場合は必ず比較する
- 良い数字・悪い数字を明確に区別する
- 「要注意」「改善必要」「良好」などの評価を付ける
- 最後に必ず「推奨アクション」を提示する

## データ参照
ユーザーがExcel/CSVファイルを提供した場合、そのデータを基に分析します。
data/financial/ ディレクトリにファイルが配置されます。

## 免責
投資助言や税務アドバイスは行いません。最終判断は税理士・公認会計士に確認することを推奨してください。
"""

    def analyze_file(self, file_path: str | Path) -> str:
        """Excelファイルを読み込んで分析結果を返す"""
        from tools.excel_reader import read_excel, read_csv

        path = Path(file_path)
        if path.suffix in (".xlsx", ".xls"):
            data = read_excel(path)
        elif path.suffix == ".csv":
            data = read_csv(path)
        else:
            return f"未対応のファイル形式です: {path.suffix}"

        prompt = (
            f"以下のデータを財務分析してください。\n\n"
            f"ファイル: {data['filename']}\n"
            f"カラム: {', '.join(data['columns'])}\n"
            f"行数: {data['rows']}\n\n"
            f"基本統計量:\n{json.dumps(data['summary'], ensure_ascii=False, indent=2)}\n\n"
            f"データ（先頭20行）:\n{json.dumps(data['data'][:20], ensure_ascii=False, indent=2)}"
        )

        return self.ask(prompt)

    def list_data_files(self) -> list[Path]:
        """data/financial/ 内のファイル一覧を返す"""
        if not _DATA_DIR.exists():
            return []
        return sorted(
            p for p in _DATA_DIR.iterdir()
            if p.suffix in (".xlsx", ".xls", ".csv") and not p.name.startswith(".")
        )
