
import pandas as pd
import json
from typing import Tuple, Any

INPUT_FILE = './merge_log_insights/logs-insights-results.xlsx'
OUTPUT_FILE = 'pg_refined.xlsx'

def extract_json_and_stacktrace(msg: str) -> Tuple[str, str]:
    """
    Extract the first balanced JSON object from the string and return (json_segment, stack_trace).
    If none found, returns ("", full_message_as_stack_trace).
    Handles quotes and escapes while scanning for matching braces.
    """
    if not isinstance(msg, str) or not msg:
        return "", ""

    s = msg.strip()
    start = s.find('{')
    if start == -1:
        # No JSON found; treat entire message as stack trace
        return "", s

    # Scan for matching closing '}' with awareness of strings/escapes
    in_str = False
    esc = False
    depth = 0
    end = -1

    for i, ch in enumerate(s[start:], start=start):
        if esc:
            esc = False
            continue
        if ch == '\\':
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if not in_str:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    end = i
                    break
    if end == -1:
        # Unbalanced; best effort: take until last '}'
        last = s.rfind('}')
        if last != -1 and last > start:
            end = last
        else:
            return "", s

    json_segment = s[start:end+1]
    stack_trace = s[end+1:].lstrip(': ').strip('\n')
    return json_segment, stack_trace

def clean_to_valid_json(json_segment: str) -> str:
    """
    Convert doubled-quote JSON to valid JSON if needed.
    """
    if not json_segment:
        return json_segment

    # Try as-is first
    try:
        json.loads(json_segment)
        return json_segment
    except Exception:
        pass

    cleaned = json_segment.replace('""', '"').strip()
    return cleaned

def try_json_loads(s: str) -> Any:
    try:
        return json.loads(s)
    except Exception:
        return None

def deep_parse_nested_strings(obj: Any) -> Any:
    """
    Recursively parse any string value that itself looks like JSON (starts with { or [).
    """
    if isinstance(obj, dict):
        return {k: deep_parse_nested_strings(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [deep_parse_nested_strings(v) for v in obj]
    if isinstance(obj, str):
        s = obj.strip()
        if (s.startswith('{') and s.endswith('}')) or (s.startswith('[') and s.endswith(']')):
            inner = try_json_loads(s)
            if inner is not None:
                return deep_parse_nested_strings(inner)
    return obj

def flatten(obj: Any, parent_key: str = '', sep: str = '.') -> dict:
    """
    Flatten nested dict/list into dot notation keys, with list indices included.
    Example:
      {'a': {'b': [ {'c':1}, {'c':2} ] }} -> {'a.b.0.c':1, 'a.b.1.c':2}
    """
    items = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
            items.extend(flatten(v, new_key, sep=sep).items())
    elif isinstance(obj, list):
        for idx, v in enumerate(obj):
            new_key = f"{parent_key}{sep}{idx}" if parent_key else str(idx)
            items.extend(flatten(v, new_key, sep=sep).items())
    else:
        items.append((parent_key, obj))
    return dict(items)

def stringify_exact(v: Any) -> str:
    """
    Convert values to strings EXACTLY for Excel output to prevent auto-formatting:
      - None (JSON null) -> "null"
      - booleans -> "true"/"false"
      - numbers -> plain string without scientific notation or separators
      - other types -> str(v)
    We don't add any commas, spaces, or quotes.
    """
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        # int -> exact decimal string
        return str(v)
    if isinstance(v, float):
        # Avoid scientific notation; keep as compact decimal if possible.
        # Using 'g' can still show scientific for very small/large. Prefer plain decimal if close to int.
        if v.is_integer():
            return str(int(v))
        # 15 significant digits to be safe without scientific notation
        s = f"{v:.15g}"
        return s
    # All other types (including already strings) -> str as-is
    return str(v)

def main():
    df = pd.read_excel(INPUT_FILE, engine='openpyxl')

    expected_cols = ['Date', 'Message', 'Count']
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        print(f"WARNING: Missing expected columns in input: {missing}. Available columns: {list(df.columns)}")

    result_rows = []
    all_keys_in_order = []
    seen = set()

    for _, row in df.iterrows():
        date_val = row.get('Date', None)
        message_val = row.get('Message', None)
        count_val = row.get('Count', None)

        json_seg, stack_trace = extract_json_and_stacktrace(str(message_val) if message_val is not None else '')
        cleaned = clean_to_valid_json(json_seg)

        parsed = None
        if cleaned:
            parsed = try_json_loads(cleaned)
            if parsed is None:
                # One more attempt for over-escaped sequences
                try:
                    try_alt = cleaned.encode('utf-8').decode('unicode_escape')
                except Exception:
                    try_alt = cleaned
                parsed = try_json_loads(try_alt)

        dynamic_flat = {}
        if isinstance(parsed, dict):
            parsed = deep_parse_nested_strings(parsed)
            dynamic_flat = flatten(parsed)

            # Convert ALL dynamic values to strings exactly to avoid Excel formatting issues
            for k, v in list(dynamic_flat.items()):
                dynamic_flat[k] = stringify_exact(v)
        else:
            if not stack_trace:
                stack_trace = str(message_val) if message_val is not None else ''

        # Track columns in first-seen order
        for k in dynamic_flat.keys():
            if k not in seen:
                seen.add(k)
                all_keys_in_order.append(k)

        # Build row; leave absent keys empty (we won't fill them here)
        result_row = {
            'Date': date_val,
            'Message': message_val,
            'Count': count_val,
            **dynamic_flat,
            'stack_trace': stack_trace,
        }
        result_rows.append(result_row)

    base_cols = ['Date', 'Message', 'Count']
    dynamic_cols = all_keys_in_order
    cols = base_cols + dynamic_cols + ['stack_trace']

    out_df = pd.DataFrame(result_rows, columns=cols)

    # Ensure cells are empty (not "nan") where keys are missing
    # (Only for dynamic cols and stack_trace; base cols remain whatever type they were)
    cols_to_blank = dynamic_cols + ['stack_trace']
    for c in cols_to_blank:
        # Replace NaN with empty string
        out_df[c] = out_df[c].where(out_df[c].notna(), '')

    # Write exactly; strings will remain strings in Excel
    out_df.to_excel(OUTPUT_FILE, index=False, engine='openpyxl')
    print(f"Wrote refined dataset to: {OUTPUT_FILE}\nRows: {len(out_df)}  Cols: {len(out_df.columns)}")

if __name__ == "__main__":
    main()



