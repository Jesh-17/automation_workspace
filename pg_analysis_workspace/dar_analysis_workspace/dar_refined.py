
import re
import sys
from collections import OrderedDict
import pandas as pd

INPUT_XLSX = 'logs-insights-results.xlsx'
OUTPUT_XLSX = 'dar_refined.xlsx'

def normalize_value_for_output(v):
    """
    Enforce value rules:
      - If v is None/NaN -> return "" (empty cell)
      - If v (string) equals 'null' (any case) -> return 'null'
      - Else return the string as-is (strip outer whitespace only)
    """
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""  # empty cell for missing
    if isinstance(v, str):
        s = v.strip()
        if s.lower() == 'null':
            return 'null'  # literal "null"
        return s
    return v  # numbers, etc.

def find_major_separator(text: str):
    """
    Find the FIRST occurrence of a colon that is surrounded by at least one space
    on one or both sides. This avoids matching 'error:' or 'key:value' tokens.
    Tries patterns in order of strictness.

    Returns a (start_index, end_index) span to slice left/right, or None if not found.
    """
    # Strict: at least one space on BOTH sides
    m = re.search(r'\s+:\s+', text)
    if m:
        return (m.start(), m.end())

    # Relaxed: at least one space on LEFT (right may be zero or more)
    m = re.search(r'\s+:\s*', text)
    if m:
        return (m.start(), m.end())

    # Relaxed: at least one space on RIGHT (left may be zero or more)
    m = re.search(r'\s*:\s+', text)
    if m:
        return (m.start(), m.end())

    return None

def parse_message(msg: str):
    """
    Parse Message into:
      - 1st_required: text up to the first ', '
      - kv: key:value pairs after the first ', ' and before the first spaced-colon separator
      - 2nd_required: text after the spaced-colon separator and before the first '{'
      - 3rd_required: text from the first '{' to the end (kept raw)
    Returns dict: { '1st_required', '2nd_required', '3rd_required', 'kv'(dict) }

    Empty/missing portions return "" (empty string). Literal 'null' stays 'null'.
    """
    result = {
        '1st_required': "",
        '2nd_required': "",
        '3rd_required': "",
        'kv': OrderedDict()
    }

    if not isinstance(msg, str) or not msg.strip():
        # Entire message missing -> all empty
        return result

    text = msg.strip()

    # 1) Split on the first " spaced-colon " separator (more tolerant to spaces)
    sep_span = find_major_separator(text)
    if sep_span:
        left = text[:sep_span[0]]
        right = text[sep_span[1]:]
    else:
        # If no spaced separator is found, treat everything as 'left'
        left = text
        right = ""

    # 2) From 'left': 1st_required up to the first ', ', then parse kv pairs in the remainder
    comma_idx = left.find(', ')
    if comma_idx == -1:
        first_required = left
        tail_for_kv = ""
    else:
        first_required = left[:comma_idx]
        tail_for_kv = left[comma_idx + 2:]  # after ", "

    # Normalize first_required for 'null' / empty
    first_required = normalize_value_for_output(first_required)

    # Parse key:value tokens (split by ', ', then on the first ':')
    kv = OrderedDict()
    if tail_for_kv:
        tokens = [t for t in (tok.strip() for tok in tail_for_kv.split(', ')) if t != ""]
        for tok in tokens:
            if ':' in tok:
                k, v = tok.split(':', 1)
                k = k.strip()
                v = v.strip()
                if k:
                    v = normalize_value_for_output(v)
                    kv[k] = v
            else:
                # Token without ":" is ignored for kv
                pass

    # 3) From 'right': 2nd_required up to first '{', 3rd_required from '{' to the end
    if right:
        brace_idx = right.find('{')
        if brace_idx == -1:
            # No JSON-looking block -> put all into 2nd_required
            second_required = right
            third_required = ""
        else:
            # Keep your rule: 2nd_required before '{', 3rd_required from '{' to end
            second_required = right[:brace_idx]
            third_required = right[brace_idx:]
    else:
        second_required = ""
        third_required = ""

    result['1st_required'] = first_required
    result['2nd_required'] = normalize_value_for_output(second_required)
    # Keep 3rd_required raw (only normalize empty vs 'null')
    result['3rd_required'] = normalize_value_for_output(third_required)
    result['kv'] = kv
    return result


