"""全エージェント共通の基底クラス"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path

import anthropic
from dotenv import load_dotenv

# プロジェクトルートの.envを読み込み
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

DEFAULT_MODEL = os.getenv("AIDX_MODEL", "claude-sonnet-4-20250514")


class BaseAgent(ABC):
    """AIDX エージェント基底クラス

    全ての専門エージェントはこのクラスを継承する。
    Claude APIとの通信、システムプロンプト管理、出力フォーマットを共通化。
    """

    name: str = "base"
    description: str = ""
    icon: str = ""

    def __init__(self, model: str | None = None):
        self.model = model or DEFAULT_MODEL
        self.client = anthropic.Anthropic()
        self.conversation_history: list[dict] = []

    @abstractmethod
    def system_prompt(self) -> str:
        """エージェント固有のシステムプロンプトを返す"""
        ...

    def ask(self, user_message: str, *, max_tokens: int = 4096) -> str:
        """ユーザーメッセージを送信し、エージェントの応答を返す"""
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
        })

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system_prompt(),
            messages=self.conversation_history,
        )

        assistant_text = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_text,
        })

        return assistant_text

    def reset(self) -> None:
        """会話履歴をリセットする"""
        self.conversation_history.clear()

    def __repr__(self) -> str:
        return f"{self.icon} {self.name}（{self.description}）"
