"""秘書エージェント - タスク管理 + ビジネス文書作成"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from .base import BaseAgent

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_TASKS_FILE = _DATA_DIR / "tasks.json"
_REMINDERS_FILE = _DATA_DIR / "reminders.json"


class SecretaryAgent(BaseAgent):
    """秘書エージェント - タスク管理、議事録、メール、提案書"""

    name = "秘書エージェント"
    description = "エグゼクティブ秘書：タスク管理・議事録・メール・提案書"
    icon = "S"

    def system_prompt(self) -> str:
        # 現在のタスク・リマインダー一覧を動的に組み込む
        tasks_summary = self._get_tasks_summary()
        reminders_summary = self._get_reminders_summary()

        return f"""あなたはAIDX経営エージェントシステムの秘書エージェントです。
敏腕エグゼクティブ秘書として、経営者の日常業務をサポートします。

## 最重要機能: タスク管理

あなたの最大の役割はタスク管理です。
経営者の「あれどうなった？」に即答できることが価値です。

### 現在のタスク状況
{tasks_summary}

### 現在のリマインダー
{reminders_summary}

### タスク管理のルール

1. 会議・会話の中で出たアクションアイテムは自動でタスク化を提案する
2. タスクには必ず「担当」「期限」「ステータス」を付ける
3. 期限が近いタスク（3日以内）は警告する
4. 期限を過ぎたタスクは最優先で報告する
5. 「今日やること」を聞かれたら、期限順でリストを出す

### タスクのステータス
- todo: 未着手
- doing: 進行中
- done: 完了
- overdue: 期限超過（自動判定）

### タスク操作コマンド
ユーザーがこう言ったら、対応するタスク操作を行ってください：

- 「タスク追加: 〇〇」→ 新規タスクを追加（担当・期限を確認）
- 「タスク一覧」「今やること」→ 未完了タスクを期限順で表示
- 「〇〇完了」「〇〇終わった」→ ステータスをdoneに変更
- 「今週のタスク」→ 今週期限のタスクを表示
- 「遅れてるやつ」→ 期限超過タスクを表示
- 「田中さんのタスク」→ 担当者でフィルタ

### リマインダー操作コマンド
- 「3日後にリマインドして: 〇〇」→ 指定日にリマインダーを設定
- 「来週月曜に思い出させて: 〇〇」→ 日付を解釈してリマインダー設定
- 「リマインダー一覧」→ 予定されているリマインダーを表示
- 「〇〇のリマインダー消して」→ リマインダーを削除

リマインダーは起動時（ブリーフィング）に自動チェックする。
今日が期日のリマインダーがあれば最優先で通知する。
タスクの期限2日前に自動でリマインダーを提案する。

## タスク出力フォーマット

```
## タスク一覧（未完了: X件 / 期限超過: Y件）

### 期限超過
| 担当 | タスク | 期限 | 遅延 |
|------|--------|------|------|
| 田中 | 見積書作成 | 4/8 | 4日超過 |

### 今日〜3日以内
| 担当 | タスク | 期限 | 状態 |
|------|--------|------|------|
| 佐藤 | 事業計画書修正 | 4/13 | 進行中 |

### 今週中
| 担当 | タスク | 期限 | 状態 |
|------|--------|------|------|
| 鈴木 | 顧客ヒアリング | 4/18 | 未着手 |
```

## 人格
- 気が利く — 指示の背景にある意図を汲み取る
- 要点をまとめるのが上手い — 長い会議も3行で要約できる
- プロフェッショナルな文体 — ビジネスマナーに精通
- 先回り — タスクの漏れや期限切れを自分から報告する
- しつこいぐらいにフォローする — 「あの件、進んでますか？」を自分から言う

## 文書作成

### 議事録
会議内容からの自動生成。必ず「決定事項」と「アクションアイテム」を分離。
アクションアイテムは自動的にタスクへの追加を提案する。

```
# 議事録: [会議名]
日時: YYYY/MM/DD HH:MM
参加者: [名前]
議題: [議題]

## 決定事項
1. [内容]

## アクションアイテム（→タスクに追加しますか？）
| 担当 | タスク | 期限 |
|------|--------|------|
| [名前] | [内容] | [日付] |

## 議論の要点
[要約]

## 次回予定
[日時・議題]
```

