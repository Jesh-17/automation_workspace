
import json
import sys
import re
from collections import defaultdict
import pandas as pd

INPUT_XLSX = 'dar_refined.xlsx'
OUTPUT_XLSX = 'sub_dar_refined.xlsx'
INPUT_SHEET = 0  # first sheet by default

def _looks_like_escaped_json(s: str) -> bool:
    """Heuristic: looks like {\"...\"} style or contains many escaped quotes."""
    return ('{\\"' in s) or ('\\"' in s and '{' in s and '}' in s)

def _strip_wrapping_quotes(s: str) -> str:
    """Remove a single layer of wrapping quotes if the whole payload is quoted."""
    if len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")):
        return s[1:-1]
    return s

def try_parse_json(raw):
    """
    Try to parse JSON from a cell value with robust fallbacks:
      1) direct json.loads
      2) if looks escaped (e.g., {\"a\":1}), unescape \" -> " and \\n, \\t, etc.
      3) if entire payload is quoted JSON, strip one layer of quotes and parse
      4) replace doubled quotes "" -> " (common in CSV/Excel)
      5) extract largest {...} substring and parse
    Returns parsed object or None if unparseable/empty.
    """
    if raw is None:
        return None
    if isinstance(raw, float) and pd.isna(raw):
        return None

    s = str(raw).strip()
    if not s:
        return None

    # 1) Direct parse
    try:
        return json.loads(s)
    except Exception:
        pass

    # 2) If the text is a quoted JSON payload, strip outer quotes and retry
    s_unquoted = _strip_wrapping_quotes(s)
    if s_unquoted != s:
        try:
            return json.loads(s_unquoted)
        except Exception:
            pass

    # 3) Escaped JSON like {\"key\":\"value\"} – unescape
    if _looks_like_escaped_json(s):
        try:
            # Interpret backslash escapes using Python's string codec
            # This will turn \" -> " and \\n -> newline, etc.
            s_unescaped = bytes(s, "utf-8").decode("unicode_escape")
            s_unescaped = _strip_wrapping_quotes(s_unescaped.strip())
            return json.loads(s_unescaped)
        except Exception:
            # Try only replacing \" -> " as a lighter fallback
            try:
                s_unescaped2 = s.replace('\\"', '"')
                s_unescaped2 = _strip_wrapping_quotes(s_unescaped2.strip())
                return json.loads(s_unescaped2)
            except Exception:
                pass

    # 4) Replace doubled quotes "" -> " (Excel/CSV artifact)
    try:
        s2 = s.replace('""', '"')
        return json.loads(s2)
    except Exception:
        pass

    # 5) Extract largest {...} core and parse
    if '{' in s and '}' in s and s.index('{') < s.rindex('}'):
        core = s[s.index('{'): s.rindex('}') + 1]
        # Try direct
        try:
            return json.loads(core)
        except Exception:
            # Try unescaping the core
            try:
                core_unescaped = bytes(core, "utf-8").decode("unicode_escape")
                core_unescaped = _strip_wrapping_quotes(core_unescaped.strip())
                return json.loads(core_unescaped)
            except Exception:
                # Last resort: replace \" -> "
                try:
                    core_unescaped2 = core.replace('\\"', '"')
                    core_unescaped2 = _strip_wrapping_quotes(core_unescaped2.strip())
                    return json.loads(core_unescaped2)
                except Exception:
                    pass

    # Not parseable
    return None

def collect_paths_no_index(obj, parent_key="", aggr=None):
    """
    Traverse JSON and collect leaf values in a dict: path -> list of values.
    - Dict keys: parent.child
    - List: recurse into items with the SAME parent key (NO index in key)
    - Leaf scalars: append to aggr[path]
    - Empty dicts/lists: record the path with a single empty value ('')
      so columns appear (e.g., 'headers' for "headers": {}) with blank cells.
    """
    if aggr is None:
        aggr = defaultdict(list)

    def join_key(pk, child):
        return f"{pk}.{child}" if pk else str(child)

    if isinstance(obj, dict):
        if not obj:
            if parent_key:
                aggr[parent_key].append("")  # empty object -> blank cell
        else:
            for k, v in obj.items():
                nk = join_key(parent_key, k)
                collect_paths_no_index(v, nk, aggr)
    elif isinstance(obj, list):
        if not obj:
            if parent_key:
                aggr[parent_key].append("")  # empty array -> blank cell
        else:
            for item in obj:
                collect_paths_no_index(item, parent_key, aggr)  # no index in the key
    else:
        # Scalar leaf (None/bool/num/str)
        if parent_key:
            aggr[parent_key].append(obj)

    return aggr

