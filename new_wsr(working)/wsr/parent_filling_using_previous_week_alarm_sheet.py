import pandas as pd
from datetime import datetime
import os

def parent_filling_using_previous_week_alarm_sheet():
    """
    Reads current week and previous week alarm sheets.
    For alarms in current week with all three escalation columns empty,
    fills them using CHILD-FIRST (latest Date+Time) from previous week;
    if no child, fills using latest PARENT (AppSupport Pending preferred, else L3 Pending).
    Preserves original AlarmDescription casing, avoids writing 'nan' strings,
    and only fills when all three source fields are present (non-empty).
    """

    # Input files
    current_week_file = "./wsr/output/parent_filling_using_ticket_tracker/parent_filling_using_ticket_tracker_in_this_day_wise_tiggered_alarms_list.xlsx"
    previous_week_file = "./required_files/previous_week_day_wise_tiggered_alarms_list.xlsx"

    # Output file
    output_file = "./wsr/output/parent_filling_using_previous_week_alarm_sheet/parent_filling_using_previous_week_alarm_sheet_in_this_day_wise_tiggered_alarms_list.xlsx"

    # Delete old output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Old file '{output_file}' deleted.")

    print("Processing parent filling using previous week alarm sheet...")

    # Load both Excel files
    current_df = pd.read_excel(current_week_file, engine="openpyxl")
    previous_df = pd.read_excel(previous_week_file, engine="openpyxl")

    # Explicitly cast target columns to object (string-friendly)
    for col in ['EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status']:
        if col in current_df.columns:
            current_df[col] = current_df[col].astype('object')
        if col in previous_df.columns:
            previous_df[col] = previous_df[col].astype('object')

    # Create normalized keys for matching (do NOT overwrite AlarmDescription)
    # IMPORTANT: match only until the first '|'
    def to_alarm_key(val):
        s = str(val) if not pd.isna(val) else ''
        return s.split('|')[0].strip().lower()

    current_df['AlarmKey'] = current_df['AlarmDescription'].apply(to_alarm_key)
    previous_df['AlarmKey'] = previous_df['AlarmDescription'].apply(to_alarm_key)

    # Combine Date and Time for sorting (explicit format first, fallback flexible)
    for df in [current_df, previous_df]:
        dt_explicit = pd.to_datetime(
            df['Date'].astype(str).str.strip() + ' ' + df['Time'].astype(str).str.strip(),
            format='%m/%d/%Y %H:%M:%S',
            errors='coerce',
            utc=True
        )
        dt_fallback = pd.to_datetime(
            df['Date'].astype(str).str.strip() + ' ' + df['Time'].astype(str).str.strip(),
            format='mixed',
            errors='coerce',
            utc=True
        )
        df['DateTime'] = dt_explicit.fillna(dt_fallback)

    # Robust empty check (NaN, '', 'nan', 'none')
    def is_empty(val):
        if pd.isna(val):
            return True
        if isinstance(val, str):
            s = val.strip().lower()
            return s == '' or s == 'nan' or s == 'none'
        return False

    # Identify CHILD rows in previous week file
    prev_escalation_norm = previous_df['EscalatedtoL3/AppSupportteam'].astype(str).str.strip().str.lower()
    prev_status_norm = previous_df['Status'].astype(str).str.strip().str.lower()

    child_conditions = (
        (prev_escalation_norm == 'acknowledged by l2 team') &
        (prev_status_norm == 'closed')
    )
    children_df = previous_df[child_conditions].copy()

    # Identify PARENT rows in previous week file (AppSupport Pending OR L3 Pending)
    parent_conditions = (
        ((prev_escalation_norm == 'escalated to appsupport team') &
         (prev_status_norm == 'pending with appsupport team')) |
        ((prev_escalation_norm == 'escalated to l3 team') &
         (prev_status_norm == 'pending with l3 team'))
    )
    parents_df = previous_df[parent_conditions].copy()

    # Sort children and parents by DateTime (latest first)
    # Missing DateTime will sort to the end (fallback)
    children_df['SortKey'] = children_df['DateTime'].fillna(pd.Timestamp('1900-01-01'))
    parents_df['SortKey'] = parents_df['DateTime'].fillna(pd.Timestamp('1900-01-01'))
    children_df.sort_values(by='SortKey', ascending=False, inplace=True)
    parents_df.sort_values(by='SortKey', ascending=False, inplace=True)

    # Build latest-per-AlarmKey maps, but ONLY if all three fields are present (avoid 'nan' writes)
    def has_all_fields(row):
        return (not is_empty(row.get('EscalatedtoL3/AppSupportteam'))) and \
               (not is_empty(row.get('Ticketnumber'))) and \
               (not is_empty(row.get('Status')))

    # For CHILD map
    latest_children = children_df.drop_duplicates(subset=['AlarmKey'], keep='first')
    #latest_children = latest_children[latest_children.apply(has_all_fields, axis=1)]
    latest_children = latest_children[latest_children.apply(has_all_fields, axis=1)].copy()
    #child_map = latest_children.set_index('AlarmKey')[['EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status', 'DateTime']].to_dict('index')
    child_map = latest_children.set_index('AlarmKey')[['EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status', 'DateTime']].to_dict('index') if (not latest_children.empty and 'AlarmKey' in latest_children.columns) else {}


    # For PARENT map
    latest_parents = parents_df.drop_duplicates(subset=['AlarmKey'], keep='first')
    #latest_parents = latest_parents[latest_parents.apply(has_all_fields, axis=1)]
    latest_parents = latest_parents[latest_parents.apply(has_all_fields, axis=1)].copy()
    #parent_map = latest_parents.set_index('AlarmKey')[['EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status', 'DateTime']].to_dict('index')
    parent_map = latest_parents.set_index('AlarmKey')[['EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status', 'DateTime']].to_dict('index') if (not latest_parents.empty and 'AlarmKey' in latest_parents.columns) else {}

    # Track updates and skips
    updates_log = []
    skip_log = []

    # Fill missing current rows (update only if ALL three columns are empty)
    for idx, row in current_df.iterrows():
        esc = row.get('EscalatedtoL3/AppSupportteam')
        tkt = row.get('Ticketnumber')
        stat = row.get('Status')

        # Only update if all three are empty
        if is_empty(esc) and is_empty(tkt) and is_empty(stat):
            alarm_key = row['AlarmKey']

            # First priority: CHILD (latest) with all three fields present
            if alarm_key in child_map:
                data = child_map[alarm_key]
                current_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = data.get('EscalatedtoL3/AppSupportteam')
                current_df.at[idx, 'Ticketnumber'] = data.get('Ticketnumber')
                current_df.at[idx, 'Status'] = data.get('Status')
                dt_str = ''
                if pd.notna(data.get('DateTime')):
                    dt_str = str(data.get('DateTime'))
                updates_log.append(
                    f"Row {idx+1} updated with CHILD (latest) from previous week for alarm '{row['AlarmDescription']}' on {dt_str}"
                )

            # Second priority: PARENT (latest) with all three fields present
            elif alarm_key in parent_map:
                data = parent_map[alarm_key]
                current_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = data.get('EscalatedtoL3/AppSupportteam')
                current_df.at[idx, 'Ticketnumber'] = data.get('Ticketnumber')
                current_df.at[idx, 'Status'] = data.get('Status')
                dt_str = ''
                if pd.notna(data.get('DateTime')):
                    dt_str = str(data.get('DateTime'))
                updates_log.append(
                    f"Row {idx+1} updated with PARENT (latest) from previous week for alarm '{row['AlarmDescription']}' on {dt_str}"
                )
            else:
                skip_log.append(
                    f"Row {idx+1} skipped: No previous week CHILD/PARENT with complete data for alarm '{row['AlarmDescription']}'."
                )

    # Drop helper columns before saving
    current_df.drop(columns=['AlarmKey', 'DateTime'], inplace=True, errors='ignore')

    # Dynamic Date formatting (preserve values; format if parseable)
    if 'Date' in current_df.columns:
        def format_date(x):
            if is_empty(x):
                return None
            dt = pd.to_datetime(x, errors='coerce')
            return dt.strftime('%m/%d/%Y') if pd.notna(dt) else x
        current_df['Date'] = current_df['Date'].apply(format_date)

    # Dynamic Time formatting (to 12-hour AM/PM if parseable)
    if 'Time' in current_df.columns:
        def format_time(x):
            if is_empty(x):
                return None
            dt = pd.to_datetime(x, errors='coerce')
            return dt.strftime('%I:%M:%S %p') if pd.notna(dt) else x
        current_df['Time'] = current_df['Time'].apply(format_time)

    # Save updated file
    current_df.to_excel(output_file, index=False, engine="openpyxl")

    # Print summary log
    print(f"✅ Updated file saved to {output_file}")
    print(f"Total rows updated: {len(updates_log)}")
    if updates_log:
        print("\nDetails of updates:")
        for log in updates_log:
            print(log)

    if skip_log:
        print("\nℹ️ Rows skipped (with reasons):")
        for log in skip_log:
            print(log)
    elif len(updates_log) == 0:
        print("No rows were updated.")





