"""社会保険料・税金計算ツール

標準報酬月額に基づく正確な保険料計算。1円単位で計算。

料率の更新方法:
  FISCAL_YEAR を変更し、該当年度の料率を更新する。
  健康保険料率は毎年3月に改定（協会けんぽ）。
  厚生年金保険料率は2017年9月以降固定（18.3%）。
  雇用保険料率は毎年4月に改定。
  https://www.kyoukaikenpo.or.jp/
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# ═══════════════════════════════════════════════
# 年度設定（ここを変えれば全体に反映される）
# ═══════════════════════════════════════════════
FISCAL_YEAR = 2026  # 令和8年度

# ═══════════════════════════════════════════════
# 標準報酬月額等級表（厚生年金保険・健康保険共通）
# 1等級〜50等級（健康保険は50等級まで）
# 厚生年金は32等級（上限650,000円）まで
# ═══════════════════════════════════════════════

_STANDARD_MONTHLY_GRADES: list[dict] = [
    # {"grade": 等級, "monthly": 標準報酬月額, "lower": 報酬月額下限, "upper": 報酬月額上限}
    {"grade": 1, "monthly": 58000, "lower": 0, "upper": 63000},
    {"grade": 2, "monthly": 68000, "lower": 63000, "upper": 73000},
    {"grade": 3, "monthly": 78000, "lower": 73000, "upper": 83000},
    {"grade": 4, "monthly": 88000, "lower": 83000, "upper": 93000},
    {"grade": 5, "monthly": 98000, "lower": 93000, "upper": 101000},
    {"grade": 6, "monthly": 104000, "lower": 101000, "upper": 107000},
    {"grade": 7, "monthly": 110000, "lower": 107000, "upper": 114000},
    {"grade": 8, "monthly": 118000, "lower": 114000, "upper": 122000},
    {"grade": 9, "monthly": 126000, "lower": 122000, "upper": 130000},
    {"grade": 10, "monthly": 134000, "lower": 130000, "upper": 138000},
    {"grade": 11, "monthly": 142000, "lower": 138000, "upper": 146000},
    {"grade": 12, "monthly": 150000, "lower": 146000, "upper": 155000},
    {"grade": 13, "monthly": 160000, "lower": 155000, "upper": 165000},
    {"grade": 14, "monthly": 170000, "lower": 165000, "upper": 175000},
    {"grade": 15, "monthly": 180000, "lower": 175000, "upper": 185000},
    {"grade": 16, "monthly": 190000, "lower": 185000, "upper": 195000},
    {"grade": 17, "monthly": 200000, "lower": 195000, "upper": 210000},
    {"grade": 18, "monthly": 220000, "lower": 210000, "upper": 230000},
    {"grade": 19, "monthly": 240000, "lower": 230000, "upper": 250000},
    {"grade": 20, "monthly": 260000, "lower": 250000, "upper": 270000},
    {"grade": 21, "monthly": 280000, "lower": 270000, "upper": 290000},
    {"grade": 22, "monthly": 300000, "lower": 290000, "upper": 310000},
    {"grade": 23, "monthly": 320000, "lower": 310000, "upper": 330000},
    {"grade": 24, "monthly": 340000, "lower": 330000, "upper": 350000},
    {"grade": 25, "monthly": 360000, "lower": 350000, "upper": 370000},
    {"grade": 26, "monthly": 380000, "lower": 370000, "upper": 395000},
    {"grade": 27, "monthly": 410000, "lower": 395000, "upper": 425000},
    {"grade": 28, "monthly": 440000, "lower": 425000, "upper": 455000},
    {"grade": 29, "monthly": 470000, "lower": 455000, "upper": 485000},
    {"grade": 30, "monthly": 500000, "lower": 485000, "upper": 515000},
    {"grade": 31, "monthly": 530000, "lower": 515000, "upper": 545000},
    {"grade": 32, "monthly": 560000, "lower": 545000, "upper": 575000},
    {"grade": 33, "monthly": 590000, "lower": 575000, "upper": 605000},
    {"grade": 34, "monthly": 620000, "lower": 605000, "upper": 635000},
    {"grade": 35, "monthly": 650000, "lower": 635000, "upper": 665000},
    {"grade": 36, "monthly": 680000, "lower": 665000, "upper": 695000},
    {"grade": 37, "monthly": 710000, "lower": 695000, "upper": 730000},
    {"grade": 38, "monthly": 750000, "lower": 730000, "upper": 770000},
    {"grade": 39, "monthly": 790000, "lower": 770000, "upper": 810000},
    {"grade": 40, "monthly": 830000, "lower": 810000, "upper": 855000},
    {"grade": 41, "monthly": 880000, "lower": 855000, "upper": 905000},
    {"grade": 42, "monthly": 930000, "lower": 905000, "upper": 955000},
    {"grade": 43, "monthly": 980000, "lower": 955000, "upper": 1005000},
    {"grade": 44, "monthly": 1030000, "lower": 1005000, "upper": 1055000},
    {"grade": 45, "monthly": 1090000, "lower": 1055000, "upper": 1115000},
    {"grade": 46, "monthly": 1150000, "lower": 1115000, "upper": 1175000},
    {"grade": 47, "monthly": 1210000, "lower": 1175000, "upper": 1235000},
    {"grade": 48, "monthly": 1270000, "lower": 1235000, "upper": 1295000},
    {"grade": 49, "monthly": 1330000, "lower": 1295000, "upper": 1355000},
    {"grade": 50, "monthly": 1390000, "lower": 1355000, "upper": 999999999},
]

# 厚生年金の上限等級（32等級 = 650,000円）
_PENSION_MAX_GRADE = 35  # grade 35 = 650,000円

# ═══════════════════════════════════════════════
# 保険料率（2026年度・令和8年度）
# ═══════════════════════════════════════════════

# 都道府県別 協会けんぽ健康保険料率（%）
# 年度: {FISCAL_YEAR} — 毎年3月に改定。協会けんぽ公式サイトで確認
# https://www.kyoukaikenpo.or.jp/g7/cat330/sb3150/r06/r6ryougakuhyou3gatukara/
_HEALTH_INSURANCE_RATES: dict[str, float] = {
    "北海道": 10.29, "青森": 9.49, "岩手": 9.63, "宮城": 10.01, "秋田": 9.78,
    "山形": 9.68, "福島": 9.47, "茨城": 9.73, "栃木": 9.79, "群馬": 9.76,
    "埼玉": 9.78, "千葉": 9.75, "東京": 9.98, "神奈川": 9.85, "新潟": 9.33,
    "富山": 9.57, "石川": 9.66, "福井": 9.91, "山梨": 9.67, "長野": 9.49,
    "岐阜": 9.80, "静岡": 9.65, "愛知": 10.03, "三重": 9.81, "滋賀": 9.73,
    "京都": 10.03, "大阪": 10.29, "兵庫": 10.17, "奈良": 9.82, "和歌山": 9.97,
    "鳥取": 9.82, "島根": 10.10, "岡山": 10.07, "広島": 9.92, "山口": 9.96,
    "徳島": 10.25, "香川": 10.28, "愛媛": 9.99, "高知": 10.10, "福岡": 10.36,
    "佐賀": 10.42, "長崎": 10.21, "熊本": 10.32, "大分": 10.06, "宮崎": 9.76,
    "鹿児島": 10.26, "沖縄": 9.56,
}

# 介護保険料率（全国一律・40歳以上65歳未満）
# 年度: {FISCAL_YEAR}
_NURSING_CARE_RATE = 1.60  # %

# 厚生年金保険料率（2017年9月〜固定。法改正がない限り変更不要）
_PENSION_RATE = 18.300  # %（労使折半で各9.150%）

# 雇用保険料率 — 年度: {FISCAL_YEAR}（毎年4月改定）
_EMPLOYMENT_INSURANCE = {
    "employee": 0.60,  # %（労働者負担）
    "employer": 0.95,  # %（事業主負担）
}
# 注: 建設業・農林水産業は料率が異なる。上記は一般の事業。

# 労災保険料率（業種による。以下は代表的な業種）
_WORKERS_COMP_RATES: dict[str, float] = {
    "事務": 0.25,
    "小売業": 0.30,
    "飲食業": 0.30,
    "IT・通信": 0.25,
    "製造業": 0.45,
    "建設業": 0.95,
    "運輸業": 0.90,
    "清掃業": 1.30,
    "その他": 0.30,
}

# ═══════════════════════════════════════════════
# 所得税・住民税
# ═══════════════════════════════════════════════

# 所得税の速算表（2026年分）
_INCOME_TAX_TABLE = [
    (1950000, 0.05, 0),
    (3300000, 0.10, 97500),
    (6950000, 0.20, 427500),
    (9000000, 0.23, 636000),
    (18000000, 0.33, 1536000),
    (40000000, 0.40, 2796000),
    (999999999999, 0.45, 4796000),
]

# 給与所得控除（2026年分）
_SALARY_DEDUCTION_TABLE = [
    (1625000, lambda s: 550000),
    (1800000, lambda s: int(s * 0.4) - 100000),
    (3600000, lambda s: int(s * 0.3) + 80000),
    (6600000, lambda s: int(s * 0.2) + 440000),
    (8500000, lambda s: int(s * 0.1) + 1100000),
    (999999999999, lambda s: 1950000),
]

# 基礎控除
_BASIC_DEDUCTION = 480000

# 住民税率（一律10%）
_RESIDENT_TAX_RATE = 0.10
_RESIDENT_TAX_EQUALIZATION = 5000  # 均等割

# ═══════════════════════════════════════════════
# 割増賃金率（労働基準法）
# ═══════════════════════════════════════════════

_OVERTIME_RATES = {
    "時間外（月60h以下）": 1.25,
    "時間外（月60h超）": 1.50,  # 中小企業も2023年4月〜適用
    "休日労働": 1.35,
    "深夜労働（22時-5時）": 1.25,
    "時間外+深夜": 1.50,
    "休日+深夜": 1.60,
}

# ═══════════════════════════════════════════════
# 各種手当・控除の計算
# ═══════════════════════════════════════════════

# 通勤手当の非課税限度額（電車・バス通勤の場合）
_COMMUTE_TAX_FREE_LIMIT = 150000  # 月額15万円まで非課税

# 扶養控除額（所得税）
_DEPENDENT_DEDUCTIONS = {
    "一般扶養（16歳以上）": 380000,
    "特定扶養（19-22歳）": 630000,
    "老人扶養（70歳以上・同居）": 580000,
    "老人扶養（70歳以上・別居）": 480000,
}

# 配偶者控除・配偶者特別控除（納税者の合計所得金額900万円以下の場合）
_SPOUSE_DEDUCTIONS = {
    "配偶者控除（配偶者所得48万円以下）": 380000,
    "配偶者特別控除（配偶者所得48-95万円）": 380000,  # 段階的に減額
    "配偶者特別控除（配偶者所得95-100万円）": 360000,
    "配偶者特別控除（配偶者所得100-105万円）": 310000,
    "配偶者特別控除（配偶者所得105-110万円）": 260000,
    "配偶者特別控除（配偶者所得110-115万円）": 210000,
    "配偶者特別控除（配偶者所得115-120万円）": 160000,
    "配偶者特別控除（配偶者所得120-125万円）": 110000,
    "配偶者特別控除（配偶者所得125-130万円）": 60000,
    "配偶者特別控除（配偶者所得130-133万円）": 30000,
}

# 生命保険料控除（上限）
_LIFE_INSURANCE_DEDUCTION_MAX = {
    "一般生命保険料控除": 40000,
    "介護医療保険料控除": 40000,
    "個人年金保険料控除": 40000,
    "合計上限": 120000,
}

# 退職金の税金（退職所得控除）
_RETIREMENT_DEDUCTION_PER_YEAR_UNDER_20 = 400000   # 勤続20年以下: 40万円×年数
_RETIREMENT_DEDUCTION_PER_YEAR_OVER_20 = 700000    # 勤続20年超: 70万円×(年数-20) + 800万円
_RETIREMENT_DEDUCTION_MINIMUM = 800000              # 最低80万円


def calculate_overtime_pay(
    base_monthly: int,
    monthly_work_hours: float = 160,
    overtime_hours: float = 0,
    overtime_over60_hours: float = 0,
    holiday_hours: float = 0,
    late_night_hours: float = 0,
) -> dict:
    """割増賃金を計算する

    Args:
        base_monthly: 基本給（月額。手当除く）
        monthly_work_hours: 月間所定労働時間（デフォルト160h = 8h×20日）
        overtime_hours: 時間外労働時間（月60h以下の分）
        overtime_over60_hours: 時間外労働時間（月60h超の分）
        holiday_hours: 休日労働時間
        late_night_hours: 深夜労働時間（時間外とは別にカウント）

    Returns:
        各種割増賃金の内訳と合計
    """
    hourly_rate = base_monthly / monthly_work_hours

    overtime_pay = int(hourly_rate * _OVERTIME_RATES["時間外（月60h以下）"] * overtime_hours)
    overtime_over60_pay = int(hourly_rate * _OVERTIME_RATES["時間外（月60h超）"] * overtime_over60_hours)
    holiday_pay = int(hourly_rate * _OVERTIME_RATES["休日労働"] * holiday_hours)
    late_night_pay = int(hourly_rate * _OVERTIME_RATES["深夜労働（22時-5時）"] * late_night_hours)

    total = overtime_pay + overtime_over60_pay + holiday_pay + late_night_pay

    return {
        "時給単価": int(hourly_rate),
        "時間外手当（60h以下）": {"hours": overtime_hours, "rate": "125%", "amount": overtime_pay},
        "時間外手当（60h超）": {"hours": overtime_over60_hours, "rate": "150%", "amount": overtime_over60_pay},
        "休日手当": {"hours": holiday_hours, "rate": "135%", "amount": holiday_pay},
        "深夜手当": {"hours": late_night_hours, "rate": "125%", "amount": late_night_pay},
        "割増賃金合計": total,
        "支給総額（基本給+割増）": base_monthly + total,
    }


def calculate_retirement_tax(
    retirement_pay: int,
    years_of_service: int,
    is_officer: bool = False,
) -> dict:
    """退職金にかかる税金を計算する

    Args:
        retirement_pay: 退職金の額
        years_of_service: 勤続年数
        is_officer: 役員かどうか（役員は5年以下の場合の特例あり）

    Returns:
        退職所得控除額、課税退職所得、所得税、住民税、手取り額
    """
    # 退職所得控除額
    if years_of_service <= 20:
        deduction = max(_RETIREMENT_DEDUCTION_MINIMUM, _RETIREMENT_DEDUCTION_PER_YEAR_UNDER_20 * years_of_service)
    else:
        deduction = 8000000 + _RETIREMENT_DEDUCTION_PER_YEAR_OVER_20 * (years_of_service - 20)

    # 課税退職所得（1/2課税）
    taxable = max(0, retirement_pay - deduction)
    if is_officer and years_of_service <= 5:
        taxable_income = taxable  # 役員は5年以下の場合1/2適用なし
    else:
        taxable_income = taxable // 2

    # 所得税
    income_tax = calculate_income_tax(taxable_income)
    income_tax_with_reconstruction = int(income_tax * 1.021)

    # 住民税（10%）
    resident_tax = int(taxable_income * 0.10)

    return {
        "退職金": retirement_pay,
        "勤続年数": years_of_service,
        "退職所得控除額": deduction,
        "課税退職所得": taxable_income,
        "所得税（復興税込み）": income_tax_with_reconstruction,
        "住民税": resident_tax,
        "税金合計": income_tax_with_reconstruction + resident_tax,
        "手取り額": retirement_pay - income_tax_with_reconstruction - resident_tax,
    }


def calculate_annual_income_detail(
    base_monthly: int,
    bonus_months: float = 4.0,
    commute_monthly: int = 15000,
    housing_allowance: int = 0,
    family_allowance: int = 0,
    position_allowance: int = 0,
    overtime_monthly_hours: float = 20,
    monthly_work_hours: float = 160,
) -> dict:
    """各種手当込みの年収明細を計算する

    Args:
        base_monthly: 基本給（月額）
        bonus_months: 賞与月数（年間。例: 夏2ヶ月+冬2ヶ月=4.0）
        commute_monthly: 通勤手当（月額）
        housing_allowance: 住宅手当（月額）
        family_allowance: 家族手当（月額）
        position_allowance: 役職手当（月額）
        overtime_monthly_hours: 月平均残業時間
        monthly_work_hours: 月間所定労働時間

    Returns:
        月額・年額の明細
    """
    # 割増賃金
    overtime = calculate_overtime_pay(
        base_monthly=base_monthly,
        monthly_work_hours=monthly_work_hours,
        overtime_hours=min(overtime_monthly_hours, 60),
        overtime_over60_hours=max(0, overtime_monthly_hours - 60),
    )

    monthly_allowances = commute_monthly + housing_allowance + family_allowance + position_allowance
    monthly_total = base_monthly + monthly_allowances + overtime["割増賃金合計"]

    # 賞与（基本給ベース）
    bonus_annual = int(base_monthly * bonus_months)

    # 年収
    annual_salary = monthly_total * 12 + bonus_annual

    # 通勤手当の非課税分
    commute_tax_free = min(commute_monthly, _COMMUTE_TAX_FREE_LIMIT)
    taxable_annual = annual_salary - commute_tax_free * 12

    return {
        "月額明細": {
            "基本給": base_monthly,
            "役職手当": position_allowance,
            "家族手当": family_allowance,
            "住宅手当": housing_allowance,
            "通勤手当": commute_monthly,
            "時間外手当": overtime["割増賃金合計"],
            "月額総支給": monthly_total,
        },
        "年額": {
            "月額支給×12": monthly_total * 12,
            "賞与（年間）": bonus_annual,
            "年収（総支給）": annual_salary,
            "課税対象額": taxable_annual,
            "通勤手当非課税分": commute_tax_free * 12,
        },
        "残業明細": overtime,
        "markdown": _annual_income_to_markdown(
            base_monthly, monthly_total, bonus_annual, annual_salary,
            commute_monthly, housing_allowance, family_allowance,
            position_allowance, overtime,
        ),
    }


def _annual_income_to_markdown(
    base, total, bonus, annual, commute, housing, family, position, overtime
) -> str:
    """年収明細をMarkdownテーブルに変換"""
    lines = [
        "## 給与明細",
        "",
        "### 月額支給",
        "| 項目 | 金額 |",
        "|------|------|",
        f"| 基本給 | {base:,}円 |",
    ]
    if position > 0:
        lines.append(f"| 役職手当 | {position:,}円 |")
    if family > 0:
        lines.append(f"| 家族手当 | {family:,}円 |")
    if housing > 0:
        lines.append(f"| 住宅手当 | {housing:,}円 |")
    if commute > 0:
        lines.append(f"| 通勤手当 | {commute:,}円 |")
    if overtime["割増賃金合計"] > 0:
        lines.append(f"| 時間外手当 | {overtime['割増賃金合計']:,}円 |")
    lines.extend([
        f"| **月額総支給** | **{total:,}円** |",
        "",
        "### 年額",
        "| 項目 | 金額 |",
        "|------|------|",
        f"| 月額支給 x 12 | {total * 12:,}円 |",
        f"| 賞与（年間） | {bonus:,}円 |",
        f"| **年収（総支給）** | **{annual:,}円** |",
    ])
    return "\n".join(lines)


def _round_insurance(amount: float) -> int:
    """保険料の端数処理（50銭以下切り捨て、50銭超切り上げ）"""
    if amount - math.floor(amount) <= 0.5:
        return math.floor(amount)
    return math.ceil(amount)


def get_standard_monthly(gross_monthly: int) -> dict:
    """月額報酬から標準報酬月額を決定する"""
    for grade in _STANDARD_MONTHLY_GRADES:
        if grade["lower"] <= gross_monthly < grade["upper"]:
            return grade
    return _STANDARD_MONTHLY_GRADES[-1]


def get_salary_deduction(annual_salary: int) -> int:
    """給与所得控除額を算出する"""
    for limit, calc in _SALARY_DEDUCTION_TABLE:
        if annual_salary <= limit:
            return calc(annual_salary)
    return 1950000


def calculate_income_tax(taxable_income: int) -> int:
    """課税所得から所得税額を算出する"""
    if taxable_income <= 0:
        return 0
    for limit, rate, deduction in _INCOME_TAX_TABLE:
        if taxable_income <= limit:
            return int(taxable_income * rate - deduction)
    return int(taxable_income * 0.45 - 4796000)


@dataclass
class InsuranceResult:
    """保険料計算結果"""
    # 基本情報
    annual_salary: int
    monthly_salary: int
    standard_monthly: int
    grade: int
    prefecture: str
    age: int
    industry: str
    dependents: int

    # 健康保険
    health_employee: int
    health_employer: int
    health_rate: float

    # 介護保険（40歳以上）
    nursing_employee: int
    nursing_employer: int

    # 厚生年金
    pension_employee: int
    pension_employer: int
    pension_standard_monthly: int  # 厚生年金の標準報酬月額（上限あり）

    # 雇用保険
    employment_employee: int
    employment_employer: int

    # 労災保険
    workers_comp: int

    # 子ども・子育て拠出金
    child_contribution: int

    # 合計
    total_employee_monthly: int
    total_employer_monthly: int
    total_employee_annual: int
    total_employer_annual: int

    # 所得税・住民税（概算）
    income_tax_annual: int
    resident_tax_annual: int
    salary_deduction: int
    taxable_income: int

    # 手取り
    take_home_annual: int
    take_home_monthly: int

    # 総人件費
    total_labor_cost_annual: int
    total_labor_cost_monthly: int

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}

    def summary(self) -> str:
        """経営者向けサマリーを返す"""
        lines = [
            f"## 給与・保険料計算結果（{FISCAL_YEAR}年度料率）",
            f"",
            f"### 基本情報",
            f"| 項目 | 金額 |",
            f"|------|------|",
            f"| 年収 | {self.annual_salary:,}円 |",
            f"| 月額報酬 | {self.monthly_salary:,}円 |",
            f"| 標準報酬月額 | {self.standard_monthly:,}円（{self.grade}等級） |",
            f"| 都道府県 | {self.prefecture}（健保料率 {self.health_rate}%） |",
            f"| 年齢 | {self.age}歳{'（介護保険対象）' if self.age >= 40 else ''} |",
            f"| 業種 | {self.industry} |",
            f"",
            f"### 月額保険料（本人負担 / 会社負担）",
            f"| 項目 | 本人負担 | 会社負担 |",
            f"|------|---------|---------|",
            f"| 健康保険 | {self.health_employee:,}円 | {self.health_employer:,}円 |",
        ]

        if self.age >= 40:
            lines.append(f"| 介護保険 | {self.nursing_employee:,}円 | {self.nursing_employer:,}円 |")

        lines.extend([
            f"| 厚生年金 | {self.pension_employee:,}円 | {self.pension_employer:,}円 |",
            f"| 雇用保険 | {self.employment_employee:,}円 | {self.employment_employer:,}円 |",
            f"| 労災保険 | — | {self.workers_comp:,}円 |",
            f"| 子ども拠出金 | — | {self.child_contribution:,}円 |",
            f"| **月額合計** | **{self.total_employee_monthly:,}円** | **{self.total_employer_monthly:,}円** |",
            f"",
            f"### 年間まとめ",
            f"| 項目 | 金額 |",
            f"|------|------|",
            f"| 本人負担（社保）年間 | {self.total_employee_annual:,}円 |",
            f"| 会社負担（社保）年間 | {self.total_employer_annual:,}円 |",
            f"| 所得税（概算） | {self.income_tax_annual:,}円 |",
            f"| 住民税（概算） | {self.resident_tax_annual:,}円 |",
            f"| **手取り（概算）** | **{self.take_home_annual:,}円（月 {self.take_home_monthly:,}円）** |",
            f"| **総人件費（会社負担総額）** | **{self.total_labor_cost_annual:,}円（月 {self.total_labor_cost_monthly:,}円）** |",
            f"",
            f"※ 上記は概算です。扶養人数{self.dependents}人で計算。実際の金額は扶養状況・各種控除により異なります。",
        ])

        return "\n".join(lines)


def calculate_insurance(
    annual_salary: int,
    age: int = 35,
    prefecture: str = "東京",
    industry: str = "事務",
    dependents: int = 0,
    bonus_months: float = 0,
) -> InsuranceResult:
    """社会保険料・税金を正確に計算する

    Args:
        annual_salary: 年収（額面）
        age: 年齢（40歳以上で介護保険適用）
        prefecture: 都道府県（健康保険料率に影響）
        industry: 業種（労災保険料率に影響）
        dependents: 扶養人数（所得税に影響）
        bonus_months: 賞与月数（0なら月額 = 年収/12）

    Returns:
        InsuranceResult: 全保険料・税金の計算結果
    """
    # 月額報酬の算出
    if bonus_months > 0:
        monthly_salary = int(annual_salary / (12 + bonus_months))
    else:
        monthly_salary = annual_salary // 12

    # 標準報酬月額の決定
    grade_info = get_standard_monthly(monthly_salary)
    standard_monthly = grade_info["monthly"]
    grade = grade_info["grade"]

    # 厚生年金の標準報酬月額（上限650,000円）
    pension_standard = min(standard_monthly, 650000)

    # ── 健康保険料 ──
    health_rate = _HEALTH_INSURANCE_RATES.get(prefecture, 9.98)
    health_half_rate = health_rate / 2 / 100
    health_employee = _round_insurance(standard_monthly * health_half_rate)
    health_employer = _round_insurance(standard_monthly * health_half_rate)

    # ── 介護保険料 ──
    if age >= 40:
        nursing_half_rate = _NURSING_CARE_RATE / 2 / 100
        nursing_employee = _round_insurance(standard_monthly * nursing_half_rate)
        nursing_employer = _round_insurance(standard_monthly * nursing_half_rate)
    else:
        nursing_employee = 0
        nursing_employer = 0

    # ── 厚生年金保険料 ──
    pension_half_rate = _PENSION_RATE / 2 / 100
    pension_employee = _round_insurance(pension_standard * pension_half_rate)
    pension_employer = _round_insurance(pension_standard * pension_half_rate)

    # ── 雇用保険料 ──
    emp_rate_employee = _EMPLOYMENT_INSURANCE["employee"] / 100
    emp_rate_employer = _EMPLOYMENT_INSURANCE["employer"] / 100
    employment_employee = _round_insurance(monthly_salary * emp_rate_employee)
    employment_employer = _round_insurance(monthly_salary * emp_rate_employer)

    # ── 労災保険料（全額事業主負担）──
    wc_rate = _WORKERS_COMP_RATES.get(industry, 0.30) / 100
    workers_comp = _round_insurance(monthly_salary * wc_rate)

    # ── 子ども・子育て拠出金（全額事業主負担）──
    child_rate = 0.36 / 100  # 0.36%
    child_contribution = _round_insurance(standard_monthly * child_rate)

    # ── 月額合計 ──
    total_employee_monthly = health_employee + nursing_employee + pension_employee + employment_employee
    total_employer_monthly = (health_employer + nursing_employer + pension_employer +
                              employment_employer + workers_comp + child_contribution)

    # ── 年間合計 ──
    total_employee_annual = total_employee_monthly * 12
    total_employer_annual = total_employer_monthly * 12

    # ── 所得税（概算）──
    salary_deduction = get_salary_deduction(annual_salary)
    social_insurance_deduction = total_employee_annual
    dependent_deduction = dependents * 380000  # 扶養控除（一般）
    taxable_income = max(0, annual_salary - salary_deduction - social_insurance_deduction -
                         _BASIC_DEDUCTION - dependent_deduction)
    income_tax = calculate_income_tax(taxable_income)
    # 復興特別所得税
    income_tax_with_reconstruction = int(income_tax * 1.021)

    # ── 住民税（概算）──
    resident_taxable = max(0, annual_salary - salary_deduction - social_insurance_deduction -
                           430000 - dependent_deduction * 330000 // 380000)  # 住民税の基礎控除は43万円
    resident_tax = int(resident_taxable * _RESIDENT_TAX_RATE) + _RESIDENT_TAX_EQUALIZATION

    # ── 手取り ──
    take_home_annual = annual_salary - total_employee_annual - income_tax_with_reconstruction - resident_tax
    take_home_monthly = take_home_annual // 12

    # ── 総人件費 ──
    total_labor_cost_annual = annual_salary + total_employer_annual
    total_labor_cost_monthly = total_labor_cost_annual // 12

    return InsuranceResult(
        annual_salary=annual_salary,
        monthly_salary=monthly_salary,
        standard_monthly=standard_monthly,
        grade=grade,
        prefecture=prefecture,
        age=age,
        industry=industry,
        dependents=dependents,
        health_employee=health_employee,
        health_employer=health_employer,
        health_rate=health_rate,
        nursing_employee=nursing_employee,
        nursing_employer=nursing_employer,
        pension_employee=pension_employee,
        pension_employer=pension_employer,
        pension_standard_monthly=pension_standard,
        employment_employee=employment_employee,
        employment_employer=employment_employer,
        workers_comp=workers_comp,
        child_contribution=child_contribution,
        total_employee_monthly=total_employee_monthly,
        total_employer_monthly=total_employer_monthly,
        total_employee_annual=total_employee_annual,
        total_employer_annual=total_employer_annual,
        income_tax_annual=income_tax_with_reconstruction,
        resident_tax_annual=resident_tax,
        salary_deduction=salary_deduction,
        taxable_income=taxable_income,
        take_home_annual=take_home_annual,
        take_home_monthly=take_home_monthly,
        total_labor_cost_annual=total_labor_cost_annual,
        total_labor_cost_monthly=total_labor_cost_monthly,
    )
