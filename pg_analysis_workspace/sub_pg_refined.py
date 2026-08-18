
import pandas as pd
import re
from typing import List, Dict

INPUT_FILE = 'pg_refined.xlsx'
OUTPUT_FILE = 'sub_pg_refined.xlsx'

def normalize_group_key(col_name: str) -> str:
    """
    Normalize a column to its 'group key' by replacing numeric index segments with '#'.
      'errors.0.code' -> 'errors.#.code'
      'body.1.orderId' -> 'body.#.orderId'
      'arr.2' -> 'arr.#'
    """
    return re.sub(r'\.(\d+)(?=\.|$)', r'.#', col_name)

def parse_user_columns(user_input: str) -> List[str]:
    """
    Split user input by commas and/or whitespace, strip, and preserve order.
    """
    if not user_input:
        return []
    tokens = re.split(r'[\s,]+', user_input.strip())
    return [t for t in tokens if t]

def build_groups(selected_cols: List[str], df_cols: List[str]) -> Dict[str, List[str]]:
    """
    Build mapping: group_key -> list of columns (in the order provided by the user).
    Only keep columns that exist in the DataFrame.
    """
    existing_set = set(df_cols)
    groups: Dict[str, List[str]] = {}
    for c in selected_cols:
        if c not in existing_set:
            continue
        gk = normalize_group_key(c)
        groups.setdefault(gk, []).append(c)
    return groups

def build_final_columns(df_cols: List[str], groups: Dict[str, List[str]]) -> List[str]:
    """
    Construct final column order:
      - iterate original df_cols,
      - when hitting the first column of a group, insert the merged header,
      - skip the remaining group members,
      - keep other columns unchanged.
    Merged header uses spaces around the pipe: 'colA | colB | colC'.
    """
    cols_in_groups = set(c for cols in groups.values() for c in cols)
    col_to_gk = {}
    for gk, cols in groups.items():
        for c in cols:
            col_to_gk[c] = gk

    processed_groups = set()
    final_cols: List[str] = []

    for col in df_cols:
        if col not in cols_in_groups:
            final_cols.append(col)
            continue

        gk = col_to_gk.get(col)
        if gk is None:
            final_cols.append(col)
            continue

        if gk in processed_groups:
            continue  # already added merged header

        merged_header = ' | '.join(groups[gk])  # header with spaces around pipe
        final_cols.append(merged_header)
        processed_groups.add(gk)

    return final_cols

def merge_group_values(df: pd.DataFrame, cols: List[str]) -> pd.Series:
    """
    Row-wise merge of the given columns with rules:
      - Treat None/NaN as empty.
      - Ignore empty strings when joining.
      - If only one non-empty value: return that value (no separator).
      - If >= 2 non-empty values: join with ' | '.
    All values are already strings (we read everything as str).
    """
    parts = []
    for c in cols:
        if c in df.columns:
            s = df[c].astype(str)
        else:
            s = pd.Series([''] * len(df), index=df.index)
        # Normalize explicit 'nan' literals to empty (in case any slipped in)
        s = s.replace({'nan': ''})
        parts.append(s)

    if not parts:
        return pd.Series([''] * len(df), index=df.index)

    merged_values = []
    for i in range(len(df)):
        values = [series.iat[i] for series in parts]
        # Clean None-like
        values = [v if v is not None else '' for v in values]
        # Keep as-is; ignore empties when joining
        non_empty = [v for v in values if v != '']
        if len(non_empty) == 0:
            merged_values.append('')
        elif len(non_empty) == 1:
            merged_values.append(non_empty[0])
        else:
            merged_values.append(' | '.join(non_empty))

    return pd.Series(merged_values, index=df.index)

def main():
    # Read everything as TEXT to preserve exact cell content semantics
    # keep_default_na=False + na_filter=False -> prevents automatic NA/NaN conversion
    df = pd.read_excel(
        INPUT_FILE,
        engine='openpyxl',
        dtype=str,
        keep_default_na=False,
        na_filter=False
    )
    original_cols = list(df.columns)

    # Ask user which columns to club
    print("Enter the columns to club (space- or comma-separated), in the order they should be paired/joined.")
    print("Example:")
    print("errors.0.httpStatusCode errors.1.httpStatusCode errors.0.code errors.1.code "
          "errors.0.description errors.1.description errors.0.userMessage errors.1.userMessage "
          "errors.0.errorDetail errors.1.errorDetail errors.0.externalErrorCode errors.1.externalErrorCode\n")

    user_input = input("Columns to club: ").strip()
    selected_cols = parse_user_columns(user_input)

    # Warn about missing columns
    missing = [c for c in selected_cols if c not in original_cols]
    if missing:
        print("\nWARNING: These columns were not found and will be ignored:")
        for c in missing:
            print(f"  - {c}")

    # Build groups (existing columns only)
    groups = build_groups(selected_cols, original_cols)

    if not groups:
        print("\nNo valid columns selected for clubbing. Copying original file (as text).")
        # Convert all to string to ensure Excel doesn't reformat
        out_df = df.astype(str).replace({'nan': ''})
        # Write and force text format in Excel
        with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
            sheet_name = 'Sheet1'
            out_df.to_excel(writer, index=False, sheet_name=sheet_name)
            ws = writer.sheets[sheet_name]
            for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
                for cell in row:
                    cell.number_format = '@'  # force text
        print(f"Wrote: {OUTPUT_FILE}")
        return

    # Final column order based on original order with merged columns injected
    final_cols = build_final_columns(original_cols, groups)

    # Prepare output DataFrame
    out_df = pd.DataFrame(index=df.index)

    # Map merged header -> component columns list (headers use ' | ')
    merged_header_to_cols: Dict[str, List[str]] = {' | '.join(cols): cols for cols in groups.values()}

    for col in final_cols:
        if '|' in col and col in merged_header_to_cols:
            # Merged/group column
            component_cols = merged_header_to_cols[col]
            out_df[col] = merge_group_values(df, component_cols)
        else:
            # Keep column as-is (ensure string)
            if col in df.columns:
                out_df[col] = df[col].astype(str).replace({'nan': ''})
            else:
                out_df[col] = ''

    # Final pass: ensure every cell is a string (no NaN) so Excel won't reformat
    out_df = out_df.astype(str).replace({'nan': ''})

    # Write and force TEXT format for all cells
    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        sheet_name = 'Sheet1'
        out_df.to_excel(writer, index=False, sheet_name=sheet_name)
        ws = writer.sheets[sheet_name]
        # Apply text number format to headers + all data cells
        for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
            for cell in row:
                cell.number_format = '@'  # text

    print(f"\nWrote clubbed dataset to: {OUTPUT_FILE}")
    print(f"Rows: {len(out_df)}  Cols: {len(out_df.columns)}")
    print("All cells are written as TEXT to preserve exact values.")

if __name__ == "__main__":
    main()