# import pandas as pd
# from datetime import datetime
# import os

# def parent_filling_using_previous_week_alarm_sheet():
#     """
#     Reads current week and previous week alarm sheets.
#     For alarms in current week with all three escalation columns empty,
#     fills them using CHILD-FIRST (latest Date+Time) from previous week;
#     if no child, fills using latest PARENT (AppSupport Pending preferred, else L3 Pending).
#     Preserves original AlarmDescription casing, avoids writing 'nan' strings,
#     and only fills when all three source fields are present (non-empty).
#     """

#     # Input files
#     current_week_file = "./wsr/output/parent_filling_using_ticket_tracker/parent_filling_using_ticket_tracker_in_this_day_wise_tiggered_alarms_list.xlsx"
#     previous_week_file = "./required_files/previous_week_day_wise_tiggered_alarms_list.xlsx"

#     # Output file
#     output_file = "./wsr/output/parent_filling_using_previous_week_alarm_sheet/parent_filling_using_previous_week_alarm_sheet_in_this_day_wise_tiggered_alarms_list.xlsx"

#     # Delete old output file if it exists
#     if os.path.exists(output_file):
#         os.remove(output_file)
#         print(f"Old file '{output_file}' deleted.")

#     print("Processing parent filling using previous week alarm sheet...")

