#!/usr/bin/env python3
"""
Merge Logs Insights Excel exports into a single Excel file WITHOUT sorting rows.
File blocks are appended in chronological order: OLDEST file first → ... → LATEST file last.

- 'Oldest'/'Latest' determined from END timestamp in filename:
    logs-insights-results(feb15th124000_to_feb16th055500).xlsx
- Prompts you to enter which columns to keep (interactive), or pass via --columns.
- Does NOT sort by Count or any other column. Rows are kept exactly as they appear.

Output: logs-insights-results.xlsx (unless overridden with --output)

Usage examples:
  python merge_log_chrono.py
  python merge_log_chrono.py --columns "Timestamp,Message,Count"
  python merge_log_chrono.py --sheet 0
  python merge_log_chrono.py --folder "C:\\path\\to\\files" --output "logs-insights-results.xlsx"
"""

import argparse
import os
import re
from datetime import datetime
from typing import Optional, Tuple, List

import pandas as pd

# --- Filename parsing ---

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}

FILENAME_REGEX = re.compile(
    r"""^logs-insights-results\(
        (?P<start_mon>[a-z]{3})(?P<start_day>\d{1,2})[a-z]{2}(?P<start_h>\d{2})(?P<start_m>\d{2})(?P<start_s>\d{2})
        _to_
        (?P<end_mon>[a-z]{3})(?P<end_day>\d{1,2})[a-z]{2}(?P<end_h>\d{2})(?P<end_m>\d{2})(?P<end_s>\d{2})
        \)\.xlsx$""",
    re.IGNORECASE | re.VERBOSE
)

def parse_end_ts_from_filename(filename: str) -> Optional[datetime]:
    """
    Parse END timestamp from filename like:
    logs-insights-results(feb15th124000_to_feb16th055500).xlsx
    Returns a datetime (assumes current year) or None.
    """
    base = os.path.basename(filename)
    m = FILENAME_REGEX.match(base)
    if not m:
        return None
    try:
        end_mon_str = m.group("end_mon").lower()
        end_day = int(m.group("end_day"))
        end_h = int(m.group("end_h"))
        end_mi = int(m.group("end_m"))
        end_s = int(m.group("end_s"))
        end_mon = MONTHS[end_mon_str]
        year = datetime.now().year
        return datetime(year, end_mon, end_day, end_h, end_mi, end_s)
    except Exception:
        return None

# --- File collection and ordering ---

def collect_files(folder: str, output_name: str) -> List[str]:
    files = []
    for entry in os.listdir(folder):
        if not entry.lower().endswith(".xlsx"):
            continue
        if not entry.startswith("logs-insights-results("):
            continue
        if entry == output_name:
            continue  # avoid including output file itself
        files.append(os.path.join(folder, entry))
    return files

def order_files_oldest_first(files: List[str]) -> List[str]:
    """
    Order files: OLDEST (by END timestamp in filename) first.
    If a file cannot be parsed, place it using filesystem mtime (oldest first).
    """
    parsed = []
    unparsed = []
    for f in files:
        ts = parse_end_ts_from_filename(f)
        if ts is not None:
            parsed.append((f, ts))
        else:
            # fallback: use mtime
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(f))
            except Exception:
                mtime = datetime.max  # if unknown, push to end
            unparsed.append((f, mtime))

    # Oldest first => ascending
    parsed.sort(key=lambda x: x[1])      # ascending by parsed end-ts
    unparsed.sort(key=lambda x: x[1])    # ascending by mtime

    # Keep parsed first (strict filename-based), then any unparsed
    return [f for f, _ in parsed] + [f for f, _ in unparsed]

# --- Excel reading helpers ---

def _read_excel_sheet_as_df(path: str, sheet) -> pd.DataFrame:
    """
    Always return a DataFrame from pd.read_excel.
    - If sheet is None: use first sheet (0) to avoid dict return.
    - If a dict is returned, take the first sheet.
    """
    sheet_to_use = 0 if sheet is None else sheet
    obj = pd.read_excel(path, sheet_name=sheet_to_use, engine="openpyxl")
    if isinstance(obj, dict):  # safety
        first_key = next(iter(obj))
        return obj[first_key]
    return obj

# --- Interactive prompt ---

