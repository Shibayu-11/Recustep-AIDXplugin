#!/usr/bin/env python3
"""AIDX経営エージェントシステム - エントリーポイント

Usage:
    python main.py              # 対話モードで起動
    python main.py "質問内容"    # ワンショットで質問
"""

from __future__ import annotations

import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from aidx_agents.orchestrator import Orchestrator
from aidx_agents.finance import FinanceAgent
from aidx_agents.legal import LegalAgent
from aidx_agents.hr import HRAgent
from aidx_agents.secretary import SecretaryAgent
from aidx_agents.strategy import StrategyAgent

console = Console()

BANNER = """
[bold white on #111111]
  ╔═══════════════════════════════════════════════╗
  ║     AIDX 経営エージェントシステム v0.1        ║
  ║     Powered by Recustep × Claude API          ║
  ╚═══════════════════════════════════════════════╝
[/]

[dim]利用可能なAI部下:[/]
  [財務] 財務エージェント    [法務] 法務エージェント
  [労務] 労務エージェント    [秘書] 秘書エージェント
  [戦略] 経営戦略エージェント

[dim]終了: quit / exit / Ctrl+C[/]
"""


def build_orchestrator() -> Orchestrator:
    """全エージェントを初期化してオーケストレーターに登録する"""
    agents = {
        "finance": FinanceAgent(),
        "legal": LegalAgent(),
        "hr": HRAgent(),
        "secretary": SecretaryAgent(),
        "strategy": StrategyAgent(),
    }
    return Orchestrator(agents=agents)


def interactive_mode(orchestrator: Orchestrator) -> None:
    """対話モード"""
    console.print(BANNER)

    while True:
        try:
            user_input = console.input("\n[bold green]社長 >[/] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]お疲れ様でした。[/]")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "終了"):
            console.print("[dim]お疲れ様でした。[/]")
            break

        # 振り分け先を表示
        targets = orchestrator.classify(user_input)
        if targets:
            agent_names = [
                f"{orchestrator.agents[t].icon} {orchestrator.agents[t].name}"
                for t in targets if t in orchestrator.agents
            ]
            console.print(
                f"[dim]→ 振り分け先: {', '.join(agent_names)}[/]"
            )
        else:
            console.print("[dim]→ オーケストレーターが直接対応します[/]")

        with console.status("[bold cyan]分析中..."):
            response = orchestrator.route(user_input)

        console.print()
        console.print(Panel(
            Markdown(response),
            border_style="green",
            padding=(1, 2),
        ))


def oneshot_mode(orchestrator: Orchestrator, query: str) -> None:
    """ワンショットモード - 引数で渡された質問に回答して終了"""
    response = orchestrator.route(query)
    console.print(Markdown(response))


def main() -> None:
    orchestrator = build_orchestrator()

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        oneshot_mode(orchestrator, query)
    else:
        interactive_mode(orchestrator)


if __name__ == "__main__":
    main()
