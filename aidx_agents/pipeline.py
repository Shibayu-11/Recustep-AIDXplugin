"""エージェント間連携パイプライン — 複数エージェントを順序立てて連携させる"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .base import BaseAgent


@dataclass
class PipelineStep:
    """パイプラインの1ステップ"""
    agent_key: str
    prompt_template: str  # {input} と {prev_result} が使える
    description: str = ""


# ── 定義済みパイプライン ──

LOAN_PREP_PIPELINE = [
    PipelineStep(
        agent_key="finance",
        prompt_template="以下の企業情報を基に、銀行融資の審査で見られる財務指標を分析してください。\n\n{input}",
        description="財務分析（融資審査の観点）",
    ),
    PipelineStep(
        agent_key="strategy",
        prompt_template="以下の財務分析結果を基に、銀行に提出する事業計画書のドラフトを作成してください。\n\n前段の分析結果:\n{prev_result}\n\n元の依頼:\n{input}",
        description="事業計画書ドラフト作成",
    ),
    PipelineStep(
        agent_key="secretary",
        prompt_template="以下の財務分析と事業計画書を、銀行担当者に提出できる品質の報告書としてまとめてください。\n\n{prev_result}",
        description="提出用レポート整形",
    ),
]

QUARTERLY_REVIEW_PIPELINE = [
    PipelineStep(
        agent_key="finance",
        prompt_template="今四半期の財務状況を分析してください。\n\n{input}",
        description="四半期財務分析",
    ),
    PipelineStep(
        agent_key="hr",
        prompt_template="以下の財務分析結果を踏まえ、人材・労務面の状況と課題を分析してください。\n\n{prev_result}\n\n追加情報:\n{input}",
        description="人材・労務分析",
    ),
    PipelineStep(
        agent_key="strategy",
        prompt_template="以下の財務分析と人材分析を踏まえ、来四半期の戦略オプションを3つ提示してください。\n\n{prev_result}",
        description="戦略オプション提示",
    ),
]

CONTRACT_FULL_REVIEW_PIPELINE = [
    PipelineStep(
        agent_key="legal",
        prompt_template="以下の契約書をレビューし、リスク箇所を全て抽出してください。\n\n{input}",
        description="法務リスク分析",
    ),
    PipelineStep(
        agent_key="finance",
        prompt_template="以下の契約書レビュー結果を基に、財務面のリスク（損害賠償上限、支払条件、違約金等）を評価してください。\n\n{prev_result}",
        description="財務リスク評価",
    ),
    PipelineStep(
        agent_key="secretary",
        prompt_template="以下の法務・財務リスク分析を、経営者向けの簡潔なサマリーにまとめてください。リスクレベルごとに整理し、推奨アクションを付けてください。\n\n{prev_result}",
        description="経営者向けサマリー",
    ),
]

NEW_BUSINESS_PIPELINE = [
    PipelineStep(
        agent_key="strategy",
        prompt_template="以下の新規事業アイデアについて、SWOT分析と市場規模の概算を行ってください。\n\n{input}",
        description="市場分析・SWOT",
    ),
    PipelineStep(
        agent_key="finance",
        prompt_template="以下の市場分析を基に、3年間の収支シミュレーションを作成してください。\n\n{prev_result}\n\n事業概要:\n{input}",
        description="収支シミュレーション",
    ),
    PipelineStep(
        agent_key="legal",
        prompt_template="以下の新規事業について、法務・コンプライアンス上の留意点を洗い出してください。\n\n{prev_result}\n\n事業概要:\n{input}",
        description="法務チェック",
    ),
]

# パイプライン名→定義のマッピング
PIPELINES: dict[str, list[PipelineStep]] = {
    "loan-prep": LOAN_PREP_PIPELINE,
    "quarterly-review": QUARTERLY_REVIEW_PIPELINE,
    "contract-full-review": CONTRACT_FULL_REVIEW_PIPELINE,
    "new-business": NEW_BUSINESS_PIPELINE,
}


def run_pipeline(
    pipeline: list[PipelineStep],
    agents: dict[str, BaseAgent],
    user_input: str,
    on_step: Callable[[int, str, str], None] | None = None,
) -> str:
    """パイプラインを順番に実行し、最終結果を返す

    Args:
        pipeline: PipelineStepのリスト
        agents: エージェント名→インスタンスのdict
        user_input: 最初のユーザー入力
        on_step: ステップ完了時のコールバック (step_num, description, result)

    Returns:
        最終ステップの出力
    """
    prev_result = ""
    all_results: list[str] = []

    for i, step in enumerate(pipeline):
        if step.agent_key not in agents:
            continue

        agent = agents[step.agent_key]
        prompt = step.prompt_template.format(
            input=user_input,
            prev_result=prev_result,
        )

        result = agent.ask(prompt)
        prev_result = result
        all_results.append(f"## Step {i+1}: {step.description}\n\n{result}")

        if on_step:
            on_step(i + 1, step.description, result)

    return "\n\n---\n\n".join(all_results)
