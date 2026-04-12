"""法務エージェント - 顧問弁護士の補佐 + 契約管理 + 書類作成"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from .base import BaseAgent

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CONTRACTS_DIR = _DATA_DIR / "contracts"
_CONTRACT_LEDGER = _DATA_DIR / "contract_ledger.json"

# 印紙税額表（主要な契約類型）
_STAMP_TAX_TABLE = {
    "売買契約・請負契約": [
        (10000, 0, "非課税"),
        (1000000, 200, ""),
        (2000000, 400, ""),
        (3000000, 1000, ""),
        (5000000, 2000, ""),
        (10000000, 10000, ""),
        (50000000, 20000, ""),
        (100000000, 60000, ""),
        (500000000, 100000, ""),
        (1000000000, 200000, ""),
        (5000000000, 400000, ""),
        (999999999999, 600000, ""),
    ],
    "業務委託契約（継続的取引）": [
        (999999999999, 4000, "第7号文書。金額に関わらず一律4,000円"),
    ],
    "NDA・秘密保持契約": [
        (999999999999, 0, "不課税。印紙不要"),
    ],
    "金銭消費貸借契約": [
        (10000, 0, "非課税"),
        (100000, 200, ""),
        (500000, 400, ""),
        (1000000, 1000, ""),
        (5000000, 2000, ""),
        (10000000, 10000, ""),
        (50000000, 20000, ""),
        (100000000, 60000, ""),
        (500000000, 100000, ""),
        (1000000000, 200000, ""),
        (999999999999, 400000, ""),
    ],
}

# 契約書テンプレートの構成要素
_CONTRACT_TEMPLATES = {
    "NDA": {
        "正式名称": "秘密保持契約書",
        "必須条項": [
            "秘密情報の定義",
            "秘密保持義務",
            "目的外使用の禁止",
            "秘密情報の返還・廃棄",
            "有効期間",
            "損害賠償",
            "準拠法・管轄裁判所",
        ],
        "注意点": "秘密情報の定義が広すぎると実務上問題。「書面で秘密と指定したもの」に限定するのが実務的",
    },
    "業務委託": {
        "正式名称": "業務委託契約書",
        "必須条項": [
            "委託業務の内容",
            "報酬・支払条件",
            "契約期間",
            "再委託の可否",
            "成果物の帰属（知的財産権）",
            "秘密保持",
            "解除条件",
            "損害賠償",
            "反社会的勢力の排除",
            "準拠法・管轄裁判所",
        ],
        "注意点": "偽装請負に該当しないよう、指揮命令関係に注意。下請法の適用も確認",
    },
    "売買契約": {
        "正式名称": "売買基本契約書",
        "必須条項": [
            "売買の目的物",
            "数量・単価・代金",
            "納品・検収条件",
            "所有権の移転時期",
            "危険負担",
            "瑕疵担保（契約不適合責任）",
            "支払条件",
            "解除条件",
            "損害賠償",
            "準拠法・管轄裁判所",
        ],
        "注意点": "下請法対象取引の場合、支払期日は受領日から60日以内（下請法第2条の2）",
    },
    "雇用契約": {
        "正式名称": "雇用契約書（労働条件通知書兼用）",
        "必須条項": [
            "契約期間",
            "就業場所",
            "業務内容",
            "始業・終業時刻",
            "休日・休暇",
            "賃金（基本給、手当、支払方法、締日・支払日）",
            "退職に関する事項",
            "社会保険の適用",
            "試用期間",
        ],
        "注意点": "労働基準法第15条により書面交付が義務。2024年4月から就業場所・業務内容の変更範囲の明示が義務化",
    },
    "賃貸借契約": {
        "正式名称": "建物賃貸借契約書",
        "必須条項": [
            "賃貸借の目的物",
            "使用目的",
            "賃料・共益費",
            "敷金・保証金",
            "契約期間・更新",
            "原状回復",
            "禁止事項",
            "解約条件",
            "損害賠償",
        ],
        "注意点": "借地借家法により借主保護が手厚い。正当事由なき解約拒絶は困難",
    },
    "利用規約": {
        "正式名称": "サービス利用規約",
        "必須条項": [
            "サービスの内容",
            "利用登録・アカウント",
            "利用料金・支払い",
            "禁止事項",
            "知的財産権",
            "免責事項・責任制限",
            "個人情報の取り扱い",
            "サービスの変更・終了",
            "規約の変更",
            "準拠法・管轄裁判所",
        ],
        "注意点": "消費者契約法による不当条項の無効に注意。一方的に不利な免責条項は無効になりうる",
    },
}


class LegalAgent(BaseAgent):
    """法務エージェント - 契約レビュー、ドラフト生成、契約管理、法改正チェック"""

    name = "法務エージェント"
    description = "顧問弁護士補佐：契約レビュー・ドラフト生成・契約管理・印紙税・法改正"
    icon = "L"

    def system_prompt(self) -> str:
        # 契約管理台帳の状況を組み込む
        ledger_summary = self._get_ledger_summary()

        return f"""あなたはAIDX経営エージェントシステムの法務エージェントです。
顧問弁護士の補佐として、経営者の法務判断をサポートします。

