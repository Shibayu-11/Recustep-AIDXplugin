"""Excel/CSV ファイル読み込みツール

決算書・勤怠表・売上データ等の日本企業で使われるExcelに対応:
- 複数シート対応（全シート読み込み可能）
- 結合セルの自動展開
- 日本語ヘッダー対応
- Shift_JIS / CP932 / UTF-8 自動判定
- 数値の自動フォーマット（円、%）
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import openpyxl


def read_excel(path: str | Path, sheet_name: str | int | None = None) -> dict:
    """Excelファイルを読み込んでdict形式で返す

    Args:
        path: ファイルパス
        sheet_name: シート名 or インデックス。Noneなら全シート読み込み

    Returns:
        {
            "filename": ファイル名,
            "sheets": [シート情報のリスト],
            "sheet_names": 全シート名,
            "total_sheets": シート数,
        }
    """
    path = Path(path)

    # openpyxlで直接読む（結合セル対応）
    wb = openpyxl.load_workbook(path, data_only=True)
    sheet_names = wb.sheetnames

    if sheet_name is not None:
        # 特定シートのみ
        targets = [sheet_name] if isinstance(sheet_name, str) else [sheet_names[sheet_name]]
    else:
        # 全シート
        targets = sheet_names

    sheets = []
    for name in targets:
        ws = wb[name]
        sheet_data = _extract_sheet(ws, name)
        sheets.append(sheet_data)

    wb.close()

    return {
        "filename": path.name,
        "sheets": sheets,
        "sheet_names": sheet_names,
        "total_sheets": len(sheet_names),
    }


def _extract_sheet(ws, name: str) -> dict:
    """ワークシートからデータを抽出"""
    # 結合セルを展開
    merged_cells = {}
    for merge_range in ws.merged_cells.ranges:
        top_left_value = ws.cell(merge_range.min_row, merge_range.min_col).value
        for row in range(merge_range.min_row, merge_range.max_row + 1):
            for col in range(merge_range.min_col, merge_range.max_col + 1):
                merged_cells[(row, col)] = top_left_value

    # 全データを読み込み
    rows = []
    for row in ws.iter_rows(min_row=1, values_only=False):
        row_data = []
        for cell in row:
            val = merged_cells.get((cell.row, cell.column), cell.value)
            row_data.append(val)
        rows.append(row_data)

    if not rows:
        return {"sheet": name, "columns": [], "rows": 0, "data": [], "summary": {}, "markdown": ""}

    # ヘッダー行を検出（最初の非空行）
    header_idx = 0
    for i, row in enumerate(rows):
        if any(v is not None for v in row):
            header_idx = i
            break

    headers = [str(v) if v is not None else f"列{j+1}" for j, v in enumerate(rows[header_idx])]
    data_rows = rows[header_idx + 1:]

    # DataFrameに変換
    records = []
    for row in data_rows:
        if any(v is not None for v in row):
            record = {}
            for j, val in enumerate(row):
                if j < len(headers):
                    record[headers[j]] = val
            records.append(record)

    df = pd.DataFrame(records)

    # 基本統計量
    summary = {}
    numeric_cols = df.select_dtypes("number")
    if not numeric_cols.empty:
        summary = numeric_cols.describe().to_dict()

    # Markdown変換
    markdown = _df_to_markdown(df, headers)

    return {
        "sheet": name,
        "columns": headers,
        "rows": len(records),
        "data": records,
        "summary": summary,
        "markdown": markdown,
    }


def _df_to_markdown(df: pd.DataFrame, headers: list[str]) -> str:
    """DataFrameをMarkdown表に変換"""
    if df.empty:
        return ""

    lines = []
    # ヘッダー行で使う列だけ
    cols = [h for h in headers if h in df.columns]
    if not cols:
        cols = list(df.columns)

    lines.append("| " + " | ".join(str(c) for c in cols) + " |")
    lines.append("| " + " | ".join(["---"] * len(cols)) + " |")

    for _, row in df.head(50).iterrows():  # 最大50行
        values = []
        for c in cols:
            val = row.get(c, "")
            if isinstance(val, float):
                if val == int(val):
                    values.append(f"{int(val):,}")
                else:
                    values.append(f"{val:,.1f}")
            elif val is None:
                values.append("")
            else:
                values.append(str(val))
        lines.append("| " + " | ".join(values) + " |")

    if len(df) > 50:
        lines.append(f"| ... | ({len(df) - 50}行省略) |")

    return "\n".join(lines)


def read_csv(path: str | Path, encoding: str = "utf-8") -> dict:
    """CSVファイルを読み込んでdict形式で返す"""
    path = Path(path)

    # 日本語CSVはshift_jisの場合が多い
    for enc in [encoding, "shift_jis", "cp932", "utf-8-sig", "euc-jp", "iso-2022-jp"]:
        try:
            df = pd.read_csv(path, encoding=enc)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    else:
        raise ValueError(f"ファイル {path.name} のエンコーディングを判定できませんでした")

    headers = list(df.columns)
    markdown = _df_to_markdown(df, headers)

    return {
        "filename": path.name,
        "columns": headers,
        "rows": len(df),
        "data": df.to_dict(orient="records"),
        "summary": df.describe().to_dict() if not df.select_dtypes("number").empty else {},
        "markdown": markdown,
    }


def list_excel_sheets(path: str | Path) -> list[str]:
    """Excelファイルのシート名一覧を返す"""
    wb = openpyxl.load_workbook(path, read_only=True)
    names = wb.sheetnames
    wb.close()
    return names