def normalize_scalar_for_cell(v):
    """
    Normalize a single scalar for a cell:
      - None -> 'null' (literal)
      - Empty string -> '' (blank)
      - Others -> as-is
    """
    if v is None:
        return 'null'
    if isinstance(v, float) and pd.isna(v):
        return ""
    if isinstance(v, str):
        return v  # keep exactly, including empty ""
    return v

def render_aggregated_values(vals):
    """
    Render list of values for one path into a single cell:
      - No values -> blank
      - One value -> normalized scalar
      - Many values -> JSON array string (order preserved; null/"" intact)
    """
    if not vals:
        return ""
    if len(vals) == 1:
        return normalize_scalar_for_cell(vals[0])
    try:
        return json.dumps(vals, ensure_ascii=False)
    except TypeError:
        safe_vals = []
        for v in vals:
            safe_vals.append(None if v is None else v)
        return json.dumps(safe_vals, ensure_ascii=False)

def main():
    # Load input
    try:
        df = pd.read_excel(INPUT_XLSX, sheet_name=INPUT_SHEET, engine='openpyxl')
    except Exception as e:
        print(f"❌ Failed to read '{INPUT_XLSX}': {e}")
        print("   Ensure the file exists and 'openpyxl' is installed: pip install openpyxl")
        sys.exit(1)

    # '3rd_required' is mandatory; 'Date' is optional. We ignore 'Count' entirely.
    if '3rd_required' not in df.columns:
        print("❌ Missing required column: '3rd_required'. 'Date' is optional.")
        sys.exit(1)

    has_date = 'Date' in df.columns
    df = df.copy()  # never drop rows

    # Parse + collect flattened paths per row; discover ordered columns globally
    per_row_flat = []
    ordered_keys = []
    seen_keys = set()
    parse_fail_count = 0

    for _, row in df.iterrows():
        raw = row.get('3rd_required', None)
        parsed = try_parse_json(raw)

        if parsed is None:
            aggr = defaultdict(list)  # no keys for this row
            # Count as parse failure only if there was non-empty content we couldn't parse
            if raw not in (None, "") and not (isinstance(raw, float) and pd.isna(raw)):
                parse_fail_count += 1
        else:
            aggr = collect_paths_no_index(parsed)

        # Discover global ordered keys by first appearance
        for k in aggr.keys():
            if k not in seen_keys:
                seen_keys.add(k)
                ordered_keys.append(k)

        per_row_flat.append(aggr)

    # Build output rows: Date? then flattened keys in stable order
    out_records = []
    for i, row in df.iterrows():
        rec = {}
        if has_date:
            date_val = row.get('Date', "")
            if isinstance(date_val, float) and pd.isna(date_val):
                date_val = ""
            rec['Date'] = date_val

        aggr = per_row_flat[i]
        for k in ordered_keys:
            rec[k] = render_aggregated_values(aggr.get(k, []))

        out_records.append(rec)

    base_cols = (['Date'] if has_date else [])
    final_cols = base_cols + ordered_keys

    out_df = pd.DataFrame(out_records, columns=final_cols)

    # Sanity: preserve 1:1 rows
    assert len(out_df) == len(df), "Row preservation failed (should never happen)."

    # Write output
    try:
        with pd.ExcelWriter(OUTPUT_XLSX, engine='openpyxl') as writer:
            out_df.to_excel(writer, index=False, sheet_name='Sheet1')
        print(f"✅ Wrote: {OUTPUT_XLSX}")
        print(f"   Rows in/out: {len(df)} → {len(out_df)} (1:1 preserved)")
        print(f"   Flattened columns: {len(ordered_keys)}")
        if parse_fail_count:
            print(f"   Note: {parse_fail_count} row(s) had unparseable JSON in '3rd_required'; those were left blank.")
    except Exception as e:
        print(f"❌ Failed to write '{OUTPUT_XLSX}': {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()





# import json
# import sys
# from collections import defaultdict
# import pandas as pd

# INPUT_XLSX = 'dar_refined.xlsx'
# OUTPUT_XLSX = 'sub_dar_refined.xlsx'
# INPUT_SHEET = 0  # first sheet by default

# def try_parse_json(raw):
#     """
#     Try to parse JSON from a cell value robustly.
#     Returns parsed object or None if unparseable/empty.
#     """
#     if raw is None:
#         return None
#     if isinstance(raw, float) and pd.isna(raw):
#         return None

#     s = str(raw)
#     if not s.strip():
#         return None

#     # 1) direct parse
#     try:
#         return json.loads(s)
#     except Exception:
#         pass

#     # 2) common log artifact: doubled quotes -> single
#     try:
#         s2 = s.replace('""', '"')
#         return json.loads(s2)
#     except Exception:
#         pass

#     # 3) extract the largest {...} substring and parse
#     if '{' in s and '}' in s and s.index('{') < s.rindex('}'):
#         core = s[s.index('{'): s.rindex('}') + 1]
#         try:
#             return json.loads(core)
#         except Exception:
#             pass

#     return None

# def collect_paths_no_index(obj, parent_key="", aggr=None):
#     """
#     Traverse JSON and collect leaf values in a dict: path -> list of values.
#     - Dict keys: parent.child
#     - List: recurse into items with the SAME parent key (NO index in key)
#     - Leaf scalars: append to aggr[path]
#     - Empty dicts/lists: record the path with a single empty value ('') so that
#       columns appear (e.g., 'headers' for "headers":{}) and the cell is empty.
#     """
#     if aggr is None:
#         aggr = defaultdict(list)

#     def join_key(pk, child):
#         return f"{pk}.{child}" if pk else str(child)

#     if isinstance(obj, dict):
#         if not obj:
#             if parent_key:
#                 aggr[parent_key].append("")  # empty object -> show column with blank cell
#         else:
#             for k, v in obj.items():
#                 nk = join_key(parent_key, k)
#                 collect_paths_no_index(v, nk, aggr)
#     elif isinstance(obj, list):
#         if not obj:
#             if parent_key:
#                 aggr[parent_key].append("")  # empty array -> show column with blank cell
#         else:
#             for item in obj:
#                 collect_paths_no_index(item, parent_key, aggr)  # no index in the key
#     else:
#         # scalar leaf (None/bool/num/str)
#         if parent_key:
#             aggr[parent_key].append(obj)

#     return aggr

# def normalize_scalar_for_cell(v):
#     """
#     Normalize a single scalar for a cell:
#       - None -> 'null' (literal text)
#       - Empty string -> '' (empty cell)
#       - Others -> returned as-is (bool/int/float/str)
#     """
#     if v is None:
#         return 'null'
#     if isinstance(v, float) and pd.isna(v):
#         return ""
#     if isinstance(v, str):
#         return v  # keep exactly as in input, including empty ""
#     return v

# def render_aggregated_values(vals):
#     """
#     Render list of values for a path into a single cell:
#       - If no values: return '' (blank)
#       - If one value: normalized scalar
#       - If multiple values: JSON array string preserving order
#         (null stays null, "" stays "")
#     """
#     if not vals:
#         return ""
#     if len(vals) == 1:
#         return normalize_scalar_for_cell(vals[0])
#     try:
#         return json.dumps(vals, ensure_ascii=False)
#     except TypeError:
#         # Fallback: stringify non-serializable elements safely
#         safe_vals = []
#         for v in vals:
#             if v is None:
#                 safe_vals.append(None)
#             else:
#                 safe_vals.append(v)
#         return json.dumps(safe_vals, ensure_ascii=False)

# def main():
#     # Load input
#     try:
#         df = pd.read_excel(INPUT_XLSX, sheet_name=INPUT_SHEET, engine='openpyxl')
#     except Exception as e:
#         print(f"❌ Failed to read '{INPUT_XLSX}': {e}")
#         print("   Ensure the file exists and 'openpyxl' is installed: pip install openpyxl")
#         sys.exit(1)

#     # '3rd_required' is mandatory here. 'Date' is optional. We ignore 'Count' entirely.
#     must_have = {'3rd_required'}
#     missing = must_have - set(df.columns)
#     if missing:
#         print(f"❌ Missing required column(s): {', '.join(sorted(missing))}. 'Date' is optional.")
#         sys.exit(1)

#     has_date = 'Date' in df.columns
#     df = df.copy()  # never drop rows

#     # Parse + collect flattened paths per row; discover ordered columns globally
#     per_row_flat = []
#     ordered_keys = []
#     seen_keys = set()
#     parse_fail_count = 0

#     for _, row in df.iterrows():
#         raw = row.get('3rd_required', None)
#         parsed = try_parse_json(raw)

#         if parsed is None:
#             aggr = defaultdict(list)  # no keys for this row
#             # Count parse failure only if cell wasn't blank and still couldn't parse
#             if raw not in (None, "") and not (isinstance(raw, float) and pd.isna(raw)):
#                 parse_fail_count += 1
#         else:
#             aggr = collect_paths_no_index(parsed)

#         # Discover global ordered keys by first appearance
#         for k in aggr.keys():
#             if k not in seen_keys:
#                 seen_keys.add(k)
#                 ordered_keys.append(k)

#         per_row_flat.append(aggr)

#     # Build output rows: Date? then flattened keys in stable order (no Count)
#     out_records = []
#     for i, row in df.iterrows():
#         rec = {}

#         if has_date:
#             date_val = row.get('Date', "")
#             if isinstance(date_val, float) and pd.isna(date_val):
#                 date_val = ""
#             rec['Date'] = date_val

#         aggr = per_row_flat[i]
#         for k in ordered_keys:
#             rec[k] = render_aggregated_values(aggr.get(k, []))

#         out_records.append(rec)

#     base_cols = (['Date'] if has_date else [])
#     final_cols = base_cols + ordered_keys

#     out_df = pd.DataFrame(out_records, columns=final_cols)

#     # Write output
#     try:
#         with pd.ExcelWriter(OUTPUT_XLSX, engine='openpyxl') as writer:
#             out_df.to_excel(writer, index=False, sheet_name='Sheet1')
#         print(f"✅ Wrote: {OUTPUT_XLSX}")
#         print(f"   Rows in/out: {len(df)} → {len(out_df)} (1:1 preserved)")
#         print(f"   Flattened columns: {len(ordered_keys)}")
#         if parse_fail_count:
#             print(f"   Note: {parse_fail_count} row(s) contained unparseable JSON; those cells were left blank.")
#     except Exception as e:
#         print(f"❌ Failed to write '{OUTPUT_XLSX}': {e}")
#         sys.exit(1)

# if __name__ == '__main__':
#     main()











# import json
# import sys
# from collections import OrderedDict, defaultdict
# import pandas as pd

# INPUT_XLSX = 'dar_refined.xlsx'
# OUTPUT_XLSX = 'sub_dar_refined.xlsx'
# INPUT_SHEET = 0  # first sheet by default

# def try_parse_json(raw):
#     """
#     Try to parse JSON from a cell value robustly.
#     Returns parsed object or None if unparseable/empty.
#     """
#     if raw is None:
#         return None
#     # Excel may give NaN for blanks
#     if isinstance(raw, float) and pd.isna(raw):
#         return None

#     s = str(raw)
#     if not s.strip():
#         return None

#     # 1) direct parse
#     try:
#         return json.loads(s)
#     except Exception:
#         pass

#     # 2) common log artifact: doubled quotes -> single
#     try:
#         s2 = s.replace('""', '"')
#         return json.loads(s2)
#     except Exception:
#         pass

#     # 3) extract the largest {...} substring and parse
#     if '{' in s and '}' in s and s.index('{') < s.rindex('}'):
#         core = s[s.index('{'): s.rindex('}') + 1]
#         try:
#             return json.loads(core)
#         except Exception:
#             pass

#     return None

# def collect_paths_no_index(obj, parent_key="", aggr=None):
#     """
#     Traverse JSON and collect leaf values in a dict: path -> list of values.
#     - Dict keys: parent.child
#     - List: recurse into items with the SAME parent key (NO index in key)
#     - Leaf scalars: append to aggr[path]
#     - **Empty dicts/lists**: record the path with a single empty value ('') so that
#       columns appear (e.g., 'headers' for "headers":{}) and cell is empty.
#     """
#     if aggr is None:
#         aggr = defaultdict(list)

#     def join_key(pk, child):
#         return f"{pk}.{child}" if pk else str(child)

#     if isinstance(obj, dict):
#         if not obj:
#             # Empty object should appear as a column with empty cell
#             if parent_key:
#                 aggr[parent_key].append("")
#         else:
#             for k, v in obj.items():
#                 nk = join_key(parent_key, k)
#                 collect_paths_no_index(v, nk, aggr)
#     elif isinstance(obj, list):
#         if not obj:
#             # Empty array should also appear as a column with empty cell
#             if parent_key:
#                 aggr[parent_key].append("")
#         else:
#             # Do not encode indices in the key; aggregate values under the same path
#             for item in obj:
#                 collect_paths_no_index(item, parent_key, aggr)
#     else:
#         # Scalar leaf (can be None/bool/num/str)
#         # Keep the path and append the raw value; null handled later
#         if parent_key:
#             aggr[parent_key].append(obj)

#     return aggr

# def normalize_scalar_for_cell(v):
#     """
#     Normalize a single scalar for a cell:
#       - None -> 'null' (literal text)
#       - Empty string -> '' (empty cell)
#       - Others -> returned as-is (bool/int/float/str)
#     """
#     if v is None:
#         return 'null'
#     if isinstance(v, float) and pd.isna(v):
#         return ""
#     if isinstance(v, str):
#         return v  # keep exactly as in input, including empty ""
#     return v

# def render_aggregated_values(vals):
#     """
#     Render list of values for a path into a single cell:
#       - If no values: return '' (blank)
#       - If one value: normalized scalar
#       - If multiple values: JSON array string preserving order (null stays null, "" stays "")
#     """
#     if not vals:
#         return ""
#     if len(vals) == 1:
#         return normalize_scalar_for_cell(vals[0])
#     try:
#         return json.dumps(vals, ensure_ascii=False)
#     except TypeError:
#         # Fallback: stringify non-serializable elements safely
#         safe_vals = []
#         for v in vals:
#             if v is None:
#                 safe_vals.append(None)
#             else:
#                 safe_vals.append(v)
#         return json.dumps(safe_vals, ensure_ascii=False)

# def main():
#     # Load input
#     try:
#         df = pd.read_excel(INPUT_XLSX, sheet_name=INPUT_SHEET, engine='openpyxl')
#     except Exception as e:
#         print(f"❌ Failed to read '{INPUT_XLSX}': {e}")
#         print("   Ensure the file exists and 'openpyxl' is installed: pip install openpyxl")
#         sys.exit(1)

#     # Validate required columns
#     must_have = {'Count', '3rd_required'}
#     missing = must_have - set(df.columns)
#     if missing:
#         print(f"❌ Missing required columns: {', '.join(sorted(missing))}. 'Date' is optional.")
#         sys.exit(1)

#     has_date = 'Date' in df.columns
#     df = df.copy()  # never drop rows

#     # Parse + collect flattened paths per row; discover ordered columns globally
#     per_row_flat = []
#     ordered_keys = []
#     seen_keys = set()
#     parse_fail_count = 0

#     for _, row in df.iterrows():
#         raw = row.get('3rd_required', None)
#         parsed = try_parse_json(raw)

#         if parsed is None:
#             aggr = defaultdict(list)  # no keys for this row
#             # Count a parse failure only if there was non-empty content that couldn't be parsed
#             if raw not in (None, "") and not (isinstance(raw, float) and pd.isna(raw)):
#                 parse_fail_count += 1
#         else:
#             aggr = collect_paths_no_index(parsed)

#         # Discover global ordered keys by first appearance
#         for k in aggr.keys():
#             if k not in seen_keys:
#                 seen_keys.add(k)
#                 ordered_keys.append(k)

#         per_row_flat.append(aggr)

#     # Build output rows: Date? Count, then flattened keys in stable order
#     out_records = []
#     for i, row in df.iterrows():
#         rec = {}

#         if has_date:
#             date_val = row.get('Date', "")
#             if isinstance(date_val, float) and pd.isna(date_val):
#                 date_val = ""
#             rec['Date'] = date_val

#         count_val = row.get('Count', "")
#         if isinstance(count_val, float) and pd.isna(count_val):
#             count_val = ""
#         rec['Count'] = count_val

#         aggr = per_row_flat[i]
#         for k in ordered_keys:
#             rec[k] = render_aggregated_values(aggr.get(k, []))

#         out_records.append(rec)

#     base_cols = (['Date'] if has_date else []) + ['Count']
#     final_cols = base_cols + ordered_keys

#     out_df = pd.DataFrame(out_records, columns=final_cols)

#     # Write output
#     try:
#         with pd.ExcelWriter(OUTPUT_XLSX, engine='openpyxl') as writer:
#             out_df.to_excel(writer, index=False, sheet_name='Sheet1')
#         print(f"✅ Wrote: {OUTPUT_XLSX}")
#         print(f"   Rows in/out: {len(df)} → {len(out_df)} (1:1 preserved)")
#         print(f"   Flattened columns: {len(ordered_keys)}")
#         if parse_fail_count:
#             print(f"   Note: {parse_fail_count} row(s) contained unparseable JSON; those cells were left blank.")
#     except Exception as e:
#         print(f"❌ Failed to write '{OUTPUT_XLSX}': {e}")
#         sys.exit(1)

# if __name__ == '__main__':
#     main()
