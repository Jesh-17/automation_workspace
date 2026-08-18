
#!/usr/bin/env python3
"""
Counts from sub_dar_refined.xlsx based on user-provided columns (space-separated),
preserving exact cell text, never dropping rows, with special handling for statusCode and '|'.

Adds a grand total row at the bottom of every counts sheet:
- 'Count' column shows: "Total: <sum>"
- All other columns are left blank.

Rules (unchanged):
- Ask ONLY for the columns (space-separated). The order is the grouping order.
- If a cell does NOT contain '|', keep it EXACTLY AS-IS and replicate across exploded rows.
- If a cell DOES contain '|':
    * statusCode -> RTL alignment.
    * Other selected columns -> LTR alignment, then REVERSE to pair opposite to status.
      Example:
        statusCode: "400 | 500"
        message       : "A | B"
      Produces:
        500 -> A
        400 -> B
- If 'statusCode' is among selected columns:
    * Split & pair as above (no drops).
    * Infer HTTP class (0xx..9xx) from the status TEXT; if cannot parse -> 'unknown'.
    * Output: one sheet per present class: counts_0xx, counts_2xx, counts_4xx, counts_5xx, ..., counts_unknown.
- If 'statusCode' is NOT among selected columns:
    * DO NOT split anything. Count exact raw strings as-is.
    * Output: a single sheet: req_col_count.

Null/empty handling (EXACT):
- Literal "null" remains "null".
- Blank cells remain blank in output.
- No trimming or type coercion. No rows are dropped.

Defaults:
- Input: sub_dar_refined.xlsx (first sheet)
- Output: sub_dar_each_counts.xlsx
- Sort: Count desc, then by keys asc.
"""

import re
import shlex
from typing import List

import pandas as pd

INPUT_FILE = "sub_dar_refined.xlsx"
SHEET = 0
OUTPUT_FILE = "sub_dar_each_counts.xlsx"
STATUS_COL = "statusCode"
PIPE = '|'

# ---------------- Utilities ----------------

def parse_columns_input(user_text: str) -> List[str]:
    """Parse columns as space-separated; allow quotes; normalize commas to spaces."""
    text = (user_text or '').strip()
    if not text:
        return []
    text = text.replace(',', ' ')
    return [c.strip() for c in shlex.split(text) if c.strip()]

def split_preserve(val: str) -> List[str]:
    """Split by '|' preserving exact text (no trimming). Blanks are '' and remain blank."""
    s = '' if val is None else str(val)
    return s.split(PIPE)

def cell_has_pipe(val: str) -> bool:
    s = '' if val is None else str(val)
    return PIPE in s

def infer_status_class_digit_from_text(v_text: str):
    """Return 'kxx' from any 1-3 digit chunk in the text; else 'unknown'."""
    s = '' if v_text is None else str(v_text)
    m = re.search(r'\b(\d{1,3})\b', s)
    if not m:
        return 'unknown'
    try:
        code = int(m.group(1))
        if code < 0:
            return 'unknown'
        return f"{code // 100}xx"
    except Exception:
        return 'unknown'

def aggregate_counts(df: pd.DataFrame, by_cols: List[str]) -> pd.DataFrame:
    """Group by given columns in fixed order; sort by Count desc then keys asc."""
    grp = df.groupby(by_cols, dropna=False).size().reset_index(name='Count')
    grp = grp.sort_values(by=['Count'] + by_cols, ascending=[False] + [True]*len(by_cols))
    return grp

def add_total_row(counts_df: pd.DataFrame) -> pd.DataFrame:
    """Append a final row where 'Count' shows 'Total: <sum>' and other columns are blank."""
    total = counts_df['Count'].sum()
    total_row = {col: '' for col in counts_df.columns}
    total_row['Count'] = f"Total: {total}"
    return pd.concat([counts_df, pd.DataFrame([total_row])], ignore_index=True)

# ---------------- Explode with opposite pairing (when status is selected) ----------------