## 人格
- 慎重で、リスクを見逃さない
- 平易な言葉で法的リスクを説明する（法律用語には必ず補足説明を添える）
- 最悪のケースを想定しつつ、実務的な落としどころも提示する
- 「やるな」ではなく「こうすればリスクを減らせる」と代替案を出す

## 契約管理台帳の状況
{ledger_summary}

## 専門領域

### 1. 契約書レビュー
- リスク箇所の抽出（HIGH/MEDIUM/LOW の3段階）
- 7条項チェック（損害賠償/契約期間/知財/秘密保持/解除/競業避止/準拠法）
- 修正文言の提案
- 弁護士に確認すべき事項のリスト化

### 2. 契約書ドラフト生成
以下の契約書の雛形を状況に合わせて生成できる：
- NDA（秘密保持契約書）
- 業務委託契約書
- 売買基本契約書
- 雇用契約書（労働条件通知書兼用）
- 建物賃貸借契約書
- サービス利用規約
- 内容証明郵便

雛形を出す際は必ず：
- 相手方との力関係を確認（自社が強い/対等/弱い）
- 業種・取引内容に合わせてカスタマイズ
- 「この雛形はたたき台です。必ず弁護士の確認を受けてください」と注記

### 3. 契約書の新旧比較
「修正案もらったけど何が変わった？」に対応。
変更点を表形式で出す：
| 条項 | 変更前 | 変更後 | 影響度 | コメント |

### 4. 契約管理台帳
data/contract_ledger.json に契約一覧を管理：
- 契約の登録・検索
- 更新期限のアラート（30日前から警告）
- 自動更新の管理

### 5. 印紙税の計算
契約類型と金額から印紙税額を即答。
電子契約なら印紙不要であることも案内。

### 6. 法改正チェック
Agent Reach連携で最新の法改正情報を取得。
「うちに関係する法改正ある？」に対応。

### 7. コンプライアンスチェック
- 下請法の適用判断
- 個人情報保護法への対応状況
- 反社チェック体制
- ハラスメント防止措置

## 出力ルール
- リスクレベル: HIGH（修正必須）/ MEDIUM（交渉推奨）/ LOW（認識しておく）
- 法令名・条文を可能な限り引用
- 「こうすべき」ではなく「こういうリスクがある。回避策はこう」
- 必ず「弁護士に確認すべき事項」を最後に列挙

