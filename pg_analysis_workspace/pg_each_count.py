#!/usr/bin/env python3
# -*- coding: utf-8 -*-

r"""
Generates ./pg_each_counts.xlsx from ./sub_pg_refined.xlsx

Key rules:
- Literal "null" in input stays "null" in output.
- Truly empty cells in input stay empty in output.
- No normalization or trimming of values (preserve text exactly).
- Output columns follow the input file's column order (among selected columns).
- 'required_columns' sheet: grouped counts (desc) + Total row; Count at the end.
- If selection includes a piped header containing 'httpStatusCode'
  (e.g., 'errors.0.httpStatusCode | errors.1.httpStatusCode'):
    * Creates class-based count sheets dynamically (e.g., '5xx_counts', '4xx_counts', '0xx_counts', '7xx_counts'):
        - If both sides fall into the same class (e.g., 500 | 500), keep piped row once in that class.
        - If sides differ (e.g., 500 | 400), create per-class rows using ONLY the matching side's values
          for all piped columns (left for 5xx, right for 4xx in this example).
        - '0xx_counts' includes whichever side(s) start with '0' (can be left and/or right).
- Any 'Count' column in input is ignored (we recompute).
- NEW: Rows where ALL selected key columns are empty are EXCLUDED from grouping (prevents blank groups).
"""

import sys
import re
import difflib
from typing import List, Tuple, Optional, Dict

import pandas as pd
import numpy as np
from collections import defaultdict

INPUT_FILE = "./sub_pg_refined.xlsx"
OUTPUT_FILE = "./pg_each_counts.xlsx"

# Toggle: whether to trim the left/right pieces around ' | ' when we *output* single-side values
# Rule says "no trimming", so this remains False by default.
TRIM_PIPED_SIDES_FOR_OUTPUT = False


# -------------------- Input handling (TEXT ONLY, preserve 'null' and empties) --------------------
def load_input_as_text(path: str) -> pd.DataFrame:
    """
    Read worksheet as strings and DO NOT treat 'null' (or similar) as NA.
    - keep_default_na=False: do not convert 'null'/'NA'/'NaN' to NaN
    - na_filter=False: skip NA detection entirely
    - dtype=str: keep everything as text
    Result: literal 'null' stays 'null'; true blanks read as empty string "".
    """
    df = pd.read_excel(
        path,
        engine="openpyxl",
        dtype=str,
        keep_default_na=False,
        na_filter=False,
    )
    if "Count" in df.columns:
        df = df.drop(columns=["Count"])
    # Clean column headers only; DO NOT touch cell values
    df.columns = [str(c).strip() for c in df.columns]
    # Safety: ensure any residual NaNs are empty strings
    df = df.where(df.notna(), "")
    return df


# -------------------- Input parsing --------------------
def parse_user_columns(raw: str) -> List[str]:
    r"""
    Accept:
      - Comma-separated columns, OR
      - Columns separated by ANY whitespace, but DO NOT split spaces around ' | ' in piped headers.
        Regex for whitespace split (not adjacent to a pipe): (?<!\|)\s+(?!\|)
    """
    raw = raw.strip()
    if "," in raw:
        parts = [p.strip() for p in raw.split(",")]
    else:
        parts = [p.strip() for p in re.split(r'(?<!\|)\s+(?!\|)', raw) if p.strip()]
    return parts


def prompt_user_for_columns(df_columns: List[str]) -> List[str]:
    print("\nAvailable columns in ./sub_pg_refined.xlsx:\n")
    for c in df_columns:
        print(f" - {c}")
    print("\nGuidelines:")
    print(" - Enter columns either comma-separated OR separated by spaces/tabs (order preserved).")
    print(" - Example: Date, Message, httpStatusCode, body")
    print(" - 'Date' is optional. Do NOT include 'Count' (it will be calculated).")
    print(" - For 0xx/4xx/5xx sheets, include a piped httpStatusCode column, e.g.:")
    print("     errors.0.httpStatusCode | errors.1.httpStatusCode")

    cols_raw = input("\nEnter your columns: ")
    chosen = parse_user_columns(cols_raw)

    print("\nYou entered:")
    for i, c in enumerate(chosen, 1):
        print(f"{i:>2}. {c}")

    if not chosen:
        print("\nERROR: You must select at least one column to group by.")
        sys.exit(1)

    # Validate names against df columns
    missing = [c for c in chosen if c not in df_columns]
    if missing:
        print("\nERROR: The following columns are not present in the file:")
        for m in missing:
            suggestion = difflib.get_close_matches(m, df_columns, n=1, cutoff=0.6)
            if suggestion:
                print(f"  - {m} (did you mean: {suggestion[0]!r} ?)")
            else:
                print(f"  - {m}")
        sys.exit(1)

    # Reorder to match the input file’s column order
    chosen_set = set(chosen)
    selected_cols_in_file_order = [c for c in df_columns if c in chosen_set]

    print("\nApplied column order (following input file):")
    for i, c in enumerate(selected_cols_in_file_order, 1):
        print(f"{i:>2}. {c}")

    return selected_cols_in_file_order


# -------------------- Helpers for blank checks and pipes --------------------
def is_all_selected_empty(row: pd.Series, selected_cols: List[str]) -> bool:
    """
    A row is considered empty if ALL selected key columns are empty.
    For piped values like ' | ' (or with spaces), treat that as empty too.
    """
    for col in selected_cols:
        v = row.get(col, "")
        if v is None:
            v = ""
        v = str(v)
        if "|" in v:
            # remove pipes and surrounding spaces to test emptiness
            if v.replace("|", "").strip() != "":
                return False
        else:
            # Preserve original behavior (no trimming of whitespace)
            if v != "":
                return False
    return True


def split_piped_value(cell: str) -> Tuple[str, Optional[str]]:
    """
    Split a piped cell 'left | right' into (left, right).
    Preserves exact substrings (including spaces) for output fidelity.
    If not piped, returns (cell, None).
    """
    if cell is None:
        return "", None
    s = str(cell)
    if "|" not in s:
        return s, None
    # split on first pipe
    parts = s.split("|", 1)
    left = parts[0]
    right = parts[1]
    # Keep exact substrings; DO NOT strip for output.
    return left, right