### ビジネスメール
- 件名は20文字以内
- 「結論→理由→詳細→依頼事項」の順
- 敬語レベル: 社外（丁寧）/ 社内上司（標準）/ 同僚（カジュアル）

敬語パターン:
- 初めての取引先: 「突然のご連絡失礼いたします」
- 既存顧客: 「いつもお世話になっております」
- お詫び: 「このたびはご迷惑をおかけし、誠に申し訳ございません」
- 依頼: 「お忙しいところ恐れ入りますが」
- お礼: 「早速のご対応、誠にありがとうございます」

### 提案書
1. エグゼクティブサマリー（1段落）
2. 背景・課題
3. 提案内容
4. 期待効果
5. スケジュール・予算
6. リスクと対策

### 日報・週報
```
# [日報/週報] YYYY/MM/DD

## 今日やったこと
1. [内容]（[所要時間]）

## 明日やること
1. [内容]

## 課題・相談事項
- [内容]
```
"""

    def _get_tasks_summary(self) -> str:
        """現在のタスク状況のサマリーを返す"""
        tasks = self._load_tasks()
        if not tasks:
            return "タスクはまだ登録されていません。"

        today = datetime.now().date()
        overdue = []
        upcoming = []
        doing = []

        for t in tasks:
            if t.get("status") == "done":
                continue
            deadline = t.get("deadline")
            if deadline:
                try:
                    d = datetime.strptime(deadline, "%Y-%m-%d").date()
                    if d < today:
                        t["_overdue_days"] = (today - d).days
                        overdue.append(t)
                    elif d <= today + timedelta(days=3):
                        upcoming.append(t)
                except ValueError:
                    pass
            if t.get("status") == "doing":
                doing.append(t)

        parts = []
        parts.append(f"未完了タスク: {len([t for t in tasks if t.get('status') != 'done'])}件")
        if overdue:
            parts.append(f"期限超過: {len(overdue)}件（要対応）")
            for t in overdue:
                parts.append(f"  - {t.get('owner','?')}: {t.get('task','')}（{t.get('_overdue_days',0)}日超過）")
        if upcoming:
            parts.append(f"3日以内の期限: {len(upcoming)}件")
        if doing:
            parts.append(f"進行中: {len(doing)}件")

        return "\n".join(parts)

    def _load_tasks(self) -> list[dict]:
        """タスクファイルを読み込む"""
        if not _TASKS_FILE.exists():
            return []
        try:
            return json.loads(_TASKS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def _save_tasks(self, tasks: list[dict]) -> None:
        """タスクファイルに保存する"""
        _TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _TASKS_FILE.write_text(
            json.dumps(tasks, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_task(self, task: str, owner: str = "", deadline: str = "") -> dict:
        """タスクを追加する"""
        tasks = self._load_tasks()
        new_task = {
            "id": len(tasks) + 1,
            "task": task,
            "owner": owner,
            "deadline": deadline,
            "status": "todo",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        tasks.append(new_task)
        self._save_tasks(tasks)
        return new_task

    def complete_task(self, task_id: int) -> dict | None:
        """タスクを完了にする"""
        tasks = self._load_tasks()
        for t in tasks:
            if t.get("id") == task_id:
                t["status"] = "done"
                t["completed"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                self._save_tasks(tasks)
                return t
        return None

    def get_tasks(self, owner: str | None = None, status: str | None = None) -> list[dict]:
        """タスク一覧を取得する（フィルタ可能）"""
        tasks = self._load_tasks()
        if owner:
            tasks = [t for t in tasks if t.get("owner", "").lower() == owner.lower()]
        if status:
            tasks = [t for t in tasks if t.get("status") == status]
        return tasks

    def get_overdue_tasks(self) -> list[dict]:
        """期限超過タスクを取得する"""
        tasks = self._load_tasks()
        today = datetime.now().date()
        overdue = []
        for t in tasks:
            if t.get("status") == "done":
                continue
            deadline = t.get("deadline")
            if deadline:
                try:
                    d = datetime.strptime(deadline, "%Y-%m-%d").date()
                    if d < today:
                        t["overdue_days"] = (today - d).days
                        overdue.append(t)
                except ValueError:
                    pass
        return sorted(overdue, key=lambda x: x.get("overdue_days", 0), reverse=True)

    def create_minutes(self, meeting_text: str) -> str:
        """会議テキストから議事録を生成する"""
        prompt = (
            "以下の会議内容から議事録を作成してください。\n"
            "必ず「決定事項」と「アクションアイテム」を分離してください。\n"
            "アクションアイテムには担当者と期限を付けてください。\n"
            "最後に「上記アクションアイテムをタスクに追加しますか？」と確認してください。\n\n"
            f"--- 会議内容 ---\n{meeting_text}"
        )
        return self.ask(prompt)

    def draft_email(self, context: str) -> str:
        """コンテキストからビジネスメールを下書きする"""
        prompt = (
            "以下の内容でビジネスメールを作成してください。\n"
            "件名は20文字以内。本文は結論→理由→詳細→依頼事項の順。\n"
            "相手との関係性に合わせて敬語レベルを調整してください。\n\n"
            f"--- 依頼内容 ---\n{context}"
        )
        return self.ask(prompt)

    def draft_proposal(self, context: str) -> str:
        """コンテキストから提案書を作成する"""
        prompt = (
            "以下の内容で提案書を作成してください。\n"
            "構成: エグゼクティブサマリー→背景・課題→提案内容→期待効果→スケジュール・予算→リスクと対策\n\n"
            f"--- 依頼内容 ---\n{context}"
        )
        return self.ask(prompt)

    def daily_briefing(self) -> str:
        """朝のブリーフィング（今日やるべきこと + リマインダー）"""
        overdue = self.get_overdue_tasks()
        today_tasks = self._get_today_tasks()
        today_reminders = self.get_due_reminders()
        all_incomplete = [t for t in self._load_tasks() if t.get("status") != "done"]

        # タスクの期限2日前リマインダーを自動提案
        upcoming_tasks = self._get_upcoming_tasks(days=2)

        prompt_parts = ["今日のブリーフィングを作成してください。\n"]

        if today_reminders:
            prompt_parts.append(f"## リマインダー（{len(today_reminders)}件）")
            for r in today_reminders:
                prompt_parts.append(f"  - {r['message']}")

        if overdue:
            prompt_parts.append(f"\n## 期限超過タスク（{len(overdue)}件・要対応）")
            for t in overdue:
                prompt_parts.append(f"  - {t.get('owner','?')}: {t['task']}（{t.get('overdue_days',0)}日超過）")

        if today_tasks:
            prompt_parts.append(f"\n## 今日が期限のタスク（{len(today_tasks)}件）")
            for t in today_tasks:
                prompt_parts.append(f"  - {t.get('owner','?')}: {t['task']}")

        if upcoming_tasks:
            prompt_parts.append(f"\n## 明日〜明後日が期限（{len(upcoming_tasks)}件）")
            for t in upcoming_tasks:
                prompt_parts.append(f"  - {t.get('owner','?')}: {t['task']}（{t.get('deadline')}）")

        prompt_parts.append(f"\n未完了タスク合計: {len(all_incomplete)}件")

        # 月曜日なら業界ニュースの収集を提案
        if datetime.now().weekday() == 0:  # 0 = Monday
            news_config = _DATA_DIR / "news_config.json"
            if news_config.exists():
                prompt_parts.append("\n## 業界ニュース")
                prompt_parts.append("月曜日です。`skills/industry-news/SKILL.md` に従って業界ニュースを収集してください。")
                prompt_parts.append("3行サマリーをブリーフィングに含めてください。")
            else:
                prompt_parts.append("\n## 業界ニュース")
                prompt_parts.append("業界ニュースの定期収集が未設定です。")
                prompt_parts.append("業種・競合・キーワードを教えていただければ、毎週月曜に自動で業界動向をまとめます。")

        prompt_parts.append("\n優先順位をつけて、今日やるべきことを3つに絞ってください。")

        return self.ask("\n".join(prompt_parts))

    def _get_today_tasks(self) -> list[dict]:
        """今日が期限のタスクを取得する"""
        tasks = self._load_tasks()
        today = datetime.now().strftime("%Y-%m-%d")
        return [
            t for t in tasks
            if t.get("deadline") == today and t.get("status") != "done"
        ]

    def _get_upcoming_tasks(self, days: int = 2) -> list[dict]:
        """N日以内に期限が来るタスクを取得する（今日は除く）"""
        tasks = self._load_tasks()
        today = datetime.now().date()
        upcoming = []
        for t in tasks:
            if t.get("status") == "done":
                continue
            deadline = t.get("deadline")
            if deadline:
                try:
                    d = datetime.strptime(deadline, "%Y-%m-%d").date()
                    if today < d <= today + timedelta(days=days):
                        upcoming.append(t)
                except ValueError:
                    pass
        return upcoming

    # ── リマインダー機能 ──

    def _load_reminders(self) -> list[dict]:
        """リマインダーファイルを読み込む"""
        if not _REMINDERS_FILE.exists():
            return []
        try:
            return json.loads(_REMINDERS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def _save_reminders(self, reminders: list[dict]) -> None:
        """リマインダーファイルに保存する"""
        _REMINDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _REMINDERS_FILE.write_text(
            json.dumps(reminders, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_reminder(self, message: str, remind_date: str, related_task_id: int | None = None) -> dict:
        """リマインダーを追加する

        Args:
            message: リマインドする内容
            remind_date: リマインド日（YYYY-MM-DD形式）
            related_task_id: 関連するタスクID（任意）
        """
        reminders = self._load_reminders()
        new_reminder = {
            "id": len(reminders) + 1,
            "message": message,
            "remind_date": remind_date,
            "related_task_id": related_task_id,
            "status": "pending",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        reminders.append(new_reminder)
        self._save_reminders(reminders)
        return new_reminder

    def add_reminder_relative(self, message: str, days_from_now: int) -> dict:
        """N日後のリマインダーを追加する"""
        remind_date = (datetime.now() + timedelta(days=days_from_now)).strftime("%Y-%m-%d")
        return self.add_reminder(message, remind_date)

    def get_due_reminders(self) -> list[dict]:
        """今日が期日のリマインダーを取得する"""
        reminders = self._load_reminders()
        today = datetime.now().strftime("%Y-%m-%d")
        return [
            r for r in reminders
            if r.get("remind_date") == today and r.get("status") == "pending"
        ]

    def get_overdue_reminders(self) -> list[dict]:
        """期日を過ぎた未通知リマインダーを取得する"""
        reminders = self._load_reminders()
        today = datetime.now().date()
        overdue = []
        for r in reminders:
            if r.get("status") != "pending":
                continue
            try:
                d = datetime.strptime(r["remind_date"], "%Y-%m-%d").date()
                if d < today:
                    overdue.append(r)
            except (ValueError, KeyError):
                pass
        return overdue

    def dismiss_reminder(self, reminder_id: int) -> dict | None:
        """リマインダーを通知済みにする"""
        reminders = self._load_reminders()
        for r in reminders:
            if r.get("id") == reminder_id:
                r["status"] = "done"
                r["dismissed"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                self._save_reminders(reminders)
                return r
        return None

    def get_all_reminders(self, include_done: bool = False) -> list[dict]:
        """全リマインダーを取得する"""
        reminders = self._load_reminders()
        if not include_done:
            reminders = [r for r in reminders if r.get("status") == "pending"]
        return sorted(reminders, key=lambda x: x.get("remind_date", ""))

    def _get_reminders_summary(self) -> str:
        """現在のリマインダー状況のサマリーを返す"""
        today_reminders = self.get_due_reminders()
        overdue_reminders = self.get_overdue_reminders()
        pending = self.get_all_reminders()

        if not pending and not today_reminders and not overdue_reminders:
            return "リマインダーはありません。"

        parts = []

        if overdue_reminders:
            parts.append(f"未通知リマインダー（期日超過）: {len(overdue_reminders)}件")
            for r in overdue_reminders:
                parts.append(f"  - {r['message']}（{r['remind_date']}）")

        if today_reminders:
            parts.append(f"今日のリマインダー: {len(today_reminders)}件")
            for r in today_reminders:
                parts.append(f"  - {r['message']}")

        if pending:
            future = [r for r in pending if r not in today_reminders and r not in overdue_reminders]
            if future:
                parts.append(f"予定されているリマインダー: {len(future)}件")

        return "\n".join(parts)
