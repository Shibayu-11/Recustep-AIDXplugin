"""PDF ファイル読み込みツール

2段階の読み取り戦略:
1. OpenDataLoader PDF（推奨）— ベンチマーク1位。テーブル・スキャン・複雑レイアウト全対応
2. pdfplumber（フォールバック）— Java不要。軽量だが精度は劣る

OpenDataLoaderが使える場合は自動的にそちらを使う。
Java 11+が必要。入ってなければpdfplumberにフォールバック。
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

# OpenDataLoader が使えるか判定
_HAS_JAVA = shutil.which("java") is not None

try:
    import opendataloader_pdf
    _HAS_OPENDATALOADER = True
except ImportError:
    _HAS_OPENDATALOADER = False


def read_pdf(path: str | Path, max_pages: int | None = None) -> dict:
    """PDFファイルからテキストと表を抽出してdict形式で返す

    OpenDataLoaderが使える場合はそちらを優先。なければpdfplumberにフォールバック。

    Returns:
        {
            "filename": ファイル名,
            "total_pages": 総ページ数,
            "full_text": 全テキスト,
            "markdown": Markdown形式の全内容,
            "tables": 抽出された表のリスト,
            "extraction_method": 使用した抽出エンジン,
        }
    """
    path = Path(path)

    if _HAS_OPENDATALOADER and _HAS_JAVA:
        return _read_with_opendataloader(path, max_pages)
    else:
        return _read_with_pdfplumber(path, max_pages)


def _read_with_opendataloader(path: Path, max_pages: int | None = None) -> dict:
    """OpenDataLoader PDFで読み取り（高精度）"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Markdown + JSON で出力
        kwargs = {
            "input_path": [str(path)],
            "output_dir": tmpdir,
            "format": "markdown",
        }

        if max_pages:
            kwargs["pages"] = f"1-{max_pages}"

        opendataloader_pdf.convert(**kwargs)

        # 出力されたMarkdownファイルを読み込む
        md_files = list(Path(tmpdir).rglob("*.md"))
        if md_files:
            markdown = md_files[0].read_text(encoding="utf-8")
        else:
            markdown = ""

        # ページ数をカウント
        try:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                total_pages = len(pdf.pages)
        except Exception:
            total_pages = markdown.count("---") + 1  # 概算

    # テーブルを抽出（Markdownのテーブル記法から）
    tables = _extract_tables_from_markdown(markdown)

    return {
        "filename": path.name,
        "total_pages": total_pages,
        "full_text": markdown,
        "markdown": markdown,
        "tables": tables,
        "has_tables": len(tables) > 0,
        "extraction_method": "opendataloader",
    }


def _read_with_pdfplumber(path: Path, max_pages: int | None = None) -> dict:
    """pdfplumberで読み取り（フォールバック）"""
    import pdfplumber

    pages_text = []
    tables = []

    with pdfplumber.open(path) as pdf:
        total = len(pdf.pages)
        limit = min(total, max_pages) if max_pages else total

        for i in range(limit):
            page = pdf.pages[i]

            # テーブル抽出
            page_tables = _extract_tables_pdfplumber(page)
            tables.extend(page_tables)

            # テキスト抽出
            text = page.extract_text() or ""
            pages_text.append(text)

    full_text = "\n\n".join(pages_text)

    # Markdown化
    markdown_parts = []
    for i, text in enumerate(pages_text):
        markdown_parts.append(f"## Page {i+1}\n\n{text}")
    markdown = "\n\n".join(markdown_parts)

    return {
        "filename": path.name,
        "total_pages": total,
        "full_text": full_text,
        "markdown": markdown,
        "tables": tables,
        "has_tables": len(tables) > 0,
        "extraction_method": "pdfplumber (fallback)",
    }


def _extract_tables_pdfplumber(page) -> list[dict]:
    """pdfplumberでページからテーブルを抽出"""
    tables = []
    try:
        for strategy in [
            {"vertical_strategy": "lines", "horizontal_strategy": "lines"},
            {"vertical_strategy": "text", "horizontal_strategy": "text"},
        ]:
            raw_tables = page.extract_tables(strategy)
            for raw_table in (raw_tables or []):
                if not raw_table or len(raw_table) < 2:
                    continue
                headers = [str(c or "").strip() for c in raw_table[0]]
                rows = [[str(c or "").strip() for c in row] for row in raw_table[1:] if any(c for c in row)]
                if headers and rows:
                    tables.append({
                        "headers": headers,
                        "rows": rows,
                        "markdown": _table_to_markdown(headers, rows),
                    })
            if tables:
                break
    except Exception:
        pass
    return tables


def _extract_tables_from_markdown(md: str) -> list[dict]:
    """Markdownテキストからテーブルを抽出"""
    tables = []
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("|") and i + 1 < len(lines) and "---" in lines[i + 1]:
            # テーブル開始
            headers = [c.strip() for c in line.strip("|").split("|")]
            i += 2  # ヘッダー + セパレータをスキップ
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(row)
                i += 1
            if headers and rows:
                tables.append({
                    "headers": headers,
                    "rows": rows,
                    "markdown": _table_to_markdown(headers, rows),
                })
        else:
            i += 1
    return tables


def _table_to_markdown(headers: list[str], rows: list[list[str]]) -> str:
    """テーブルをMarkdown形式に変換"""
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        padded = row + [""] * (len(headers) - len(row))
        lines.append("| " + " | ".join(padded[:len(headers)]) + " |")
    return "\n".join(lines)


def read_pdf_tables_only(path: str | Path) -> list[dict]:
    """PDFから表だけを抽出する（決算書向け）"""
    result = read_pdf(path)
    return result["tables"]


def pdf_to_markdown(path: str | Path) -> str:
    """PDFの内容を全てMarkdown形式で返す"""
    result = read_pdf(path)
    return result["markdown"]


def get_extraction_engine() -> str:
    """現在使用可能な抽出エンジンを返す"""
    if _HAS_OPENDATALOADER and _HAS_JAVA:
        return "opendataloader (high accuracy)"
    else:
        reasons = []
        if not _HAS_OPENDATALOADER:
            reasons.append("opendataloader-pdf not installed")
        if not _HAS_JAVA:
            reasons.append("Java not found")
        return f"pdfplumber (fallback: {', '.join(reasons)})"