def classify_code(code_text: str) -> Optional[str]:
    """
    Return '<digit>xx' for first digit 0..9, or None otherwise.
    Trims only for classification (NOT for output).
    Examples: '500' -> '5xx', '07' -> '0xx', '700' -> '7xx'
    """
    if code_text is None:
        return None
    t = str(code_text).strip()
    if t == "":
        return None
    first = t[0]
    if first.isdigit():
        return f"{first}xx"
    return None


def get_side_value(cell: str, side: str) -> str:
    """
    For a piped value 'L | R', return exact left or right substring.
    If not piped, returns the cell as-is (right side falls back to left if right is absent).
    If TRIM_PIPED_SIDES_FOR_OUTPUT is True, will trim the chosen side.
    """
    left, right = split_piped_value(cell)
    val = left if side == "left" else (right if right is not None else left)
    if TRIM_PIPED_SIDES_FOR_OUTPUT and isinstance(val, str):
        return val.strip()
    return val


# -------------------- Grouping & Sheet builders --------------------
def group_counts(df: pd.DataFrame, selected_cols: List[str]) -> pd.DataFrame:
    """
    Group by selected columns (exact text), compute Count, sort desc.
    Excludes rows where ALL selected columns are empty.
    Places 'Count' as the last column and adds a 'Total' row.
    """
    # Exclude all-empty rows
    mask_keep = ~df[selected_cols].apply(lambda r: is_all_selected_empty(r, selected_cols), axis=1)
    working = df.loc[mask_keep, selected_cols].copy()

    # Group
    grouped = (
        working.groupby(selected_cols, dropna=False)
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=False)
    )

    # Total row
    total = grouped["Count"].sum()
    total_row = {col: "" for col in selected_cols}
    total_row[selected_cols[0]] = "Total"
    total_row["Count"] = total
    grouped = pd.concat([grouped, pd.DataFrame([total_row])], ignore_index=True)

    # Ensure Count at the end
    cols = [c for c in grouped.columns if c != "Count"] + ["Count"]
    grouped = grouped[cols]
    return grouped


def build_class_sheets(
    df: pd.DataFrame,
    selected_cols: List[str],
    piped_status_col: str,
) -> Dict[str, pd.DataFrame]:
    """
    Build dynamic <class>_counts sheets (e.g., 0xx, 4xx, 5xx, 7xx...) from df based on a piped httpStatusCode column.
    Dynamic behavior:
      - If both sides classify to the same class (non-None), keep the original piped row ONCE in that class.
      - Else, emit per-side row into the corresponding class using that side's values for *all piped columns*.
      - Non-piped columns are preserved as-is.
    Only non-empty class sheets are returned.
    """
    class_rows = defaultdict(list)  # key: '5xx', '7xx', etc. value: list of row dicts

    for _, row in df.iterrows():
        raw_status = row.get(piped_status_col, "")
        left_s, right_s = split_piped_value(raw_status)
        left_cls = classify_code(left_s)
        right_cls = classify_code(right_s if right_s is not None else "")

        # Both sides same valid class? Keep the row as-is once in that class
        if left_cls is not None and left_cls == right_cls:
            class_rows[left_cls].append({c: row[c] for c in selected_cols})
            continue

        # Otherwise, create side-specific rows for whichever sides classify
        for side, side_cls in (("left", left_cls), ("right", right_cls)):
            if side_cls is None:
                continue

            new_row = {}
            for col in selected_cols:
                cell = row.get(col, "")
                if "|" in col:
                    # Header is piped: take side value from the *cell* content
                    new_row[col] = get_side_value(cell, side)
                else:
                    # Non-piped header: copy as-is
                    new_row[col] = cell
            class_rows[side_cls].append(new_row)

    # Convert to DataFrames and group/count; only include non-empty classes
    result: Dict[str, pd.DataFrame] = {}
    for cls, rows in class_rows.items():
        if not rows:
            continue  # skip empty classes—no placeholder sheets
        tmp_df = pd.DataFrame(rows, columns=selected_cols)
        grouped_df = group_counts(tmp_df, selected_cols)
        result[f"{cls}_counts"] = grouped_df

    return result