#     # Load both Excel files
#     current_df = pd.read_excel(current_week_file, engine="openpyxl")
#     previous_df = pd.read_excel(previous_week_file, engine="openpyxl")

#     # Explicitly cast target columns to object (string-friendly)
#     for col in ['EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status']:
#         if col in current_df.columns:
#             current_df[col] = current_df[col].astype('object')
#         if col in previous_df.columns:
#             previous_df[col] = previous_df[col].astype('object')

#     # Create normalized keys for matching (do NOT overwrite AlarmDescription)
#     # IMPORTANT: match only until the first '|'
#     def to_alarm_key(val):
#         s = str(val) if not pd.isna(val) else ''
#         return s.split('|')[0].strip().lower()

#     current_df['AlarmKey'] = current_df['AlarmDescription'].apply(to_alarm_key)
#     previous_df['AlarmKey'] = previous_df['AlarmDescription'].apply(to_alarm_key)

#     # Combine Date and Time for sorting (explicit format first, fallback flexible)
#     for df in [current_df, previous_df]:
#         dt_explicit = pd.to_datetime(
#             df['Date'].astype(str).str.strip() + ' ' + df['Time'].astype(str).str.strip(),
#             format='%m/%d/%Y %H:%M:%S',
#             errors='coerce',
#             utc=True
#         )
#         dt_fallback = pd.to_datetime(
#             df['Date'].astype(str).str.strip() + ' ' + df['Time'].astype(str).str.strip(),
#             format='mixed',
#             errors='coerce',
#             utc=True
#         )
#         df['DateTime'] = dt_explicit.fillna(dt_fallback)

#     # Robust empty check (NaN, '', 'nan', 'none')
#     def is_empty(val):
#         if pd.isna(val):
#             return True
#         if isinstance(val, str):
#             s = val.strip().lower()
#             return s == '' or s == 'nan' or s == 'none'
#         return False

