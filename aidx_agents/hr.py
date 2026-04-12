"""労務エージェント - 社労士の補佐 + 勤怠管理 + 採用支援"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .base import BaseAgent

# 退職手続きチェックリスト
_RESIGNATION_CHECKLIST = [
    {"step": "退職届の受理", "deadline": "退職日の14日前まで", "note": "就業規則に別途定めがあればそちらに従う"},
    {"step": "業務引継ぎ計画の作成", "deadline": "退職日の2週間前", "note": "引継ぎ先の担当者を決定"},
    {"step": "社会保険の資格喪失届", "deadline": "退職日の翌日から5日以内", "note": "年金事務所に届出"},
    {"step": "雇用保険の資格喪失届", "deadline": "退職日の翌日から10日以内", "note": "ハローワークに届出"},
    {"step": "離職票の交付", "deadline": "退職日の翌日から10日以内", "note": "本人が希望する場合（59歳以上は必須）"},
    {"step": "源泉徴収票の交付", "deadline": "退職日から1ヶ月以内", "note": "年の途中で退職する場合"},
    {"step": "住民税の異動届", "deadline": "退職日の翌月10日まで", "note": "市区町村に届出"},
    {"step": "会社備品の返却", "deadline": "退職日まで", "note": "PC、カードキー、制服等"},
    {"step": "最終給与・退職金の精算", "deadline": "就業規則に従う", "note": "未消化有給の買取は任意"},
]


class HRAgent(BaseAgent):
    """労務エージェント - 就業規則、勤怠管理、採用、評価、給与計算"""

    name = "労務エージェント"
    description = "社労士補佐：就業規則・勤怠管理・採用・評価・給与・事業承継"
    icon = "H"

    def system_prompt(self) -> str:
        return """あなたはAIDX経営エージェントシステムの労務エージェントです。
社会保険労務士の補佐として、経営者の人事・労務判断をサポートします。

## 人格
- 法令遵守に厳格。違反は絶対に見逃さない
- 従業員の権利を守りつつ、経営者のコスト意識も理解する
- 「義務」と「努力義務」を明確に分ける
- 違反した場合の罰則・リスクを必ず伝える
- 数字で話す（「社保料は年収の約30%」等）

## 専門領域

### 1. 就業規則
- Q&A・解釈サポート
- 必須記載事項のチェック（労基法89条）
- 改定案の作成
- 法改正への対応確認

### 2. 勤怠管理・36協定
- 残業時間のチェック（月45時間/年360時間の上限）
- 特別条項の適用確認（年6回まで/月100時間未満/複数月平均80時間以内）
- 有給休暇の取得状況確認（年5日の取得義務）
- 変形労働時間制の適用判断

### 3. 採用
- 求人票作成（職業安定法に基づく必須記載事項）
- 採用要件定義
- 面接評価シート作成
- 内定通知書・雇用契約書のたたき台

### 4. 評価制度
- 等級制度設計（職能等級/職務等級/役割等級）
- 評価項目設計（成果/能力/行動）
- MBO（目標管理制度）/ OKR の設計
- 昇給テーブル・賞与算定基準

### 5. 給与・社会保険（正確計算）
- tools/insurance_calculator.py を使って1円単位で計算
- 標準報酬月額等級表（50等級）に基づく正確な保険料
- 都道府県別の健康保険料率
- 厚生年金の上限（650,000円）適用
- 介護保険（40歳以上）の自動判定
- 雇用保険・労災保険（業種別料率）
- 所得税（速算表）・住民税の概算
- 手取り額の算出
- 総人件費（会社負担総額）の算出

### 6. 退職・解雇
- 退職手続きチェックリスト
- 解雇の4要件（整理解雇）
- 退職金の相場と計算方法
- 競業避止義務の有効性

### 7. ハラスメント対策
- パワハラ・セクハラの定義と6類型
- 相談窓口の設計
- 研修内容の提案
- 事後対応フロー

### 8. 事業承継（労務面）
- 従業員への説明・同意取得
- 雇用条件の維持義務
- 退職金の承継処理

## 出力ルール
- 根拠法令を必ず引用（例: 労働基準法第36条第4項）
- 「義務」は「しなければならない」、「努力義務」は「するよう努めなければならない」と明記
- 違反時の罰則を必ず記載（例: 6ヶ月以下の懲役又は30万円以下の罰金）
- 金額は具体的な数字で（「年収600万円の場合、社会保険料は約180万円/年」）

## 残業チェック出力フォーマット

```
## 残業時間チェック結果

### 36協定超過者（要対応）
| 社員名 | 今月残業 | 36協定上限 | 超過時間 | リスク |
|--------|---------|-----------|---------|-------|
| 田中 | 52h | 45h | 7h超過 | 労基法違反 |

### 注意レベル（40h以上）
| 社員名 | 今月残業 | 残り枠 |
|--------|---------|--------|
| 佐藤 | 42h | あと3h |

### 有給取得状況
| 社員名 | 付与日数 | 取得済み | 年5日義務まで |
|--------|---------|---------|-------------|
| 鈴木 | 20日 | 2日 | あと3日必要（期限: X月） |
```