# -------------------- Main --------------------
def main():
    print(f"Reading: {INPUT_FILE}")
    df = load_input_as_text(INPUT_FILE)

    selected_cols = prompt_user_for_columns(df.columns.tolist())

    # Base: required_columns sheet (group by selected columns)
    required_sheet = group_counts(df, selected_cols)

    # Check if we have a piped httpStatusCode column among selections
    piped_status_cols = [c for c in selected_cols if ("httpStatusCode" in c and "|" in c)]
    has_class_sheets = len(piped_status_cols) > 0

    # Prepare writer & save sheets
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        required_sheet.to_excel(writer, index=False, sheet_name="required_columns")

        if has_class_sheets:
            # Use the first piped httpStatusCode column encountered
            piped_status_col = piped_status_cols[0]
            class_sheets = build_class_sheets(df[selected_cols].copy(), selected_cols, piped_status_col)
            # Write only non-empty class sheets (dynamic)
            for sheet_name, sdf in class_sheets.items():
                sdf.to_excel(writer, index=False, sheet_name=sheet_name)

    print(f"Done. Wrote: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()


# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# r"""
# Generates ./pg_each_counts.xlsx from ./sub_pg_refined.xlsx

# Key rules:
# - Literal "null" in input stays "null" in output.
# - Truly empty cells in input stay empty in output.
# - No normalization or trimming of values (preserve text exactly).
# - Output columns follow the input file's column order (among selected columns).
# - 'required_columns' sheet: grouped counts (desc) + Total row; Count at the end.
# - If selection includes a piped header containing 'httpStatusCode'
#   (e.g., 'errors.0.httpStatusCode | errors.1.httpStatusCode'):
#     * Creates class-based count sheets dynamically (e.g., '5xx_counts', '4xx_counts', '0xx_counts', '7xx_counts'):
#         - If both sides fall into the same class (e.g., 500 | 500), keep piped row once in that class.
#         - If sides differ (e.g., 500 | 400), create per-class rows using ONLY the matching side's values
#           for all piped columns (left for 5xx, right for 4xx in this example).
#         - Any class is supported as long as the first digit is 0..9.
# - Any 'Count' column in input is ignored (we recompute).
# - NEW: Rows where ALL selected key columns are empty are EXCLUDED from grouping (prevents blank groups).
# """

# import sys
# import re
# import difflib
# from typing import List, Tuple, Optional, Dict

# import pandas as pd
# import numpy as np
# from collections import defaultdict

# INPUT_FILE = "./sub_pg_refined.xlsx"
# OUTPUT_FILE = "./pg_each_counts.xlsx"

# # Toggle: whether to trim the left/right pieces around ' | ' when we *output* single-side values
# # Rule says "no trimming", so this remains False by default.
# TRIM_PIPED_SIDES_FOR_OUTPUT = False


# # -------------------- Input handling (TEXT ONLY, preserve 'null' and empties) --------------------
# def load_input_as_text(path: str) -> pd.DataFrame:
#     """
#     Read worksheet as strings and DO NOT treat 'null' (or similar) as NA.
#     - keep_default_na=False: do not convert 'null'/'NA'/'NaN' to NaN
#     - na_filter=False: skip NA detection entirely
#     - dtype=str: keep everything as text
#     Result: literal 'null' stays 'null'; true blanks read as empty string "".
#     """
#     df = pd.read_excel(
#         path,
#         engine="openpyxl",
#         dtype=str,
#         keep_default_na=False,
#         na_filter=False,
#     )
#     if "Count" in df.columns:
#         df = df.drop(columns=["Count"])
#     # Clean column headers only; DO NOT touch cell values
#     df.columns = [str(c).strip() for c in df.columns]
#     # Safety: ensure any residual NaNs are empty strings
#     df = df.where(df.notna(), "")
#     return df


# # -------------------- Input parsing --------------------
# def parse_user_columns(raw: str) -> List[str]:
#     r"""
#     Accept:
#       - Comma-separated columns, OR
#       - Columns separated by ANY whitespace, but DO NOT split spaces around ' | ' in piped headers.
#         Regex for whitespace split (not adjacent to a pipe): (?<!\|)\s+(?!\|)
#     """
#     raw = raw.strip()
#     if "," in raw:
#         parts = [p.strip() for p in raw.split(",")]
#     else:
#         parts = [p.strip() for p in re.split(r'(?<!\|)\s+(?!\|)', raw) if p.strip()]
#     return parts


# def prompt_user_for_columns(df_columns: List[str]) -> List[str]:
#     print("\nAvailable columns in ./sub_pg_refined.xlsx:\n")
#     for c in df_columns:
#         print(f" - {c}")
#     print("\nGuidelines:")
#     print(" - Enter columns either comma-separated OR separated by spaces/tabs (order preserved).")
#     print(" - Example: Date, Message, httpStatusCode, body")
#     print(" - 'Date' is optional. Do NOT include 'Count' (it will be calculated).")
#     print(" - For 0xx/4xx/5xx sheets, include a piped httpStatusCode column, e.g.:")
#     print("     errors.0.httpStatusCode | errors.1.httpStatusCode")

#     cols_raw = input("\nEnter your columns: ")
#     chosen = parse_user_columns(cols_raw)

#     print("\nYou entered:")
#     for i, c in enumerate(chosen, 1):
#         print(f"{i:>2}. {c}")

#     if not chosen:
#         print("\nERROR: You must select at least one column to group by.")
#         sys.exit(1)

#     # Validate names against df columns
#     missing = [c for c in chosen if c not in df_columns]
#     if missing:
#         print("\nERROR: The following columns are not present in the file:")
#         for m in missing:
#             suggestion = difflib.get_close_matches(m, df_columns, n=1, cutoff=0.6)
#             if suggestion:
#                 print(f"  - {m} (did you mean: {suggestion[0]!r} ?)")
#             else:
#                 print(f"  - {m}")
#         sys.exit(1)

#     # Reorder to match the input file’s column order
#     chosen_set = set(chosen)
#     selected_cols_in_file_order = [c for c in df_columns if c in chosen_set]

#     print("\nApplied column order (following input file):")
#     for i, c in enumerate(selected_cols_in_file_order, 1):
#         print(f"{i:>2}. {c}")

#     return selected_cols_in_file_order


# # -------------------- Helpers for blank checks and pipes --------------------
# def is_all_selected_empty(row: pd.Series, selected_cols: List[str]) -> bool:
#     """
#     A row is considered empty if ALL selected key columns are empty.
#     For piped values like ' | ' (or with spaces), treat that as empty too.
#     """
#     for col in selected_cols:
#         v = row.get(col, "")
#         if v is None:
#             v = ""
#         v = str(v)
#         if "|" in v:
#             # remove pipes and surrounding spaces to test emptiness
#             if v.replace("|", "").strip() != "":
#                 return False
#         else:
#             # NOTE: preserving your original behavior (no trimming).
#             # If you want whitespace-only to count as empty, change to: if v.strip() != "": return False
#             if v != "":
#                 return False
#     return True


# def split_piped_value(cell: str) -> Tuple[str, Optional[str]]:
#     """
#     Split a piped cell 'left | right' into (left, right).
#     Preserves exact substrings (including spaces) for output fidelity.
#     If not piped, returns (cell, None).
#     """
#     if cell is None:
#         return "", None
#     s = str(cell)
#     if "|" not in s:
#         return s, None
#     # split on first pipe
#     parts = s.split("|", 1)
#     left = parts[0]
#     right = parts[1]
#     # Keep exact substrings; DO NOT strip for output.
#     return left, right


# def classify_code(code_text: str) -> Optional[str]:
#     """
#     Return '<digit>xx' for first digit 0..9, or None otherwise.
#     Trims only for classification (NOT for output).
#     Examples: '500' -> '5xx', '07' -> '0xx', '700' -> '7xx'
#     """
#     if code_text is None:
#         return None
#     t = str(code_text).strip()
#     if t == "":
#         return None
#     first = t[0]
#     if first.isdigit():
#         return f"{first}xx"
#     return None


# def get_side_value(cell: str, side: str) -> str:
#     """
#     For a piped value 'L | R', return exact left or right substring.
#     If not piped, returns the cell as-is (right side falls back to left if right is absent).
#     If TRIM_PIPED_SIDES_FOR_OUTPUT is True, will trim the chosen side.
#     """
#     left, right = split_piped_value(cell)
#     val = left if side == "left" else (right if right is not None else left)
#     if TRIM_PIPED_SIDES_FOR_OUTPUT and isinstance(val, str):
#         return val.strip()
#     return val


# # -------------------- Grouping & Sheet builders --------------------
# def group_counts(df: pd.DataFrame, selected_cols: List[str]) -> pd.DataFrame:
#     """
#     Group by selected columns (exact text), compute Count, sort desc.
#     Excludes rows where ALL selected columns are empty.
#     Places 'Count' as the last column and adds a 'Total' row.
#     """
#     # Exclude all-empty rows
#     mask_keep = ~df[selected_cols].apply(lambda r: is_all_selected_empty(r, selected_cols), axis=1)
#     working = df.loc[mask_keep, selected_cols].copy()

#     # Group
#     grouped = (
#         working.groupby(selected_cols, dropna=False)
#         .size()
#         .reset_index(name="Count")
#         .sort_values("Count", ascending=False)
#     )

#     # Total row
#     total = grouped["Count"].sum()
#     total_row = {col: "" for col in selected_cols}
#     total_row[selected_cols[0]] = "Total"
#     total_row["Count"] = total
#     grouped = pd.concat([grouped, pd.DataFrame([total_row])], ignore_index=True)

#     # Ensure Count at the end
#     cols = [c for c in grouped.columns if c != "Count"] + ["Count"]
#     grouped = grouped[cols]
#     return grouped


# def build_class_sheets(
#     df: pd.DataFrame,
#     selected_cols: List[str],
#     piped_status_col: str,
# ) -> Dict[str, pd.DataFrame]:
#     """
#     Build dynamic <class>_counts sheets (e.g., 0xx, 4xx, 5xx, 7xx...) from df based on a piped httpStatusCode column.
#     Dynamic behavior:
#       - If both sides classify to the same class (non-None), keep the original piped row ONCE in that class.
#       - Else, emit per-side row into the corresponding class using that side's values for *all piped columns*.
#       - Non-piped columns are preserved as-is.
#     Only non-empty class sheets are returned.
#     """
#     # NOTE: piped_cols header-list computed earlier was unused—keeping minimal change while fixing dynamic behavior.
#     class_rows = defaultdict(list)  # key: '5xx', '7xx', etc. value: list of row dicts

#     for _, row in df.iterrows():
#         raw_status = row.get(piped_status_col, "")
#         left_s, right_s = split_piped_value(raw_status)
#         left_cls = classify_code(left_s)
#         right_cls = classify_code(right_s if right_s is not None else "")

#         # Both sides same valid class? Keep the row as-is once in that class
#         if left_cls is not None and left_cls == right_cls:
#             class_rows[left_cls].append({c: row[c] for c in selected_cols})
#             continue

#         # Otherwise, create side-specific rows for whichever sides classify
#         for side, side_cls in (("left", left_cls), ("right", right_cls)):
#             if side_cls is None:
#                 continue
#             new_row = {}
#             for col in selected_cols:
#                 cell = row.get(col, "")
#                 if "|" in col:
#                     # Header is piped: take side value from the *cell* content
#                     new_row[col] = get_side_value(cell, side)
#                 else:
#                     # Non-piped header: copy as-is
#                     new_row[col] = cell
#             class_rows[side_cls].append(new_row)

#     # Convert to DataFrames and group/count; only include non-empty classes
#     result: Dict[str, pd.DataFrame] = {}
#     for cls, rows in class_rows.items():
#         if not rows:
#             continue  # skip empty classes—no static/placeholder sheets
#         tmp_df = pd.DataFrame(rows, columns=selected_cols)
#         grouped_df = group_counts(tmp_df, selected_cols)
#         result[f"{cls}_counts"] = grouped_df

#     return result


# # -------------------- Main --------------------
# def main():
#     print(f"Reading: {INPUT_FILE}")
#     df = load_input_as_text(INPUT_FILE)

#     selected_cols = prompt_user_for_columns(df.columns.tolist())

#     # Base: required_columns sheet (group by selected columns)
#     required_sheet = group_counts(df, selected_cols)

#     # Check if we have a piped httpStatusCode column among selections
#     piped_status_cols = [c for c in selected_cols if ("httpStatusCode" in c and "|" in c)]
#     has_class_sheets = len(piped_status_cols) > 0

#     # Prepare writer & save sheets
#     with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
#         required_sheet.to_excel(writer, index=False, sheet_name="required_columns")

#         if has_class_sheets:
#             # Use the first piped httpStatusCode column encountered
#             piped_status_col = piped_status_cols[0]
#             class_sheets = build_class_sheets(df[selected_cols].copy(), selected_cols, piped_status_col)
#             # Write only non-empty class sheets (dynamic)
#             for sheet_name, sdf in class_sheets.items():
#                 sdf.to_excel(writer, index=False, sheet_name=sheet_name)

#     print(f"Done. Wrote: {OUTPUT_FILE}")


# if __name__ == "__main__":
#     main()



# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# r"""
# Generates ./pg_each_counts.xlsx from ./sub_pg_refined.xlsx

# Key rules:
# - Literal "null" in input stays "null" in output.
# - Truly empty cells in input stay empty in output.
# - No normalization or trimming of values (preserve text exactly).
# - Output columns follow the input file's column order (among selected columns).
# - 'required_columns' sheet: grouped counts (desc) + Total row; Count at the end.
# - If selection includes a piped header containing 'httpStatusCode'
#   (e.g., 'errors.0.httpStatusCode | errors.1.httpStatusCode'):
#     * Creates '5xx_counts', '4xx_counts', '0xx_counts' dynamically:
#         - If both sides fall into the same class (e.g., 500 | 500), keep piped row once in that class.
#         - If sides differ (e.g., 500 | 400), create per-class rows using ONLY the matching side's values
#           for all piped columns (left for 5xx, right for 4xx in this example).
#         - '0xx_counts' includes whichever side(s) start with '0' (can be left and/or right).
# - Any 'Count' column in input is ignored (we recompute).
# - NEW: Rows where ALL selected key columns are empty are EXCLUDED from grouping (prevents blank groups).
# """

# import sys
# import re
# import difflib
# from typing import List, Tuple, Optional, Dict

# import pandas as pd
# import numpy as np

# INPUT_FILE = "./sub_pg_refined.xlsx"
# OUTPUT_FILE = "./pg_each_counts.xlsx"

# # Toggle: whether to trim the left/right pieces around ' | ' when we *output* single-side values
# # Rule says "no trimming", so this remains False by default.
# TRIM_PIPED_SIDES_FOR_OUTPUT = False


# # -------------------- Input handling (TEXT ONLY, preserve 'null' and empties) --------------------
# def load_input_as_text(path: str) -> pd.DataFrame:
#     """
#     Read worksheet as strings and DO NOT treat 'null' (or similar) as NA.
#     - keep_default_na=False: do not convert 'null'/'NA'/'NaN' to NaN
#     - na_filter=False: skip NA detection entirely
#     - dtype=str: keep everything as text
#     Result: literal 'null' stays 'null'; true blanks read as empty string "".
#     """
#     df = pd.read_excel(
#         path,
#         engine="openpyxl",
#         dtype=str,
#         keep_default_na=False,
#         na_filter=False,
#     )
#     if "Count" in df.columns:
#         df = df.drop(columns=["Count"])
#     # Clean column headers only; DO NOT touch cell values
#     df.columns = [str(c).strip() for c in df.columns]
#     # Safety: ensure any residual NaNs are empty strings
#     df = df.where(df.notna(), "")
#     return df


# # -------------------- Input parsing --------------------
# def parse_user_columns(raw: str) -> List[str]:
#     r"""
#     Accept:
#       - Comma-separated columns, OR
#       - Columns separated by ANY whitespace, but DO NOT split spaces around ' | ' in piped headers.
#         Regex for whitespace split (not adjacent to a pipe): (?<!\|)\s+(?!\|)
#     """
#     raw = raw.strip()
#     if "," in raw:
#         parts = [p.strip() for p in raw.split(",")]
#     else:
#         parts = [p.strip() for p in re.split(r'(?<!\|)\s+(?!\|)', raw) if p.strip()]
#     return parts


# def prompt_user_for_columns(df_columns: List[str]) -> List[str]:
#     print("\nAvailable columns in ./sub_pg_refined.xlsx:\n")
#     for c in df_columns:
#         print(f" - {c}")
#     print("\nGuidelines:")
#     print(" - Enter columns either comma-separated OR separated by spaces/tabs (order preserved).")
#     print(" - Example: Date, Message, httpStatusCode, body")
#     print(" - 'Date' is optional. Do NOT include 'Count' (it will be calculated).")
#     print(" - For 0xx/4xx/5xx sheets, include a piped httpStatusCode column, e.g.:")
#     print("     errors.0.httpStatusCode | errors.1.httpStatusCode")

#     cols_raw = input("\nEnter your columns: ")
#     chosen = parse_user_columns(cols_raw)

#     print("\nYou entered:")
#     for i, c in enumerate(chosen, 1):
#         print(f"{i:>2}. {c}")

#     if not chosen:
#         print("\nERROR: You must select at least one column to group by.")
#         sys.exit(1)

#     # Validate names against df columns
#     missing = [c for c in chosen if c not in df_columns]
#     if missing:
#         print("\nERROR: The following columns are not present in the file:")
#         for m in missing:
#             suggestion = difflib.get_close_matches(m, df_columns, n=1, cutoff=0.6)
#             if suggestion:
#                 print(f"  - {m} (did you mean: {suggestion[0]!r} ?)")
#             else:
#                 print(f"  - {m}")
#         sys.exit(1)

#     # Reorder to match the input file’s column order
#     chosen_set = set(chosen)
#     selected_cols_in_file_order = [c for c in df_columns if c in chosen_set]

#     print("\nApplied column order (following input file):")
#     for i, c in enumerate(selected_cols_in_file_order, 1):
#         print(f"{i:>2}. {c}")

#     return selected_cols_in_file_order


# # -------------------- Helpers for blank checks and pipes --------------------
# def is_all_selected_empty(row: pd.Series, selected_cols: List[str]) -> bool:
#     """
#     A row is considered empty if ALL selected key columns are empty.
#     For piped values like ' | ' (or with spaces), treat that as empty too.
#     """
#     for col in selected_cols:
#         v = row.get(col, "")
#         if v is None:
#             v = ""
#         v = str(v)
#         if "|" in v:
#             # remove pipes and surrounding spaces to test emptiness
#             if v.replace("|", "").strip() != "":
#                 return False
#         else:
#             if v != "":
#                 return False
#     return True


# def split_piped_value(cell: str) -> Tuple[str, Optional[str]]:
#     """
#     Split a piped cell 'left | right' into (left, right).
#     Preserves exact substrings (including spaces) for output fidelity.
#     If not piped, returns (cell, None).
#     """
#     if cell is None:
#         return "", None
#     s = str(cell)
#     if "|" not in s:
#         return s, None
#     # split on first pipe
#     parts = s.split("|", 1)
#     left = parts[0]
#     right = parts[1]
#     # Keep exact substrings; DO NOT strip for output.
#     return left, right


# def classify_code(code_text: str) -> Optional[str]:
#     """
#     Return '5xx', '4xx', '0xx', or None based on the first digit of the code.
#     Trims only for classification (NOT for output).
#     """
#     if code_text is None:
#         return None
#     t = str(code_text).strip()
#     if t == "":
#         return None
#     first = t[0]
#     if first == "5":
#         return "5xx"
#     if first == "4":
#         return "4xx"
#     if first == "0":
#         return "0xx"
#     return None


# def get_side_value(cell: str, side: str) -> str:
#     """
#     For a piped value 'L | R', return exact left or right substring.
#     If not piped, returns the cell as-is.
#     If TRIM_PIPED_SIDES_FOR_OUTPUT is True, will trim the chosen side.
#     """
#     left, right = split_piped_value(cell)
#     val = left if side == "left" else (right if right is not None else left)
#     if TRIM_PIPED_SIDES_FOR_OUTPUT and isinstance(val, str):
#         return val.strip()
#     return val


# # -------------------- Grouping & Sheet builders --------------------
# def group_counts(df: pd.DataFrame, selected_cols: List[str]) -> pd.DataFrame:
#     """
#     Group by selected columns (exact text), compute Count, sort desc.
#     Excludes rows where ALL selected columns are empty.
#     Places 'Count' as the last column and adds a 'Total' row.
#     """
#     # Exclude all-empty rows
#     mask_keep = ~df[selected_cols].apply(lambda r: is_all_selected_empty(r, selected_cols), axis=1)
#     working = df.loc[mask_keep, selected_cols].copy()

#     # Group
#     grouped = (
#         working.groupby(selected_cols, dropna=False)
#         .size()
#         .reset_index(name="Count")
#         .sort_values("Count", ascending=False)
#     )

#     # Total row
#     total = grouped["Count"].sum()
#     total_row = {col: "" for col in selected_cols}
#     total_row[selected_cols[0]] = "Total"
#     total_row["Count"] = total
#     grouped = pd.concat([grouped, pd.DataFrame([total_row])], ignore_index=True)

#     # Ensure Count at the end
#     cols = [c for c in grouped.columns if c != "Count"] + ["Count"]
#     grouped = grouped[cols]
#     return grouped


# def build_class_sheets(
#     df: pd.DataFrame,
#     selected_cols: List[str],
#     piped_status_col: str,
# ) -> Dict[str, pd.DataFrame]:
#     """
#     Build 5xx_counts, 4xx_counts, 0xx_counts from df based on a piped httpStatusCode column.
#     Dynamic behavior:
#       - If both sides classify to the same class (non-None), keep the original piped row ONCE in that class.
#       - Else, emit per-side row into the corresponding class using that side's values for *all piped columns*.
#       - Non-piped columns are preserved as-is.
#     """
#     piped_cols = [c for c in selected_cols if "|" in c]
#     class_rows = {"5xx": [], "4xx": [], "0xx": []}

#     for _, row in df.iterrows():
#         raw_status = row.get(piped_status_col, "")
#         left_s, right_s = split_piped_value(raw_status)
#         left_cls = classify_code(left_s)
#         right_cls = classify_code(right_s if right_s is not None else "")

#         # Both sides same valid class? Keep the row as-is once in that class
#         if left_cls is not None and left_cls == right_cls:
#             class_rows[left_cls].append({c: row[c] for c in selected_cols})
#             continue

#         # Otherwise, create side-specific rows for whichever sides classify
#         for side, side_cls in (("left", left_cls), ("right", right_cls)):
#             if side_cls not in ("5xx", "4xx", "0xx"):
#                 continue

#             new_row = {}
#             for col in selected_cols:
#                 cell = row.get(col, "")
#                 if "|" in col:
#                     # Header is piped: take side value from the *cell* content
#                     new_row[col] = get_side_value(cell, side)
#                 else:
#                     # Non-piped header: copy as-is
#                     new_row[col] = cell
#             class_rows[side_cls].append(new_row)

#     # Convert to DataFrames and group/count
#     result = {}
#     for key, rows in class_rows.items():
#         if not rows:
#             # empty placeholder with the same columns + Count (to keep sheet present)
#             result[key] = pd.DataFrame(columns=selected_cols + ["Count"])
#             continue
#         tmp_df = pd.DataFrame(rows, columns=selected_cols)
#         result[key] = group_counts(tmp_df, selected_cols)

#     return {
#         "5xx_counts": result["5xx"],
#         "4xx_counts": result["4xx"],
#         "0xx_counts": result["0xx"],
#     }


# # -------------------- Main --------------------
# def main():
#     print(f"Reading: {INPUT_FILE}")
#     df = load_input_as_text(INPUT_FILE)

#     selected_cols = prompt_user_for_columns(df.columns.tolist())

#     # Base: required_columns sheet (group by selected columns)
#     required_sheet = group_counts(df, selected_cols)

#     # Check if we have a piped httpStatusCode column among selections
#     piped_status_cols = [c for c in selected_cols if ("httpStatusCode" in c and "|" in c)]
#     has_class_sheets = len(piped_status_cols) > 0

#     # Prepare writer & save sheets
#     with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
#         required_sheet.to_excel(writer, index=False, sheet_name="required_columns")

#         if has_class_sheets:
#             # Use the first piped httpStatusCode column encountered
#             piped_status_col = piped_status_cols[0]
#             class_sheets = build_class_sheets(df[selected_cols].copy(), selected_cols, piped_status_col)
#             for sheet_name, sdf in class_sheets.items():
#                 sdf.to_excel(writer, index=False, sheet_name=sheet_name)

#     print(f"Done. Wrote: {OUTPUT_FILE}")


# if __name__ == "__main__":
#     main()










# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# r"""
# Generates ./pg_each_counts.xlsx from ./sub_pg_refined.xlsx

# Key rules:
# - Literal "null" in input stays "null" in output.
# - Truly empty cells in input stay empty in output.
# - No normalization or trimming of values (preserve text exactly).
# - Output columns follow the input file's column order (among selected columns).
# - 'required_columns' sheet: grouped counts (desc) + Total row; Count at the end.
# - If selection includes a piped header containing 'httpStatusCode'
#   (e.g., 'errors.0.httpStatusCode | errors.1.httpStatusCode'):
#     * Creates '5xx_counts' (left/errors.0.*),
#              '4xx_counts' (right/errors.1.*),
#              '0xx_counts' (whichever side starts with '0'; can include both sides).
# - Any 'Count' column in input is ignored (we recompute).
# - NEW: Rows where ALL selected key columns are empty are EXCLUDED from grouping (prevents blank groups boosting Count).
# """

# import sys
# import re
# import difflib
# from typing import List, Tuple

# import pandas as pd
# import numpy as np

# INPUT_FILE = "./sub_pg_refined.xlsx"
# OUTPUT_FILE = "./pg_each_counts.xlsx"

# # -------------------- Input handling (TEXT ONLY, preserve 'null' and empties) --------------------
# def load_input_as_text(path: str) -> pd.DataFrame:
#     """
#     Read worksheet as strings and DO NOT treat 'null' (or similar) as NA.
#     - keep_default_na=False: do not convert 'null'/'NA'/'NaN' to NaN
#     - na_filter=False: skip NA detection entirely
#     - dtype=str: keep everything as text
#     Result: literal 'null' stays 'null'; true blanks read as empty string "".
#     """
#     df = pd.read_excel(
#         path,
#         engine="openpyxl",
#         dtype=str,
#         keep_default_na=False,
#         na_filter=False,
#     )
#     if "Count" in df.columns:
#         df = df.drop(columns=["Count"])
#     # Clean column headers only; DO NOT touch cell values
#     df.columns = [str(c).strip() for c in df.columns]
#     # Safety: ensure any residual NaNs are empty strings
#     df = df.where(df.notna(), "")
#     return df

# # -------------------- Input parsing --------------------
# def parse_user_columns(raw: str) -> List[str]:
#     r"""
#     Accept:
#       - Comma-separated columns, OR
#       - Columns separated by ANY whitespace, but DO NOT split spaces around ' | ' in piped headers.
#         Regex for whitespace split (not adjacent to a pipe): (?<!\|)\s+(?!\|)
#     """
#     raw = raw.strip()
#     if "," in raw:
#         parts = [p.strip() for p in raw.split(",")]
#     else:
#         parts = [p.strip() for p in re.split(r'(?<!\|)\s+(?!\|)', raw) if p.strip()]
#     return parts

# def prompt_user_for_columns(df_columns: List[str]) -> List[str]:
#     print("\nAvailable columns in ./sub_pg_refined.xlsx:\n")
#     for c in df_columns:
#         print(f" - {c}")
#     print("\nGuidelines:")
#     print(" - Enter columns either comma-separated OR separated by spaces/tabs (order preserved).")
#     print(" - Example: Date, Message, httpStatusCode, body")
#     print(" - 'Date' is optional. Do NOT include 'Count' (it will be calculated).")
#     print(" - For 0xx/4xx/5xx sheets, include a piped httpStatusCode column, e.g.:")
#     print("     errors.0.httpStatusCode | errors.1.httpStatusCode")

#     cols_raw = input("\nEnter your columns: ")
#     chosen = parse_user_columns(cols_raw)

#     print("\nYou entered:")
#     for i, c in enumerate(chosen, 1):
#         print(f"{i:>2}. {c}")

#     if not chosen:
#         print("\nERROR: You must select at least one column to group by.")
#         sys.exit(1)

#     # Validate names against df columns
#     missing = [c for c in chosen if c not in df_columns]
#     if missing:
#         print("\nERROR: The following columns are not needed in the file:")
#         for m in missing:
#             suggestion = difflib.get_close_matches(m, df_columns, n=1, cutoff=0.6)
#             if suggestion:
#                 print(f"  - {m} (did you mean: {suggestion[0]!r} ?)")
#             else:
#                 print(f"  - {m}")
#         sys.exit(1)

#     # Reorder to match the input file’s column order
#     chosen_set = set(chosen)
#     selected_cols_in_file_order = [c for c in df_columns if c in chosen_set]

#     print("\nApplied column order (following input file):")
#     for i, c in enumerate(selected_cols_in_file_order, 1):
#         print(f"{i:>2}. {c}")

#     return selected_cols_in_file_order

# # -------------------- Piped column helpers --------------------
# def is_piped_col(col_name: str) -> bool:
#     return " | " in col_name

# def split_header_into_sides(col_name: str) -> Tuple[str, str]:
#     left, right = [part.strip() for part in col_name.split("|", 1)]
#     return left, right

# def split_value_into_sides(value: str) -> Tuple[str, str]:
#     """
#     Split the cell value into left/right sides:
#     - Prefer ' | ' delimiter to preserve inner values exactly.
#     - If only '|' is present, split on that without trimming.
#     - If empty string, both sides empty.
#     """
#     if value is None:
#         return ("", "")
#     text = str(value)
#     if text == "":
#         return ("", "")
#     if " | " in text:
#         l, r = text.split(" | ", 1)
#         return (l, r)
#     if "|" in text:
#         l, r = text.split("|", 1)
#         return (l, r)
#     return (text, "")

# def starts_with_digit_str(v: str, digit: str) -> bool:
#     if v is None:
#         return False
#     v = str(v)
#     return len(v) > 0 and v[0] == digit

# # -------------------- Filtering: exclude rows where ALL keys are empty --------------------
# def filter_non_empty_key_rows(df: pd.DataFrame, key_cols: List[str]) -> pd.DataFrame:
#     """
#     Keep rows where at least ONE of the key columns is non-empty (after strip).
#     This prevents blank-key groups from inflating counts.
#     """
#     if not key_cols:
#         return df
#     # Ensure columns exist
#     cols = [c for c in key_cols if c in df.columns]
#     if not cols:
#         return df
#     # Replace NaN with empty string to simplify checks
#     df2 = df.where(df.notna(), "")
#     mask = ~df2[cols].apply(lambda row: all(str(v).strip() == "" for v in row.values), axis=1)
#     return df.loc[mask].copy()

# # -------------------- Grouping and totals (text data) --------------------
# def group_and_count_text(df: pd.DataFrame, group_cols: List[str]) -> pd.DataFrame:
#     """
#     Group and count with text columns; includes rows where some keys are empty strings.
#     Rows whose ALL keys are empty are excluded by a pre-filter (see caller).
#     """
#     grouped = (
#         df.groupby(group_cols, dropna=False)
#           .size()
#           .reset_index(name="Count")
#           .sort_values("Count", ascending=False)
#           .reset_index(drop=True)
#     )
#     return grouped

# def append_total_row_text(df_counts: pd.DataFrame, key_cols: List[str]) -> pd.DataFrame:
#     total_val = int(df_counts["Count"].sum()) if not df_counts.empty else 0
#     # Leave keys empty for Total row except the first which is labeled "Total"
#     total_row = {k: "" for k in key_cols}
#     if key_cols:
#         total_row[key_cols[0]] = "Total"
#     total_row["Count"] = total_val
#     return pd.concat([df_counts, pd.DataFrame([total_row])], ignore_index=True)

# # -------------------- Build category sheets (preserve file order) --------------------
# def build_category_frame_file_order(
#     base_df: pd.DataFrame,
#     selected_cols_in_file_order: List[str],
#     http_pipe_col: str,
#     category_digit: str  # '0', '4', or '5'
# ):
#     """
#     Build a DataFrame for one category, preserving the input-file order of selected columns.
#     For each piped column, expand to side headers at the same position:
#         - 5xx: left header only
#         - 4xx: right header only
#         - 0xx: include left then right if they appear in data
#     """
#     piped_cols = [c for c in selected_cols_in_file_order if is_piped_col(c)]
#     non_piped_cols = [c for c in selected_cols_in_file_order if not is_piped_col(c)]
#     pipe_header_map = {c: split_header_into_sides(c) for c in piped_cols}

#     records = []

#     # Iterate each row; selection happens by category rule (no rows skipped otherwise)
#     for _, row in base_df.iterrows():
#         http_val = row.get(http_pipe_col, "")
#         http_lval, http_rval = split_value_into_sides(http_val)

#         sides_to_emit = []
#         if starts_with_digit_str(http_lval, category_digit):
#             sides_to_emit.append("left")
#         if starts_with_digit_str(http_rval, category_digit):
#             sides_to_emit.append("right")

#         if not sides_to_emit:
#             continue

#         for side in sides_to_emit:
#             rec = {}
#             # Non-piped: copy as-is
#             for c in non_piped_cols:
#                 rec[c] = row.get(c, "")
#             # Piped: map to side header/value
#             for c in piped_cols:
#                 left_h, right_h = pipe_header_map[c]
#                 val = row.get(c, "")
#                 lval, rval = split_value_into_sides(val)
#                 if side == "left":
#                     rec[left_h] = lval
#                 else:
#                     rec[right_h] = rval
#             records.append(rec)

#     if not records:
#         # No rows matched this category
#         return pd.DataFrame(columns=selected_cols_in_file_order + ["Count"]), selected_cols_in_file_order

#     cat_df = pd.DataFrame(records)

#     # Build final column order using the file order; expand piped slots in-place
#     final_cols: List[str] = []
#     for c in selected_cols_in_file_order:
#         if c in non_piped_cols:
#             if c in cat_df.columns:
#                 final_cols.append(c)
#         else:
#             left_h, right_h = pipe_header_map[c]
#             if category_digit == "5":  # left only
#                 if left_h in cat_df.columns:
#                     final_cols.append(left_h)
#             elif category_digit == "4":  # right only
#                 if right_h in cat_df.columns:
#                     final_cols.append(right_h)
#             else:  # 0xx: include whichever exist, left then right
#                 if left_h in cat_df.columns:
#                     final_cols.append(left_h)
#                 if right_h in cat_df.columns:
#                     final_cols.append(right_h)

#     # 🚫 Remove rows where ALL final key columns are empty BEFORE grouping
#     cat_df = filter_non_empty_key_rows(cat_df, final_cols)
#     if cat_df.empty:
#         return pd.DataFrame(columns=final_cols + ["Count"]), final_cols

#     grouped = group_and_count_text(cat_df, final_cols)
#     grouped = append_total_row_text(grouped, final_cols)
#     return grouped, final_cols

# # -------------------- Avoid blank rows when writing --------------------
# def drop_truly_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
#     """
#     Remove rows that are 100% empty across all columns (after converting NaN -> "").
#     This is purely for presentation in Excel sheets.
#     """
#     if df.empty:
#         return df
#     df2 = df.where(df.notna(), "")
#     mask_nonempty = ~df2.apply(
#         lambda row: all((str(v).strip() == "") for v in row.values),
#         axis=1
#     )
#     return df.loc[mask_nonempty].copy()

# # -------------------- Excel writing (force TEXT cells, preserve exact values) --------------------
# def write_sheet_text(writer: pd.ExcelWriter, df: pd.DataFrame, sheet_name: str):
#     """
#     Write a DataFrame and then set every cell's number_format to '@' (Text) to preserve values exactly.
#     We DO NOT convert 'null' or other strings; we also leave true empties as empties.
#     """
#     # Presentation-only cleanup: drop rows that are entirely empty
#     df_clean = drop_truly_empty_rows(df)

#     # Replace any real NaNs with empty strings BEFORE converting to str
#     df_clean = df_clean.where(df_clean.notna(), "")

#     # Convert everything to string for Excel write; empty strings remain empty
#     df_out = df_clean.copy()
#     for c in df_out.columns:
#         df_out[c] = df_out[c].astype(str)

#     df_out.to_excel(writer, index=False, sheet_name=sheet_name)

#     # Enforce Excel "Text" format on all cells and best-effort autofit
#     try:
#         ws = writer.sheets[sheet_name]
#         from openpyxl.utils import get_column_letter
#         for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
#             for cell in row:
#                 cell.number_format = "@"
#         for idx, col in enumerate(df_out.columns, start=1):
#             series = df_out[col].astype(str)
#             max_len = max([len(str(col))] + [len(s) for s in series.head(2000)])
#             ws.column_dimensions[get_column_letter(idx)].width = min(60, max(10, max_len + 2))
#     except Exception:
#         pass

# # -------------------- Main --------------------
# def main():
#     # Load input strictly as text, preserving 'null' and blanks as-is
#     try:
#         df = load_input_as_text(INPUT_FILE)
#     except FileNotFoundError:
#         print(f"\nERROR: '{INPUT_FILE}' not found. Place the file next to this script and retry.")
#         sys.exit(1)

#     selected_cols_in_file_order = prompt_user_for_columns(df.columns.tolist())

#     # 🚫 Exclude rows where ALL selected keys are empty BEFORE grouping
#     df_for_grouping = filter_non_empty_key_rows(df, selected_cols_in_file_order)

#     # ---- required_columns
#     required_df = group_and_count_text(df_for_grouping, selected_cols_in_file_order)
#     required_df = append_total_row_text(required_df, selected_cols_in_file_order)

#     # Determine if category sheets are needed
#     http_pipe_cols = [
#         c for c in selected_cols_in_file_order
#         if is_piped_col(c) and ("httpstatuscode" in c.lower())
#     ]

#     with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
#         write_sheet_text(writer, required_df, "required_columns")

#         if http_pipe_cols:
#             http_pipe_col = http_pipe_cols[0]
#             five_df, _ = build_category_frame_file_order(df, selected_cols_in_file_order, http_pipe_col, "5")
#             if not five_df.empty:
#                 write_sheet_text(writer, five_df, "5xx_counts")

#             four_df, _ = build_category_frame_file_order(df, selected_cols_in_file_order, http_pipe_col, "4")
#             if not four_df.empty:
#                 write_sheet_text(writer, four_df, "4xx_counts")

#             zero_df, _ = build_category_frame_file_order(df, selected_cols_in_file_order, http_pipe_col, "0")
#             if not zero_df.empty:
#                 write_sheet_text(writer, zero_df, "0xx_counts")

#     print(f"\nSuccess! Wrote grouped results to: {OUTPUT_FILE}")
#     print(" - Sheet: required_columns")
#     if http_pipe_cols:
#         print(" - Sheets (if matches exist): 0xx_counts, 4xx_counts, 5xx_counts")

# if __name__ == "__main__":
#     main()