def prompt_columns_interactive(sample_df: pd.DataFrame) -> List[str]:
    print("\n🔎 Columns detected in a sample file:")
    print(", ".join([str(c) for c in sample_df.columns]))
    user = input(
        "\nEnter columns to keep (comma-separated), or press Enter to keep ALL: "
    ).strip()
    if not user:
        return list(sample_df.columns)
    cols = [c.strip() for c in user.split(",") if c.strip()]
    return cols

# --- Merge core ---

def merge_excels(files: List[str], sheet, columns: Optional[List[str]], add_source: bool) -> pd.DataFrame:
    """
    Read each file (in the provided order) and append rows EXACTLY as they are.
    No sorting is applied to rows. Optionally add a source_file column.
    """
    frames: List[pd.DataFrame] = []

    for idx, f in enumerate(files, start=1):
        try:
            df = _read_excel_sheet_as_df(f, sheet)
        except Exception as e:
            print(f"⚠️  Skipping '{os.path.basename(f)}' due to read error: {e}")
            continue

        if columns is not None:
            missing = [c for c in columns if c not in df.columns]
            if missing:
                print(f"⚠️  File '{os.path.basename(f)}' is missing columns: {missing}. They will be filled with NaN.")
            df = df.reindex(columns=columns)

        if add_source:
            df.insert(0, "source_file", os.path.basename(f))

        frames.append(df)

        print(f"✓ Loaded {idx}/{len(files)}: {os.path.basename(f)}  ({len(df)} rows)")

    if not frames:
        raise RuntimeError("No valid input files to merge.")

    # Concatenate in the given file order (oldest -> latest). No row sorting.
    merged = pd.concat(frames, ignore_index=True)
    return merged

# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="Merge Logs Insights Excel exports (oldest → latest; no row sorting).")
    parser.add_argument("--folder", type=str, default=".", help="Folder containing the Excel files. Default: current directory")
    parser.add_argument("--output", type=str, default="logs-insights-results.xlsx", help="Output Excel filename.")
    parser.add_argument("--sheet", type=str, default=None, help="Sheet name or index to read (default: first sheet).")
    parser.add_argument("--columns", type=str, default=None,
                        help="Comma-separated list of columns to keep. If omitted, you will be prompted (interactive).")
    parser.add_argument("--add-source-col", action="store_true",
                        help="Add a 'source_file' column to show where each row came from.")
    args = parser.parse_args()

    # Collect and strictly order files by END timestamp (OLDEST -> LATEST)
    files = collect_files(args.folder, args.output)
    ordered_files = order_files_oldest_first(files)

    if not ordered_files:
        raise SystemExit(f"No matching files found in: {os.path.abspath(args.folder)}")

    print(f"\nFound {len(ordered_files)} file(s). Merge order (oldest → latest):")
    for i, f in enumerate(ordered_files, start=1):
        end_ts = parse_end_ts_from_filename(f)
        ts_str = end_ts.isoformat(sep=" ") if end_ts else f"mtime={datetime.fromtimestamp(os.path.getmtime(f)).isoformat(sep=' ')}"
        print(f"  {i:2d}. {os.path.basename(f)}  [{ts_str}]")

    # Columns to keep
    columns_list: Optional[List[str]] = None
    if args.columns is not None:
        columns_list = [c.strip() for c in args.columns.split(",") if c.strip()]
    else:
        try:
            sample_for_prompt = _read_excel_sheet_as_df(ordered_files[0], args.sheet)
            if sample_for_prompt is not None and not sample_for_prompt.empty:
                columns_list = prompt_columns_interactive(sample_for_prompt)
            else:
                print("⚠️  Could not preview columns; proceeding to include ALL columns found in each file.")
        except Exception as e:
            print(f"⚠️  Could not preview columns due to error: {e}. Including ALL columns.")
            columns_list = None

    # Merge with NO sorting of rows
    merged_df = merge_excels(
        ordered_files,
        sheet=args.sheet,
        columns=columns_list,
        add_source=args.add_source_col
    )

    # Write output
    out_path = os.path.join(args.folder, args.output)
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        merged_df.to_excel(writer, index=False, sheet_name="Merged")

    print(f"\n✅ Done. Wrote {len(merged_df)} rows to: {out_path}")
    print("   Order: Oldest file rows first → Latest file rows last. No row sorting applied.")

if __name__ == "__main__":
    main()