## 免責事項（必ず全回答に記載）
本エージェントは社会保険労務士業務を代行するものではありません。
最終判断は必ず社会保険労務士または弁護士にご確認ください。
"""

    def calculate_labor_cost(
        self,
        annual_salary: int,
        age: int = 35,
        prefecture: str = "東京",
        industry: str = "事務",
        dependents: int = 0,
    ) -> str:
        """年収から総人件費を1円単位で正確に計算する"""
        from tools.insurance_calculator import calculate_insurance

        result = calculate_insurance(
            annual_salary=annual_salary,
            age=age,
            prefecture=prefecture,
            industry=industry,
            dependents=dependents,
        )
        return result.summary()

    def check_overtime(self, overtime_data: list[dict]) -> dict:
        """残業時間をチェックして36協定違反を検出する

        Args:
            overtime_data: [{"name": "田中", "hours": 52}, ...]

        Returns:
            {"violations": [...], "warnings": [...], "safe": [...]}
        """
        result = {"violations": [], "warnings": [], "safe": []}

        for emp in overtime_data:
            name = emp.get("name", "不明")
            hours = emp.get("hours", 0)

            if hours > 45:
                result["violations"].append({
                    "name": name,
                    "hours": hours,
                    "over": hours - 45,
                    "risk": "36協定上限（月45時間）超過。労基法違反の可能性",
                })
            elif hours >= 40:
                result["warnings"].append({
                    "name": name,
                    "hours": hours,
                    "remaining": 45 - hours,
                })
            else:
                result["safe"].append({"name": name, "hours": hours})

        return result

    def check_paid_leave(self, leave_data: list[dict]) -> dict:
        """有給取得状況をチェックする

        Args:
            leave_data: [{"name": "田中", "granted": 20, "taken": 2, "deadline": "2026-09-30"}, ...]

        Returns:
            {"violations": [...], "warnings": [...], "ok": [...]}
        """
        result = {"violations": [], "warnings": [], "ok": []}
        today = datetime.now().date()

        for emp in leave_data:
            name = emp.get("name", "不明")
            granted = emp.get("granted", 10)
            taken = emp.get("taken", 0)
            remaining_required = max(0, 5 - taken)

            if granted >= 10 and taken < 5:
                deadline = emp.get("deadline", "")
                try:
                    dl = datetime.strptime(deadline, "%Y-%m-%d").date()
                    days_left = (dl - today).days
                except (ValueError, TypeError):
                    days_left = -1

                if days_left < 30:
                    result["violations"].append({
                        "name": name,
                        "taken": taken,
                        "remaining_required": remaining_required,
                        "deadline": deadline,
                        "urgency": "期限間近" if days_left > 0 else "期限超過",
                    })
                else:
                    result["warnings"].append({
                        "name": name,
                        "taken": taken,
                        "remaining_required": remaining_required,
                        "deadline": deadline,
                    })
            else:
                result["ok"].append({"name": name, "taken": taken})

        return result

    def get_resignation_checklist(self) -> list[dict]:
        """退職手続きチェックリストを返す"""
        return _RESIGNATION_CHECKLIST

    def generate_job_posting(self, context: str) -> str:
        """求人票のたたき台を生成する"""
        prompt = (
            "以下の情報を基に求人票を作成してください。\n"
            "職業安定法に基づく必須記載事項を必ず含めてください:\n"
            "- 業務内容、契約期間、就業場所、就業時間・休日、賃金、社会保険の有無\n"
            "- 試用期間の有無と条件\n"
            "- 受動喫煙防止措置の状況\n\n"
            f"--- 情報 ---\n{context}"
        )
        return self.ask(prompt)

    def generate_interview_sheet(self, context: str) -> str:
        """面接評価シートを生成する"""
        prompt = (
            "以下の職種・要件に基づいて面接評価シートを作成してください。\n"
            "含めるもの:\n"
            "- 質問リスト（10問、行動面接法ベース）\n"
            "- 各質問の評価基準（1-5点）\n"
            "- 見るべきポイント\n"
            "- 不適切な質問の注意事項（本籍地、家族構成等は聞いてはいけない）\n\n"
            f"--- 職種・要件 ---\n{context}"
        )
        return self.ask(prompt)

    def design_evaluation_system(self, context: str) -> str:
        """評価制度を設計する"""
        prompt = (
            "以下の企業情報に基づいて人事評価制度を設計してください。\n"
            "含めるもの:\n"
            "- 等級制度（何段階、各等級の定義）\n"
            "- 評価項目（成果/能力/行動の3軸）\n"
            "- 評価サイクル（半期/年次）\n"
            "- 昇給・賞与との連動方法\n"
            "- 評価面談の進め方\n\n"
            f"--- 企業情報 ---\n{context}"
        )
        return self.ask(prompt)

    def simulate_hiring_cost(
        self,
        annual_salary: int,
        age: int = 30,
        prefecture: str = "東京",
        industry: str = "事務",
    ) -> str:
        """採用した場合の初年度総コストを正確に試算する"""
        from tools.insurance_calculator import calculate_insurance

        result = calculate_insurance(
            annual_salary=annual_salary,
            age=age,
            prefecture=prefecture,
            industry=industry,
        )

        recruitment_cost = int(annual_salary * 0.3)
        training_cost = 500000
        equipment_cost = 300000
        first_year_total = result.total_labor_cost_annual + recruitment_cost + training_cost + equipment_cost

        prompt = (
            f"以下の採用コスト試算結果を経営者に分かりやすく報告してください。\n\n"
            f"{result.summary()}\n\n"
            f"### 採用関連費用（初年度のみ）\n"
            f"| 項目 | 金額 |\n"
            f"|------|------|\n"
            f"| 採用費（エージェント30%） | {recruitment_cost:,}円 |\n"
            f"| 研修費 | {training_cost:,}円 |\n"
            f"| PC・備品 | {equipment_cost:,}円 |\n"
            f"| **初年度総コスト** | **{first_year_total:,}円** |\n\n"
            f"「年収{annual_salary/10000:.0f}万円の人を1人採用すると、会社は初年度{first_year_total/10000:.0f}万円かかる」と伝えてください。"
        )
        return self.ask(prompt)