## 免責事項（必ず全回答に記載）
本エージェントは法的助言を行うものではありません。
分析結果は参考情報であり、最終判断は必ず弁護士にご確認ください。
"""

    def review_contract(self, file_path: str | Path) -> str:
        """契約書PDFを読み込んでリスク分析を行う"""
        from tools.pdf_reader import read_pdf

        data = read_pdf(file_path)
        prompt = (
            "以下の契約書を法務レビューしてください。\n"
            "7条項（損害賠償/契約期間/知財/秘密保持/解除/競業避止/準拠法）を必ずチェック。\n"
            "各条項にHIGH/MEDIUM/LOWのリスクレベルを付けてください。\n"
            "最後に「弁護士に確認すべき事項」をリストで出してください。\n\n"
            f"ファイル: {data['filename']}（全{data['total_pages']}ページ）\n\n"
            f"--- 契約書本文 ---\n{data['markdown']}"
        )
        return self.ask(prompt)

    def draft_contract(self, contract_type: str, context: str) -> str:
        """契約書のドラフトを生成する"""
        template = _CONTRACT_TEMPLATES.get(contract_type)
        template_info = ""
        if template:
            clauses = "\n".join(f"  - {c}" for c in template["必須条項"])
            template_info = (
                f"\n契約種別: {template['正式名称']}\n"
                f"必須条項:\n{clauses}\n"
                f"注意点: {template['注意点']}\n"
            )

        prompt = (
            f"以下の情報を基に{contract_type}のドラフトを作成してください。\n"
            f"{template_info}\n"
            "条文形式（第1条、第2条...）で出力してください。\n"
            "各条項にはコメント（なぜこの条項が必要か）を付けてください。\n"
            "最後に「この雛形はたたき台です。必ず弁護士の確認を受けてください」と記載。\n\n"
            f"--- 依頼内容 ---\n{context}"
        )
        return self.ask(prompt)

    def compare_contracts(self, original: str, revised: str) -> str:
        """契約書の新旧を比較する"""
        prompt = (
            "以下の2つの契約書を比較してください。\n"
            "変更点を表形式で出力してください：\n"
            "| 条項 | 変更前 | 変更後 | 影響度 | コメント |\n\n"
            "影響度はHIGH/MEDIUM/LOWで。\n"
            "自社に不利な変更は必ず指摘してください。\n\n"
            f"--- 原本 ---\n{original}\n\n"
            f"--- 修正案 ---\n{revised}"
        )
        return self.ask(prompt)

    def calculate_stamp_tax(self, contract_type: str, amount: int) -> dict:
        """印紙税額を計算する"""
        table = _STAMP_TAX_TABLE.get(contract_type)
        if not table:
            return {
                "contract_type": contract_type,
                "amount": amount,
                "stamp_tax": "不明",
                "note": f"「{contract_type}」の印紙税テーブルがありません。弁護士に確認してください。",
            }

        for threshold, tax, note in table:
            if amount <= threshold:
                return {
                    "contract_type": contract_type,
                    "amount": amount,
                    "stamp_tax": tax,
                    "note": note or f"契約金額{amount:,}円に対する印紙税額",
                    "electronic_note": "電子契約の場合は印紙不要（0円）",
                }

        return {"contract_type": contract_type, "amount": amount, "stamp_tax": "要確認"}

    def draft_demand_letter(self, context: str) -> str:
        """内容証明郵便のドラフトを作成する"""
        prompt = (
            "以下の情報を基に内容証明郵便のドラフトを作成してください。\n"
            "形式:\n"
            "- 1行26文字以内、1ページ20行以内（内容証明の書式制限）\n"
            "- 差出人・受取人の住所氏名\n"
            "- 日付\n"
            "- 通知内容（事実→法的根拠→要求事項→期限）\n"
            "- 「本書面到達後○日以内にご対応いただけない場合、法的措置を検討いたします」\n\n"
            "注意: 内容証明は証拠保全の手段であり、それ自体に法的強制力はありません。\n\n"
            f"--- 依頼内容 ---\n{context}"
        )
        return self.ask(prompt)

    def check_law_updates(self, industry: str) -> str:
        """業界に関連する法改正をチェックする"""
        prompt = (
            f"以下の業界に関連する最新の法改正・法律動向を確認してください。\n"
            f"業界: {industry}\n\n"
            "Web検索で最新情報を取得し、以下のフォーマットで報告:\n"
            "| 法律名 | 改正内容 | 施行日 | 御社への影響 | 必要な対応 |\n\n"
            "特に以下をチェック:\n"
            "- 労働基準法の改正\n"
            "- 下請法・独占禁止法の運用変更\n"
            "- 個人情報保護法\n"
            "- インボイス制度関連\n"
            "- 業界固有の規制変更\n"
        )
        return self.ask(prompt)

    # ── 契約管理台帳 ──

    def _load_ledger(self) -> list[dict]:
        """契約管理台帳を読み込む"""
        if not _CONTRACT_LEDGER.exists():
            return []
        try:
            return json.loads(_CONTRACT_LEDGER.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def _save_ledger(self, ledger: list[dict]) -> None:
        """契約管理台帳を保存する"""
        _CONTRACT_LEDGER.parent.mkdir(parents=True, exist_ok=True)
        _CONTRACT_LEDGER.write_text(
            json.dumps(ledger, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def register_contract(
        self,
        title: str,
        counterparty: str,
        contract_type: str,
        start_date: str,
        end_date: str = "",
        auto_renew: bool = False,
        amount: int = 0,
        notes: str = "",
    ) -> dict:
        """契約を台帳に登録する"""
        ledger = self._load_ledger()
        entry = {
            "id": len(ledger) + 1,
            "title": title,
            "counterparty": counterparty,
            "type": contract_type,
            "start_date": start_date,
            "end_date": end_date,
            "auto_renew": auto_renew,
            "amount": amount,
            "notes": notes,
            "status": "active",
            "registered": datetime.now().strftime("%Y-%m-%d"),
        }
        ledger.append(entry)
        self._save_ledger(ledger)
        return entry

    def get_expiring_contracts(self, days: int = 30) -> list[dict]:
        """指定日数以内に期限が来る契約を取得する"""
        ledger = self._load_ledger()
        today = datetime.now().date()
        expiring = []
        for c in ledger:
            if c.get("status") != "active" or not c.get("end_date"):
                continue
            try:
                end = datetime.strptime(c["end_date"], "%Y-%m-%d").date()
                remaining = (end - today).days
                if 0 <= remaining <= days:
                    c["remaining_days"] = remaining
                    expiring.append(c)
            except ValueError:
                pass
        return sorted(expiring, key=lambda x: x.get("remaining_days", 999))

    def _get_ledger_summary(self) -> str:
        """契約管理台帳のサマリーを返す"""
        ledger = self._load_ledger()
        if not ledger:
            return "契約管理台帳にはまだ契約が登録されていません。"

        active = [c for c in ledger if c.get("status") == "active"]
        expiring = self.get_expiring_contracts(30)

        parts = [f"登録契約数: {len(active)}件"]
        if expiring:
            parts.append(f"30日以内に期限到来: {len(expiring)}件（要確認）")
            for c in expiring[:3]:
                parts.append(f"  - {c['counterparty']}: {c['title']}（残{c['remaining_days']}日）")
        return "\n".join(parts)

    def get_contract_templates(self) -> dict:
        """利用可能な契約書テンプレート一覧を返す"""
        return {k: v["正式名称"] for k, v in _CONTRACT_TEMPLATES.items()}

    def list_data_files(self) -> list[Path]:
        """data/contracts/ 内のファイル一覧を返す"""
        if not _CONTRACTS_DIR.exists():
            return []
        return sorted(
            p for p in _CONTRACTS_DIR.iterdir()
            if p.suffix == ".pdf" and not p.name.startswith(".")
        )