def explode_with_opposite_pairing(df: pd.DataFrame, by_columns: List[str]) -> pd.DataFrame:
    """
    Split selected columns on '|', align, and explode without dropping rows.

    - If NO '|' in a cell -> replicate exact value across segments.
    - If HAS '|':
        * STATUS_COL: Right-align (pad LEFT with '').
        * Others    : Left-align (pad RIGHT with ''), then REVERSE (opposite pairing).
    """
    cols_present = [c for c in by_columns if c in df.columns]
    missing = [c for c in by_columns if c not in df.columns]
    if missing:
        raise SystemExit(f"Error: These columns are missing in the file: {missing}")

    work = df[cols_present].copy()

    aligned_rows = []
    for _, row in work.iterrows():
        split_map = {c: split_preserve(row[c]) for c in cols_present}
        pipe_map  = {c: cell_has_pipe(row[c]) for c in cols_present}
        max_len = max(len(v) for v in split_map.values())

        aligned = {}
        for c in cols_present:
            parts = split_map[c]
            has_pipe = pipe_map[c]
            pad_len = max_len - len(parts)

            if not has_pipe:
                # Replicate as-is
                base_val = parts[0] if len(parts) > 0 else ''
                aligned_list = [base_val] * max_len
            else:
                if c == STATUS_COL:
                    # STATUS: Right-align
                    aligned_list = [''] * pad_len + parts
                else:
                    # Others: Left-align then reverse
                    aligned_list = parts + [''] * pad_len
                    aligned_list = list(reversed(aligned_list))

            aligned[c] = aligned_list

        for i in range(max_len):
            aligned_rows.append({c: aligned[c][i] for c in cols_present})

    out = pd.DataFrame(aligned_rows)
    return out

# ---------------- Main script ----------------

def main():
    # Read all cells as text; keep_default_na=False preserves literal 'null' and blanks
    df = pd.read_excel(
        INPUT_FILE,
        sheet_name=SHEET,
        engine='openpyxl',
        dtype=str,
        keep_default_na=False
    )

    # Show available columns
    print(f"Loaded: {INPUT_FILE} (sheet index: {SHEET})")
    print("Available columns:")
    for c in df.columns:
        print(f"  - {c}")
    print("\nEnter the columns to group by (space-separated, no commas).")
    print('Example: Date statusCode\n')

    # Ask ONLY for the columns
    cols_input = input("Columns: ").strip()
    while not cols_input:
        print("Columns are required.")
        cols_input = input("Columns: ").strip()

    by_columns = parse_columns_input(cols_input)

    # Validate
    missing = [c for c in by_columns if c not in df.columns]
    if missing:
        raise SystemExit(f"Error: These columns are missing in the file: {missing}")

    status_included = STATUS_COL in by_columns

    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        if status_included:
            exploded = explode_with_opposite_pairing(df, by_columns)
            exploded['_class'] = exploded[STATUS_COL].apply(infer_status_class_digit_from_text)

            present_classes = exploded['_class'].dropna().unique().tolist()
            present_classes.sort(key=lambda x: (x == 'unknown', x))
            for class_label in present_classes:
                sub = exploded[exploded['_class'] == class_label].drop(columns=['_class'])
                counts_k = aggregate_counts(sub, by_cols=by_columns)
                counts_k = add_total_row(counts_k)  # <-- Add Total here
                sheet_name = f"counts_{class_label}"  # e.g., counts_4xx, counts_5xx, counts_unknown
                counts_k.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # Count exact raw strings without splitting
            req_df = df[by_columns].copy()
            counts_req = aggregate_counts(req_df, by_cols=by_columns)
            counts_req = add_total_row(counts_req)  # <-- Add Total here
            counts_req.to_excel(writer, sheet_name="req_col_count", index=False)

    print("\nDone.")
    print(f"Columns (fixed order): {' '.join(by_columns)}")
    print(f"Output file: {OUTPUT_FILE}")
    if status_included:
        print("Sheets: counts_{k}xx per present class (each sheet includes a 'Total' row).")
    else:
        print("Sheet: req_col_count (includes a 'Total' row)")

if __name__ == '__main__':
    main()