#     # Identify CHILD rows in previous week file
#     prev_escalation_norm = previous_df['EscalatedtoL3/AppSupportteam'].astype(str).str.strip().str.lower()
#     prev_status_norm = previous_df['Status'].astype(str).str.strip().str.lower()

#     child_conditions = (
#         (prev_escalation_norm == 'acknowledged by l2 team') &
#         (prev_status_norm == 'closed')
#     )
#     children_df = previous_df[child_conditions].copy()

#     # Identify PARENT rows in previous week file (AppSupport Pending OR L3 Pending)
#     parent_conditions = (
#         ((prev_escalation_norm == 'escalated to appsupport team') &
#          (prev_status_norm == 'pending with appsupport team')) |
#         ((prev_escalation_norm == 'escalated to l3 team') &
#          (prev_status_norm == 'pending with l3 team'))
#     )
#     parents_df = previous_df[parent_conditions].copy()

#     # Sort children and parents by DateTime (latest first)
#     # Missing DateTime will sort to the end (fallback)
#     children_df['SortKey'] = children_df['DateTime'].fillna(pd.Timestamp('1900-01-01'))
#     parents_df['SortKey'] = parents_df['DateTime'].fillna(pd.Timestamp('1900-01-01'))
#     children_df.sort_values(by='SortKey', ascending=False, inplace=True)
#     parents_df.sort_values(by='SortKey', ascending=False, inplace=True)

#     # Build latest-per-AlarmKey maps, but ONLY if all three fields are present (avoid 'nan' writes)
#     def has_all_fields(row):
#         return (not is_empty(row.get('EscalatedtoL3/AppSupportteam'))) and \
#                (not is_empty(row.get('Ticketnumber'))) and \
#                (not is_empty(row.get('Status')))

#     # For CHILD map
#     latest_children = children_df.drop_duplicates(subset=['AlarmKey'], keep='first')
#     latest_children = latest_children[latest_children.apply(has_all_fields, axis=1)]
#     child_map = latest_children.set_index('AlarmKey')[['EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status', 'DateTime']].to_dict('index')

#     # For PARENT map
#     latest_parents = parents_df.drop_duplicates(subset=['AlarmKey'], keep='first')
#     latest_parents = latest_parents[latest_parents.apply(has_all_fields, axis=1)]
#     parent_map = latest_parents.set_index('AlarmKey')[['EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status', 'DateTime']].to_dict('index')

#     # Track updates and skips
#     updates_log = []
#     skip_log = []

#     # Fill missing current rows (update only if ALL three columns are empty)
#     for idx, row in current_df.iterrows():
#         esc = row.get('EscalatedtoL3/AppSupportteam')
#         tkt = row.get('Ticketnumber')
#         stat = row.get('Status')

#         # Only update if all three are empty
#         if is_empty(esc) and is_empty(tkt) and is_empty(stat):
#             alarm_key = row['AlarmKey']

#             # First priority: CHILD (latest) with all three fields present
#             if alarm_key in child_map:
#                 data = child_map[alarm_key]
#                 current_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = data.get('EscalatedtoL3/AppSupportteam')
#                 current_df.at[idx, 'Ticketnumber'] = data.get('Ticketnumber')
#                 current_df.at[idx, 'Status'] = data.get('Status')
#                 dt_str = ''
#                 if pd.notna(data.get('DateTime')):
#                     dt_str = str(data.get('DateTime'))
#                 updates_log.append(
#                     f"Row {idx+1} updated with CHILD (latest) from previous week for alarm '{row['AlarmDescription']}' on {dt_str}"
#                 )

#             # Second priority: PARENT (latest) with all three fields present
#             elif alarm_key in parent_map:
#                 data = parent_map[alarm_key]
#                 current_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = data.get('EscalatedtoL3/AppSupportteam')
#                 current_df.at[idx, 'Ticketnumber'] = data.get('Ticketnumber')
#                 current_df.at[idx, 'Status'] = data.get('Status')
#                 dt_str = ''
#                 if pd.notna(data.get('DateTime')):
#                     dt_str = str(data.get('DateTime'))
#                 updates_log.append(
#                     f"Row {idx+1} updated with PARENT (latest) from previous week for alarm '{row['AlarmDescription']}' on {dt_str}"
#                 )
#             else:
#                 skip_log.append(
#                     f"Row {idx+1} skipped: No previous week CHILD/PARENT with complete data for alarm '{row['AlarmDescription']}'."
#                 )

