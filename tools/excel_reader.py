"""Excel/CSV ファイル読み込みツール"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_excel(path: str | Path, sheet_name: str | int = 0) -> dict:
    """Excelファイルを読み込んでdict形式で返す

    Returns:
        {
            "filename": ファイル名,
            "sheet": シート名,
            "columns": カラム一覧,
            "rows": 行数,
            "data": DataFrameのdict表現,
            "summary": 数値列の基本統計量,
        }
    """
    path = Path(path)
    df = pd.read_excel(path, sheet_name=sheet_name)

    return {
        "filename": path.name,
        "sheet": sheet_name if isinstance(sheet_name, str) else f"Sheet{sheet_name}",
        "columns": list(df.columns),
        "rows": len(df),
        "data": df.to_dict(orient="records"),
        "summary": df.describe().to_dict() if not df.select_dtypes("number").empty else {},
    }


def read_csv(path: str | Path, encoding: str = "utf-8") -> dict:
    """CSVファイルを読み込んでdict形式で返す"""
    path = Path(path)

    # 日本語CSVはshift_jisの場合が多い
    for enc in [encoding, "shift_jis", "cp932", "utf-8-sig"]:
        try:
            df = pd.read_csv(path, encoding=enc)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    else:
        raise ValueError(f"ファイル {path.name} のエンコーディングを判定できませんでした")

    return {
        "filename": path.name,
        "columns": list(df.columns),
        "rows": len(df),
        "data": df.to_dict(orient="records"),
        "summary": df.describe().to_dict() if not df.select_dtypes("number").empty else {},
    }
