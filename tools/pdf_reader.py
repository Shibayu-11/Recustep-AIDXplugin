"""PDF ファイル読み込みツール"""

from __future__ import annotations

from pathlib import Path

import pdfplumber


def read_pdf(path: str | Path, max_pages: int | None = None) -> dict:
    """PDFファイルからテキストを抽出してdict形式で返す

    Returns:
        {
            "filename": ファイル名,
            "total_pages": 総ページ数,
            "pages": [{"page": ページ番号, "text": テキスト}, ...],
            "full_text": 全ページのテキスト結合,
        }
    """
    path = Path(path)
    pages = []

    with pdfplumber.open(path) as pdf:
        total = len(pdf.pages)
        limit = min(total, max_pages) if max_pages else total

        for i in range(limit):
            page = pdf.pages[i]
            text = page.extract_text() or ""
            pages.append({"page": i + 1, "text": text})

    full_text = "\n\n".join(p["text"] for p in pages)

    return {
        "filename": path.name,
        "total_pages": total,
        "pages": pages,
        "full_text": full_text,
    }