#     # Drop helper columns before saving
#     current_df.drop(columns=['AlarmKey', 'DateTime'], inplace=True, errors='ignore')

#     # Dynamic Date formatting (preserve values; format if parseable)
#     if 'Date' in current_df.columns:
#         def format_date(x):
#             if is_empty(x):
#                 return None
#             dt = pd.to_datetime(x, errors='coerce')
#             return dt.strftime('%m/%d/%Y') if pd.notna(dt) else x
#         current_df['Date'] = current_df['Date'].apply(format_date)

#     # Dynamic Time formatting (to 12-hour AM/PM if parseable)
#     if 'Time' in current_df.columns:
#         def format_time(x):
#             if is_empty(x):
#                 return None
#             dt = pd.to_datetime(x, errors='coerce')
#             return dt.strftime('%I:%M:%S %p') if pd.notna(dt) else x
#         current_df['Time'] = current_df['Time'].apply(format_time)

#     # Save updated file
#     current_df.to_excel(output_file, index=False, engine="openpyxl")

#     # Print summary log
#     print(f"✅ Updated file saved to {output_file}")
#     print(f"Total rows updated: {len(updates_log)}")
#     if updates_log:
#         print("\nDetails of updates:")
#         for log in updates_log:
#             print(log)

#     if skip_log:
#         print("\nℹ️ Rows skipped (with reasons):")
#         for log in skip_log:
#             print(log)
#     elif len(updates_log) == 0:
#         print("No rows were updated.")




# import pandas as pd
# from datetime import datetime
# import os

# def parent_filling_using_previous_week_alarm_sheet():
#     """
#     Reads current week and previous week alarm sheets.
#     For alarms in current week with all three escalation columns empty,
#     fills them using parent data from previous week (latest parent if multiple).
#     Preserves original AlarmDescription casing.
#     """

#     # Input files
#     current_week_file = "./wsr/output/parent_filling_using_ticket_tracker_in_this_day_wise_tiggered_alarms_list.xlsx"
#     previous_week_file = "./required_files/previous_week_day_wise_tiggered_alarms_list.xlsx"

#     # Output file
#     output_file = "./wsr/output/parent_filling_using_previous_week_alarm_sheet_in_this_day_wise_tiggered_alarms_list.xlsx"


#     #Delete old output file if it exists
#     if os.path.exists(output_file):
#         os.remove(output_file)
#         print(f"Old file '{output_file}' deleted.")
        

#     print("Processing parent filling using previous week alarm sheet...")

#     # Load both Excel files
#     current_df = pd.read_excel(current_week_file)
#     previous_df = pd.read_excel(previous_week_file)

#     # ✅ Explicitly cast target columns to object
#     for col in ['EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status']:
#         current_df[col] = current_df[col].astype('object')
#         previous_df[col] = previous_df[col].astype('object')

#     # ✅ Create normalized keys for matching (do NOT overwrite AlarmDescription)
#     current_df['AlarmKey'] = current_df['AlarmDescription'].astype(str).str.strip().str.lower()
#     previous_df['AlarmKey'] = previous_df['AlarmDescription'].astype(str).str.strip().str.lower()

#     # # ✅ Combine Date and Time for sorting
#     # for df in [current_df, previous_df]:
#     #     df['DateTime'] = pd.to_datetime(
#     #         df['Date'].astype(str) + ' ' + df['Time'].astype(str),
#     #         errors='coerce'
#     #     )

#     # ✅ Combine Date and Time for sorting with explicit format
#     for df in [current_df, previous_df]:
#         df['DateTime'] = pd.to_datetime(
#             df['Date'].astype(str) + ' ' + df['Time'].astype(str),
#             format='%m/%d/%Y %H:%M:%S',  # Adjust if your time is in 12-hour format
#             errors='coerce'
#         )


