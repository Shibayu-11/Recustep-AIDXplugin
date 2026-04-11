"""HTML レポート生成ツール"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def _get_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=True,
    )


def render_html(template_name: str, context: dict) -> str:
    """テンプレートにコンテキストを流し込んでHTML文字列を返す

    Args:
        template_name: テンプレートファイル名（例: "report.html"）
        context: テンプレートに渡す変数のdict

    Returns:
        レンダリングされたHTML文字列
    """
    env = _get_env()
    template = env.get_template(template_name)
    return template.render(**context)


def save_html(template_name: str, context: dict, output_path: str | Path) -> Path:
    """テンプレートをレンダリングしてファイルに保存する

    Returns:
        保存先のPathオブジェクト
    """
    html = render_html(template_name, context)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path
