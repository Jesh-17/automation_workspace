
# tickets_separation/alarms_separation.py
from typing import Set, Tuple
import os
import sys
import pandas as pd


def tickets_separation(
    input_path1: str = './wsr/output/parent_filling_using_ticket_tracker/parent_filling_using_ticket_tracker_in_this_day_wise_tiggered_alarms_list.xlsx',
    input_path2: str = './required_files/duration_alarms_list.xlsx',
    input_path3: str = './required_files/re_fine_tuning_alarms_list.xlsx',
    output_path: str = './tickets_separation/output/alarms_not_having_tickets.xlsx',
) -> str:
    """
    Build './tickets_separation/output/alarms_not_having_tickets.xlsx' with sheets:
      - 'duration_alarms'
      - 'refine_tuning_alarms'
      - 'alarms_required_tickets'

    Behavior:
      * Filters rows with empty EscalatedtoL3/AppSupportteam, Ticketnumber, Status
      * Splits via duration/refine lookups; remainder -> alarms_required_tickets
      * Aggregates by (AlarmDescription, Priority) with compact month-aware Date
      * Sorts: Priority (Critical → High → Major → Medium/Minor → Low/Warning → Info),
               then Count desc, then Alarm asc
      * Trims leading/trailing spaces from AlarmDescription & Priority
      * Dynamic date/time normalization to avoid parsing warnings
      * Progress bar is rendered dynamically based on percentage; final output:
            [██████████████████████████████] 100%
            Output: <absolute path>
    """

    # Constants
    READ_KW = dict(engine='openpyxl')
    COL_SNO = 'S.No'
    COL_DATE = 'Date'
    COL_TIME = 'Time'
    COL_ALARM_DESC = 'AlarmDescription'
    COL_PRIORITY = 'Priority'
    COL_HANDLED_L2 = 'HandledbyL2'
    COL_ESCALATED = 'EscalatedtoL3/AppSupportteam'
    COL_TICKET = 'Ticketnumber'
    COL_STATUS = 'Status'

    OUT_COL_DATE = 'Date'
    OUT_COL_DAYS = 'No Of Days Trigerred'
    OUT_COL_ALARM = 'AlarmDescription'
    OUT_COL_PRIORITY = 'Priority'
    OUT_COL_COUNT = 'Count of AlarmDescription'

    # ---- Progress helpers (DYNAMIC) ----
    def _render_bar(percentage: int) -> str:
        """Render a 30-char bar for a given 0..100 integer percentage."""
        bar_len = 30
        pct = max(0, min(100, int(percentage)))
        filled = int(bar_len * (pct / 100.0))
        return '█' * filled + '░' * (bar_len - filled)

    def _progress_update(percentage: int, message: str = '') -> None:
        """Inline dynamic progress bar; overwrites same line."""
        bar = _render_bar(percentage)
        sys.stdout.write(f"\r[{bar}] {percentage:>3}% {message:<40}")
        sys.stdout.flush()

    def _progress_done() -> None:
        """Write final 100% bar on its own line (no message)."""
        bar = _render_bar(100)
        sys.stdout.write(f"\r[{bar}] 100%\n")
        sys.stdout.flush()

    # ---- Helpers ----
    def norm_text(x) -> str:
        if pd.isna(x):
            return ''
        s = str(x)
        return ' '.join(s.split()).strip().lower()

    def _format_date_cell(x):
        """Dynamic date formatting: try parse; if OK -> 'MM/DD/YYYY'; else keep original; blank -> None."""
        if pd.isna(x) or str(x).strip() == '':
            return None
        try:
            dt = pd.to_datetime(x, errors='coerce')  # single pass (no warnings)
            return dt.strftime('%m/%d/%Y') if pd.notna(dt) else str(x)
        except Exception:
            return str(x)

    def _format_time_cell(x):
        """Dynamic time formatting: try parse; if OK -> 'hh:mm:ss AM/PM'; else keep original; blank -> None."""
        if pd.isna(x) or str(x).strip() == '':
            return None
        try:
            dt = pd.to_datetime(x, errors='coerce')
            return dt.strftime('%I:%M:%S %p') if pd.notna(dt) else str(x)
        except Exception:
            return str(x)

    def _strip_outer(x):
        """Trim only leading/trailing spaces; keep inner spaces."""
        if pd.isna(x):
            return None
        s = str(x).strip()
        return None if s == '' else s

    def read_tracker(path: str) -> pd.DataFrame:
        df = pd.read_excel(
            path,
            dtype={
                COL_TIME: 'object',
                COL_ALARM_DESC: 'object',
                COL_PRIORITY: 'object',
                COL_HANDLED_L2: 'object',
                COL_ESCALATED: 'object',
                COL_TICKET: 'object',
                COL_STATUS: 'object',
            },
            converters={COL_DATE: (lambda x: '' if pd.isna(x) else str(x))},
            **READ_KW,
        )
        df.columns = [c.strip() for c in df.columns]

        # Validate required columns
        required = [
            COL_SNO, COL_DATE, COL_TIME, COL_ALARM_DESC, COL_PRIORITY,
            COL_HANDLED_L2, COL_ESCALATED, COL_TICKET, COL_STATUS
        ]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns in input_path1: {missing}")

        # Normalize date/time
        df[COL_DATE] = df[COL_DATE].apply(_format_date_cell)
        df[COL_TIME] = df[COL_TIME].apply(_format_time_cell)

        # Trim outer spaces to prevent duplicates
        df[COL_ALARM_DESC] = df[COL_ALARM_DESC].apply(_strip_outer)
        df[COL_PRIORITY] = df[COL_PRIORITY].apply(_strip_outer)

        return df

    def read_lookup(path: str) -> Set[Tuple[str, str]]:
        df = pd.read_excel(path, **READ_KW)
        df.columns = [c.strip() for c in df.columns]
        if COL_ALARM_DESC not in df.columns or COL_PRIORITY not in df.columns:
            raise ValueError(f"Missing required columns in lookup file '{path}': ['{COL_ALARM_DESC}', '{COL_PRIORITY}']")
        pairs: Set[Tuple[str, str]] = set()
        for _, row in df.iterrows():
            a = norm_text(_strip_outer(row.get(COL_ALARM_DESC)))
            p = norm_text(_strip_outer(row.get(COL_PRIORITY)))
            if a and p:
                pairs.add((a, p))
        return pairs

    def filter_no_tickets(df: pd.DataFrame) -> pd.DataFrame:
        def is_empty(series: pd.Series) -> pd.Series:
            return series.isna() | (series.astype(str).str.strip() == '')
        mask = is_empty(df[COL_ESCALATED]) & is_empty(df[COL_TICKET]) & is_empty(df[COL_STATUS])
        return df.loc[mask].copy()

    def categorize(df: pd.DataFrame, duration_set: Set[Tuple[str, str]], refine_set: Set[Tuple[str, str]]):
        norm_alarm = df[COL_ALARM_DESC].apply(norm_text)
        norm_prio = df[COL_PRIORITY].apply(norm_text)
        key_series = pd.Series(list(zip(norm_alarm, norm_prio)), index=df.index)
        is_duration = key_series.apply(lambda k: k in duration_set)
        is_refine = key_series.apply(lambda k: k in refine_set)
        duration_df = df.loc[is_duration].copy()
        refine_df = df.loc[is_refine & ~is_duration].copy()  # duration has precedence
        required_df = df.loc[~(is_duration | is_refine)].copy()
        return duration_df, refine_df, required_df

    def aggregate(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=[OUT_COL_DATE, OUT_COL_DAYS, OUT_COL_ALARM, OUT_COL_PRIORITY, OUT_COL_COUNT])

        # Strict high → low priority map
        def priority_rank(p: str) -> int:
            #key = (p or '').strip().lower()
            key = '' if pd.isna(p) else str(p).strip().lower()
            mapping = {
                'critical': 1, 'p1': 1, 'sev1': 1,
                'high': 2,
                'major': 3, 'p2': 3, 'sev2': 3,
                'medium': 4, 'minor': 4, 'p3': 4, 'sev3': 4,
                'low': 5, 'warning': 5, 'p4': 5, 'sev4': 5,
                'info': 6, 'informational': 6
            }
            return mapping.get(key, 999)

        def format_dates_compact(date_series: pd.Series) -> str:
            s = date_series.dropna()
            s = s[s.astype(str).str.strip() != '']
            if s.empty:
                return ''
            s = s.astype(str)
            uniq_idx = s.drop_duplicates().index
            s_unique = s.loc[uniq_idx]
            dt_unique = pd.to_datetime(s_unique, errors='coerce')  # single pass
            if dt_unique.isna().any():
                return ','.join(list(s_unique))
            parts = []
            current_key = None
            for d in dt_unique:
                d = d.to_pydatetime().date()
                key = (d.year, d.month)
                if key != current_key:
                    parts.append(f"{d.strftime('%b')}-{d.day:02d}")
                    current_key = key
                else:
                    parts.append(f"{d.day:02d}")
            return ','.join(parts)

        grouped = df.groupby([COL_ALARM_DESC, COL_PRIORITY], dropna=False)
        rows = []
        for (alarm, prio), g in grouped:
            dates_compact = format_dates_compact(g[COL_DATE])
            unique_days = (
                g[COL_DATE]
                .dropna()
                .astype(str)
                .map(lambda z: z.strip())
                .replace('', pd.NA)
                .dropna()
                .drop_duplicates()
                .shape[0]
            )
            rows.append({
                OUT_COL_DATE: dates_compact,
                OUT_COL_DAYS: unique_days,
                OUT_COL_ALARM: alarm,
                OUT_COL_PRIORITY: prio,
                OUT_COL_COUNT: len(g)
            })

        out = pd.DataFrame(rows, columns=[OUT_COL_DATE, OUT_COL_DAYS, OUT_COL_ALARM, OUT_COL_PRIORITY, OUT_COL_COUNT])
        out['__prio_order'] = out[OUT_COL_PRIORITY].apply(priority_rank)
        out = out.sort_values(['__prio_order', OUT_COL_COUNT, OUT_COL_ALARM],
                              ascending=[True, False, True], kind='stable')
        out = out.drop(columns='__prio_order').reset_index(drop=True)
        return out

    # ---- Pipeline + dynamic progress bar ----
    _progress_update(5,  'Reading tracker...')
    tracker_df = read_tracker(input_path1)

    _progress_update(15, 'Reading duration lookup...')
    duration_lookup = read_lookup(input_path2)

    _progress_update(25, 'Reading refine lookup...')
    refine_lookup = read_lookup(input_path3)

    _progress_update(35, 'Filtering no-ticket rows...')
    no_ticket_df = filter_no_tickets(tracker_df)

    _progress_update(45, 'Categorizing...')
    duration_df, refine_df, required_df = categorize(no_ticket_df, duration_lookup, refine_lookup)

    _progress_update(60, 'Aggregating duration...')
    duration_out = aggregate(duration_df)

    _progress_update(75, 'Aggregating refine...')
    refine_out = aggregate(refine_df)

    _progress_update(90, 'Aggregating required...')
    required_out = aggregate(required_df)

    _progress_update(95, 'Preparing output folder...')
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    _progress_update(99, 'Writing Excel...')
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        duration_out.to_excel(writer, sheet_name='duration_alarms', index=False)
        refine_out.to_excel(writer, sheet_name='refine_tuning_alarms', index=False)
        required_out.to_excel(writer, sheet_name='alarms_required_tickets', index=False)

    # Final dynamic 100% bar + Output path
    _progress_update(100, '')
    _progress_done()
    print(f"Output: {os.path.abspath(output_path)}")

    return output_path