#     # ✅ Identify parent rows in previous week file
#     parent_conditions = (
#         ((previous_df['EscalatedtoL3/AppSupportteam'].str.strip().str.lower() == 'escalated to appsupport team') &
#          (previous_df['Status'].str.strip().str.lower() == 'pending with appsupport team')) |
#         ((previous_df['EscalatedtoL3/AppSupportteam'].str.strip().str.lower() == 'escalated to l3 team') &
#          (previous_df['Status'].str.strip().str.lower() == 'pending with l3 team'))
#     )
#     parents_df = previous_df[parent_conditions].copy()

#     # ✅ Sort parents by DateTime (latest first) and keep latest per AlarmKey
#     parents_df.sort_values(by='DateTime', ascending=False, inplace=True)
#     latest_parents = parents_df.drop_duplicates(subset=['AlarmKey'], keep='first')

#     # ✅ Create mapping from AlarmKey to parent details
#     parent_map = latest_parents.set_index('AlarmKey')[['EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status']].to_dict('index')

#     # ✅ Track updates for logging
#     updates_log = []

#     # ✅ Fill missing child rows (update only if ALL three columns are empty)
#     for idx, row in current_df.iterrows():
#         if pd.isna(row['EscalatedtoL3/AppSupportteam']) and pd.isna(row['Ticketnumber']) and pd.isna(row['Status']):
#             alarm_key = row['AlarmKey']
#             if alarm_key in parent_map:
#                 current_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = str(parent_map[alarm_key]['EscalatedtoL3/AppSupportteam'])
#                 current_df.at[idx, 'Ticketnumber'] = str(parent_map[alarm_key]['Ticketnumber'])
#                 current_df.at[idx, 'Status'] = str(parent_map[alarm_key]['Status'])
#                 updates_log.append(f"Row {idx+1} updated with previous week parent data for alarm '{row['AlarmDescription']}'")

#     # ✅ Drop helper columns before saving
#     current_df.drop(columns=['AlarmKey', 'DateTime'], inplace=True)

#     # ✅ Dynamic Date formatting
#     if 'Date' in current_df.columns:
#         def format_date(x):
#             if pd.isna(x) or str(x).strip() == '':
#                 return None
#             try:
#                 dt = pd.to_datetime(x, errors='coerce')
#                 return dt.strftime('%m/%d/%Y') if pd.notna(dt) else str(x)
#             except Exception:
#                 return str(x)
#         current_df['Date'] = current_df['Date'].apply(format_date)

#     # ✅ Dynamic Time formatting
#     if 'Time' in current_df.columns:
#         def format_time(x):
#             if pd.isna(x) or str(x).strip() == '':
#                 return None
#             try:
#                 dt = pd.to_datetime(x, errors='coerce')
#                 return dt.strftime('%I:%M:%S %p') if pd.notna(dt) else str(x)
#             except Exception:
#                 return str(x)
#         current_df['Time'] = current_df['Time'].apply(format_time)

#     # ✅ Save updated file
#     current_df.to_excel(output_file, index=False)

#     # ✅ Print summary log
#     print(f"✅ Updated file saved to {output_file}")
#     print(f"Total rows updated: {len(updates_log)}")
#     if updates_log:
#         print("\nDetails of updates:")
#         for log in updates_log:
#             print(log)
#     else:
#         print("No rows were updated.")














































































































































# import pandas as pd
# from datetime import datetime
# import os

# def parent_filling_using_previous_week_alarm_sheet():
#     """
#     Reads current week and previous week alarm sheets.
#     For alarms in current week with all three escalation columns empty,
#     fills them using parent data from previous week (latest parent if multiple).
#     Preserves original AlarmDescription casing.
#     """

#     # Input files
#     current_week_file = "./wsr/output/parent_filling_using_ticket_tracker_in_this_day_wise_tiggered_alarms_list.xlsx"
#     previous_week_file = "./required_files/previous_week_day_wise_tiggered_alarms_list.xlsx"

#     # Output file
#     output_file = "./wsr/output/parent_filling_using_previous_week_alarm_sheet_in_this_day_wise_tiggered_alarms_list.xlsx"


#     #Delete old output file if it exists
#     if os.path.exists(output_file):
#         os.remove(output_file)
#         print(f"Old file '{output_file}' deleted.")
        

#     print("Processing parent filling using previous week alarm sheet...")