def main():
    # Read input
    try:
        df = pd.read_excel(INPUT_XLSX, engine='openpyxl')
    except Exception as e:
        print(f"❌ Failed to read '{INPUT_XLSX}': {e}")
        print("   Ensure the file exists and openpyxl is available: pip install openpyxl")
        sys.exit(1)

    # Validate required columns (Date is optional)
    must_have = {'Message', 'Count'}
    missing = must_have - set(df.columns)
    if missing:
        print(f"❌ Missing required columns: {', '.join(sorted(missing))}. 'Date' is optional.")
        sys.exit(1)

    has_date = 'Date' in df.columns

    # Do NOT drop any rows
    df = df.copy()

    # Parse messages and collect all keys across rows in order of first appearance
    parsed_rows = []
    ordered_keys = []
    seen_keys = set()

    for _, row in df.iterrows():
        parsed = parse_message(row.get('Message', None))
        parsed_rows.append(parsed)

        for k in parsed['kv'].keys():
            if k not in seen_keys:
                seen_keys.add(k)
                ordered_keys.append(k)

    # Build output records (row count preserved 1:1 with input)
    out_records = []
    for i, row in df.iterrows():
        parsed = parsed_rows[i]
        rec = {}

        # Include Date only if present in input
        if has_date:
            rec['Date'] = normalize_value_for_output(row.get('Date'))

        # Always include Count as-is (if NaN -> becomes empty)
        rec['Count'] = normalize_value_for_output(row.get('Count'))

        # Parsed fields
        rec['1st_required'] = parsed['1st_required']

        # Key columns in stable order; if a key doesn't appear for a row -> empty
        for k in ordered_keys:
            rec[k] = parsed['kv'].get(k, "")

        rec['2nd_required'] = parsed['2nd_required']
        rec['3rd_required'] = parsed['3rd_required']

        out_records.append(rec)

    # Column order
    base_cols = (['Date'] if has_date else []) + ['Count', '1st_required']
    final_cols = base_cols + ordered_keys + ['2nd_required', '3rd_required']

    out_df = pd.DataFrame(out_records, columns=final_cols)

    # Write to Excel (empty strings remain empty cells; literal 'null' remains 'null')
    try:
        with pd.ExcelWriter(OUTPUT_XLSX, engine='openpyxl') as writer:
            out_df.to_excel(writer, index=False, sheet_name='Sheet1')
        print(f"✅ Wrote refined file: {OUTPUT_XLSX}")
        print(f"   Rows in/out: {len(df)} → {len(out_df)}")
        print(f"   Columns: {final_cols}")
    except Exception as e:
        print(f"❌ Failed to write '{OUTPUT_XLSX}': {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()




# import re
# import sys
# from collections import OrderedDict
# import pandas as pd

# INPUT_XLSX = 'logs-insights-results(nov1-nov30).xlsx'
# OUTPUT_XLSX = 'dar_refined.xlsx'

# def normalize_value_for_output(v):
#     """
#     Enforce value rules:
#       - If v is None/NaN -> return "" (empty cell)
#       - If v (string) equals 'null' (any case) -> return 'null'
#       - Else return the string as-is (strip only trailing newlines/spaces that are clearly accidental)
#     """
#     if v is None or (isinstance(v, float) and pd.isna(v)):
#         return ""  # empty cell for missing
#     if isinstance(v, str):
#         s = v.strip()
#         if s.lower() == 'null':
#             return 'null'  # literal "null"
#         return s  # keep actual text including empty "" if it was empty
#     return v  # numbers, etc.

# def parse_message(msg: str):
#     """
#     Parse Message into:
#       - 1st_required: text up to the first ', '
#       - kv: key:value pairs after the first ', ' and before the first ' : '
#       - 2nd_required: text after the first ' : ' and before the first '{'
#       - 3rd_required: text from the first '{' to the end
#     Returns dict: { '1st_required', '2nd_required', '3rd_required', 'kv'(dict) }

#     Empty/missing portions return "" (empty string). Literal 'null' stays 'null'.
#     """
#     result = {
#         '1st_required': "",
#         '2nd_required': "",
#         '3rd_required': "",
#         'kv': OrderedDict()
#     }

#     if not isinstance(msg, str) or not msg.strip():
#         # Entire message missing -> all empty
#         return result

#     text = msg.strip()

#     # 1) Split on the first " : " (space-colon-space), be tolerant to variable spaces
#     m_sep = re.search(r'\s:\s', text)
#     if m_sep:
#         left = text[:m_sep.start()]
#         right = text[m_sep.end():]
#     else:
#         # No " : " present, everything is 'left'
#         left = text
#         right = ""

#     # 2) From 'left': 1st_required up to first ', ', rest are kv pairs "key:value" separated by ', '
#     comma_idx = left.find(', ')
#     if comma_idx == -1:
#         first_required = left
#         tail_for_kv = ""
#     else:
#         first_required = left[:comma_idx]
#         tail_for_kv = left[comma_idx + 2:]  # after ", "

#     # Normalize first_required for 'null' / empty
#     first_required = normalize_value_for_output(first_required)

#     # Parse key:value tokens
#     kv = OrderedDict()
#     if tail_for_kv:
#         tokens = [t for t in (tok.strip() for tok in tail_for_kv.split(', ')) if t != ""]
#         for tok in tokens:
#             if ':' in tok:
#                 k, v = tok.split(':', 1)
#                 k = k.strip()
#                 v = v.strip()
#                 if k:  # only if we have a key
#                     # Preserve literal 'null'; if empty, keep as ""
#                     v = normalize_value_for_output(v)
#                     kv[k] = v
#             else:
#                 # Token without ":" is ignored for kv; 1st_required/2nd/3rd already cover context
#                 pass

#     # 3) From 'right': 2nd_required up to '{', and 3rd_required from '{' to end
#     if right:
#         brace_idx = right.find('{')
#         if brace_idx == -1:
#             second_required = right
#             third_required = ""
#         else:
#             second_required = right[:brace_idx]
#             third_required = right[brace_idx:]
#     else:
#         second_required = ""
#         third_required = ""

#     result['2nd_required'] = normalize_value_for_output(second_required)
#     # Keep 3rd_required raw (but still apply normalization for empty vs 'null')
#     result['3rd_required'] = normalize_value_for_output(third_required)
#     result['1st_required'] = first_required
#     result['kv'] = kv
#     return result


# def main():
#     # Read input
#     try:
#         df = pd.read_excel(INPUT_XLSX, engine='openpyxl')
#     except Exception as e:
#         print(f"❌ Failed to read '{INPUT_XLSX}': {e}")
#         print("   Ensure the file exists and openpyxl is available: pip install openpyxl")
#         sys.exit(1)

#     # Validate required columns (Date is optional)
#     must_have = {'Message', 'Count'}
#     missing = must_have - set(df.columns)
#     if missing:
#         print(f"❌ Missing required columns: {', '.join(sorted(missing))}. 'Date' is optional.")
#         sys.exit(1)

#     has_date = 'Date' in df.columns

#     # Do NOT drop any rows
#     df = df.copy()

#     # Parse messages and collect all keys across rows in order of first appearance
#     parsed_rows = []
#     ordered_keys = []
#     seen_keys = set()

#     for _, row in df.iterrows():
#         parsed = parse_message(row.get('Message', None))
#         parsed_rows.append(parsed)

#         for k in parsed['kv'].keys():
#             if k not in seen_keys:
#                 seen_keys.add(k)
#                 ordered_keys.append(k)

#     # Build output records (row count preserved 1:1 with input)
#     out_records = []
#     for i, row in df.iterrows():
#         parsed = parsed_rows[i]
#         rec = {}

#         # Include Date only if present in input
#         if has_date:
#             rec['Date'] = normalize_value_for_output(row.get('Date'))

#         # Always include Count as-is (if NaN -> becomes empty)
#         rec['Count'] = normalize_value_for_output(row.get('Count'))

#         # Parsed fields
#         rec['1st_required'] = parsed['1st_required']

#         # Key columns in stable order; if a key doesn't appear for a row -> empty
#         for k in ordered_keys:
#             rec[k] = parsed['kv'].get(k, "")

#         rec['2nd_required'] = parsed['2nd_required']
#         rec['3rd_required'] = parsed['3rd_required']

#         out_records.append(rec)

#     # Column order
#     base_cols = (['Date'] if has_date else []) + ['Count', '1st_required']
#     final_cols = base_cols + ordered_keys + ['2nd_required', '3rd_required']

#     out_df = pd.DataFrame(out_records, columns=final_cols)

#     # Write to Excel (empty strings remain empty cells; literal 'null' remains 'null')
#     try:
#         with pd.ExcelWriter(OUTPUT_XLSX, engine='openpyxl') as writer:
#             out_df.to_excel(writer, index=False, sheet_name='Sheet1')
#         print(f"✅ Wrote refined file: {OUTPUT_XLSX}")
#         print(f"   Rows in/out: {len(df)} → {len(out_df)}")
#         print(f"   Columns: {final_cols}")
#     except Exception as e:
#         print(f"❌ Failed to write '{OUTPUT_XLSX}': {e}")
#         sys.exit(1)


# if __name__ == '__main__':
#     main()
