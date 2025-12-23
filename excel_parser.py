#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal Excel/CSV parser with CLI.

Supports .xlsx, .xlsb, .csv/.txt inputs, optional chunked reading, and outputs to CSV/JSON/Parquet.
Requires: pandas, pyarrow, openpyxl, pyxlsb, chardet.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterator, List, Optional, Sequence, Union

import pandas as pd

try:
    import chardet  # type: ignore
except ImportError:  # pragma: no cover - handled gracefully
    chardet = None

# ----------------------- I/O helpers ----------------------- #


def detect_encoding(path: Union[str, Path], sample: int = 1_000_000) -> str:
    """Detect CSV encoding using chardet, fallback to utf-8."""
    if chardet is None:
        return "utf-8"
    with open(path, "rb") as handle:
        raw = handle.read(sample)
    detected = chardet.detect(raw).get("encoding") or "utf-8"
    return detected


def _yield_dataframe(df: pd.DataFrame, chunksize: Optional[int]) -> Iterator[pd.DataFrame]:
    if chunksize:
        for start in range(0, len(df), chunksize):
            yield df.iloc[start : start + chunksize]
    else:
        yield df


def read_xlsx(
    path: Union[str, Path],
    sheet: Optional[Union[str, int]],
    header: Optional[int],
    usecols: Optional[Union[str, Sequence]],
    chunksize: Optional[int],
) -> Iterator[pd.DataFrame]:
    kwargs = dict(
        sheet_name=sheet if sheet is not None else 0,
        header=header,
        usecols=usecols,
        dtype_backend="pyarrow",
        engine="openpyxl",
    )
    df = pd.read_excel(path, **kwargs)
    yield from _yield_dataframe(df, chunksize)


def read_xlsb(
    path: Union[str, Path],
    sheet: Optional[Union[str, int]],
    header: Optional[int],
    usecols: Optional[Union[str, Sequence]],
    chunksize: Optional[int],
) -> Iterator[pd.DataFrame]:
    kwargs = dict(
        sheet_name=sheet if sheet is not None else 0,
        header=header,
        usecols=usecols,
        dtype_backend="pyarrow",
        engine="pyxlsb",
    )
    df = pd.read_excel(path, **kwargs)
    yield from _yield_dataframe(df, chunksize)


def read_csv_stream(
    path: Union[str, Path],
    header: Optional[int],
    usecols: Optional[Union[str, Sequence]],
    chunksize: Optional[int],
    encoding: Optional[str],
) -> Iterator[pd.DataFrame]:
    enc = encoding or detect_encoding(path)
    kwargs = dict(header=header, usecols=usecols, encoding=enc, dtype_backend="pyarrow")

    if chunksize:
        kwargs["chunksize"] = chunksize
        for chunk in pd.read_csv(path, **kwargs):
            yield chunk
    else:
        df = pd.read_csv(path, **kwargs)
        yield df


def read_any(
    path: Union[str, Path],
    sheet: Optional[Union[str, int]],
    header: Optional[int],
    usecols: Optional[Union[str, Sequence]],
    chunksize: Optional[int],
    encoding: Optional[str] = None,
) -> Iterator[pd.DataFrame]:
    ext = Path(path).suffix.lower()
    if ext == ".xlsx":
        return read_xlsx(path, sheet, header, usecols, chunksize)
    if ext == ".xlsb":
        return read_xlsb(path, sheet, header, usecols, chunksize)
    if ext in {".csv", ".txt"}:
        return read_csv_stream(path, header, usecols, chunksize, encoding)
    raise ValueError(f"Unsupported file extension: {ext}")


# ----------------------- Writers ----------------------- #


def write_csv(stream: Iterator[pd.DataFrame], out: str) -> None:
    first = True
    for df in stream:
        df.to_csv(
            sys.stdout if out == "-" else out,
            index=False,
            header=first,
            mode="w" if first else "a",
            lineterminator="\n",
        )
        first = False


def write_json(stream: Iterator[pd.DataFrame], out: str) -> None:
    if out != "-" and Path(out).exists():
        Path(out).unlink()

    def emit(df: pd.DataFrame) -> None:
        records = json.loads(df.to_json(orient="records"))
        dest = sys.stdout if out == "-" else open(out, "a", encoding="utf-8")
        try:
            for rec in records:
                line = json.dumps(rec, ensure_ascii=False)
                dest.write(line + "\n")
        finally:
            if dest is not sys.stdout:
                dest.close()

    for chunk in stream:
        emit(chunk)


def write_parquet(stream: Iterator[pd.DataFrame], out: str) -> None:
    if out == "-":
        raise ValueError("Parquet output requires a file path (stdout is not supported).")
    dfs: List[pd.DataFrame] = [df for df in stream]
    if not dfs:
        pd.DataFrame().to_parquet(out, index=False)
    else:
        pd.concat(dfs, ignore_index=True).to_parquet(out, index=False)


# ----------------------- CLI ----------------------- #


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Universal Excel/CSV parser → CSV/JSON/Parquet (chunk-friendly)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--path", required=True, help="Input file (.xlsx|.xlsb|.csv|.txt)")
    parser.add_argument("--sheet", help="Sheet name or index for Excel (default: 0)", default=None)
    parser.add_argument("--header", type=int, help="Row index for header (0-based); use -1 for no header", default=0)
    parser.add_argument("--usecols", help="Excel range (e.g. A:F) or JSON list of columns", default=None)
    parser.add_argument("--chunksize", type=int, help="Chunk size for streaming reads", default=None)
    parser.add_argument("--encoding", help="CSV encoding (auto-detected if omitted)", default=None)
    parser.add_argument("--to", choices=["csv", "json", "parquet"], required=True, help="Output format")
    parser.add_argument("--out", required=True, help="Output path or '-' for stdout (CSV/JSON only)")
    return parser.parse_args(argv)


def normalize_sheet(sheet_value: Optional[str]) -> Optional[Union[str, int]]:
    if sheet_value is None:
        return None
    try:
        return int(sheet_value)
    except (TypeError, ValueError):
        return sheet_value


def normalize_usecols(usecols: Optional[str]) -> Optional[Union[str, List[str]]]:
    if not usecols:
        return None
    if usecols.startswith("[") and usecols.endswith("]"):
        try:
            parsed = json.loads(usecols)
            return parsed
        except json.JSONDecodeError:
            return usecols
    return usecols


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)

    header = None if args.header == -1 else args.header
    sheet = normalize_sheet(args.sheet)
    usecols = normalize_usecols(args.usecols)

    try:
        stream = read_any(
            path=args.path,
            sheet=sheet,
            header=header,
            usecols=usecols,
            chunksize=args.chunksize,
            encoding=args.encoding,
        )

        if args.to == "csv":
            write_csv(stream, args.out)
        elif args.to == "json":
            write_json(stream, args.out)
        else:
            write_parquet(stream, args.out)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