#     # Load both Excel files
#     current_df = pd.read_excel(current_week_file)
#     previous_df = pd.read_excel(previous_week_file)

#     # ✅ Explicitly cast target columns to object
#     for col in ['EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status']:
#         current_df[col] = current_df[col].astype('object')
#         previous_df[col] = previous_df[col].astype('object')

#     # ✅ Create normalized keys for matching (do NOT overwrite AlarmDescription)
#     current_df['AlarmKey'] = current_df['AlarmDescription'].astype(str).str.strip().str.lower()
#     previous_df['AlarmKey'] = previous_df['AlarmDescription'].astype(str).str.strip().str.lower()

#     # ✅ Combine Date and Time for sorting
#     for df in [current_df, previous_df]:
#         df['DateTime'] = pd.to_datetime(
#             df['Date'].astype(str) + ' ' + df['Time'].astype(str),
#             errors='coerce'
#         )

#     # ✅ Identify parent rows in previous week file
#     parent_conditions = (
#         ((previous_df['EscalatedtoL3/AppSupportteam'].str.strip().str.lower() == 'escalated to appsupport team') &
#          (previous_df['Status'].str.strip().str.lower() == 'pending with appsupport team')) |
#         ((previous_df['EscalatedtoL3/AppSupportteam'].str.strip().str.lower() == 'escalated to l3 team') &
#          (previous_df['Status'].str.strip().str.lower() == 'pending with l3 team'))
#     )
#     parents_df = previous_df[parent_conditions].copy()

#     # ✅ Sort parents by DateTime (latest first) and keep latest per AlarmKey
#     parents_df.sort_values(by='DateTime', ascending=False, inplace=True)
#     latest_parents = parents_df.drop_duplicates(subset=['AlarmKey'], keep='first')

#     # ✅ Create mapping from AlarmKey to parent details
#     parent_map = latest_parents.set_index('AlarmKey')[['EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status']].to_dict('index')

#     # ✅ Track updates for logging
#     updates_log = []

#     # ✅ Fill missing child rows (update only if ALL three columns are empty)
#     for idx, row in current_df.iterrows():
#         if pd.isna(row['EscalatedtoL3/AppSupportteam']) and pd.isna(row['Ticketnumber']) and pd.isna(row['Status']):
#             alarm_key = row['AlarmKey']
#             if alarm_key in parent_map:
#                 current_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = str(parent_map[alarm_key]['EscalatedtoL3/AppSupportteam'])
#                 current_df.at[idx, 'Ticketnumber'] = str(parent_map[alarm_key]['Ticketnumber'])
#                 current_df.at[idx, 'Status'] = str(parent_map[alarm_key]['Status'])
#                 updates_log.append(f"Row {idx+1} updated with previous week parent data for alarm '{row['AlarmDescription']}'")

#     # ✅ Drop helper columns before saving
#     current_df.drop(columns=['AlarmKey', 'DateTime'], inplace=True)

#     # ✅ Dynamic Date formatting
#     if 'Date' in current_df.columns:
#         def format_date(x):
#             if pd.isna(x) or str(x).strip() == '':
#                 return None
#             try:
#                 dt = pd.to_datetime(x, errors='coerce')
#                 return dt.strftime('%m/%d/%Y') if pd.notna(dt) else str(x)
#             except Exception:
#                 return str(x)
#         current_df['Date'] = current_df['Date'].apply(format_date)

#     # ✅ Dynamic Time formatting
#     if 'Time' in current_df.columns:
#         def format_time(x):
#             if pd.isna(x) or str(x).strip() == '':
#                 return None
#             try:
#                 dt = pd.to_datetime(x, errors='coerce')
#                 return dt.strftime('%I:%M:%S %p') if pd.notna(dt) else str(x)
#             except Exception:
#                 return str(x)
#         current_df['Time'] = current_df['Time'].apply(format_time)

#     # ✅ Save updated file
#     current_df.to_excel(output_file, index=False)

#     # ✅ Print summary log
#     print(f"✅ Updated file saved to {output_file}")
#     print(f"Total rows updated: {len(updates_log)}")
#     if updates_log:
#         print("\nDetails of updates:")
#         for log in updates_log:
#             print(log)
#     else:
#         print("No rows were updated.")















































