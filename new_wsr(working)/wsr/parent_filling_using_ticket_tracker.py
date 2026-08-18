import pandas as pd
from datetime import datetime
import os

def parent_filling_using_ticket_tracker():
    """
    Updates child alarms with ticket data from ticket tracker using per-row selection,
    with STRICT DATE GATE: if either child Date or tracker Ticket Assigned Date/Time is missing, do not fill.

    Matching:
      - Match alarms by AlarmDescription (substring before first '|').

    Sorting:
      - Sort tracker rows by 'Ticket Assigned Date/Time' descending (latest first).

    Per-row selection (child-first across dates):
      For each child row:
        1) Require child Date to be present (not NaT). If missing → SKIP.
        2) Consider tracker rows for that AlarmKey with non-missing TicketDateTime.
        3) Among those, consider only rows with TicketDateTime >= child.Date.
        4) Choose:
           a) Latest CHILD: Ticket Assigned To == 'L2 Team' AND Ticket Status == 'Closed'.
           b) If none, latest PARENT:
              - AppSupport team + Pending (preferred),
              - else L3 Team + Pending.
        5) If no eligible tracker row meets the above, SKIP this child row.

    Filling only when:
      - EscalatedtoL3/AppSupportteam, Ticketnumber, Status are all empty/NaN.

    Output:
      - Writes to: ./wsr/output/parent_filling_using_ticket_tracker_in_this_day_wise_tiggered_alarms_list.xlsx
      - Logs updates and explicit reasons for skips.
    """

    # Input files
    tracker_file = "./required_files/day_wise_ticket_tracker_list.xlsx"
    child_file = "./wsr/output/child_or_parent_corresponding_date/child_or_parent_corresponding_date_filled_in_this_day_wise_tiggered_alarms_list.xlsx"

    # Output file
    output_file = "./wsr/output/parent_filling_using_ticket_tracker/parent_filling_using_ticket_tracker_in_this_day_wise_tiggered_alarms_list.xlsx"

    # Delete old output file if exists
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Old file '{output_file}' deleted.")

    # --- Load files (engine specified for reliability) ---
    tracker_df = pd.read_excel(tracker_file, engine="openpyxl")
    child_df = pd.read_excel(child_file, engine="openpyxl")

    # Normalize column names
    tracker_df.columns = tracker_df.columns.str.strip()
    child_df.columns = child_df.columns.str.strip()

    # Validate required columns
    required_tracker_cols = [
        'AlarmDescription', 'Ticket Assigned Date/Time', 'JIRA Ticket No.',
        'Ticket Assigned To', 'Ticket Status'
    ]
    for col in required_tracker_cols:
        if col not in tracker_df.columns:
            raise KeyError(f"Column '{col}' not found in tracker file. Available columns: {tracker_df.columns.tolist()}")

    required_child_cols = [
        'AlarmDescription', 'EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status', 'Date'
    ]
    for col in required_child_cols:
        if col not in child_df.columns:
            raise KeyError(f"Column '{col}' not found in child file. Available columns: {child_df.columns.tolist()}")

    # --- Extract AlarmKey (substring before first '|') ---
    tracker_df['AlarmKey'] = tracker_df['AlarmDescription'].astype(str).str.split('|').str[0].str.strip()
    child_df['AlarmKey'] = child_df['AlarmDescription'].astype(str).str.split('|').str[0].str.strip()

    # --- Convert dates to datetime ---
    tracker_df['TicketDateTime'] = pd.to_datetime(tracker_df['Ticket Assigned Date/Time'], errors='coerce')
    child_df['ChildDateTime'] = pd.to_datetime(child_df['Date'], errors='coerce')

    # --- Sort tracker by latest date ---
    tracker_df = tracker_df.sort_values(by='TicketDateTime', ascending=False)

    # --- Helper functions for matching conditions (case-insensitive) ---
    def norm(s):
        return (s or '').strip().lower()

    def is_child_row(r):
        return norm(r.get('Ticket Assigned To')) == 'l2 team' and norm(r.get('Ticket Status')) == 'closed'

    def is_appsupport_parent_row(r):
        a = norm(r.get('Ticket Assigned To'))
        s = norm(r.get('Ticket Status'))
        return (a in {'appsupport team', 'app support team'}) and s == 'pending'

    def is_l3_parent_row(r):
        return norm(r.get('Ticket Assigned To')) == 'l3 team' and norm(r.get('Ticket Status')) == 'pending'

    def is_empty(val):
        return pd.isna(val) or (isinstance(val, str) and val.strip() == '')

    # Pre-group tracker by AlarmKey for faster per-row selection
    grouped = tracker_df.groupby('AlarmKey')

    updates_log = []
    skip_log = []

    for idx, row in child_df.iterrows():
        # Only update rows where the three target columns are all empty
        if not (is_empty(row['EscalatedtoL3/AppSupportteam']) and is_empty(row['Ticketnumber']) and is_empty(row['Status'])):
            continue

        alarm_key = row['AlarmKey']
        child_dt = row['ChildDateTime']

        # STRICT: Child date must be present
        if pd.isna(child_dt):
            skip_log.append(f"Row {idx+1} skipped: Child Date is missing for AlarmKey '{alarm_key}'.")
            continue

        # If AlarmKey not in tracker, skip
        if alarm_key not in grouped.groups:
            skip_log.append(f"Row {idx+1} skipped: AlarmKey '{alarm_key}' not found in tracker.")
            continue

        # Tracker rows for this alarm (latest first), exclude rows with missing TicketDateTime
        alarm_rows = grouped.get_group(alarm_key).sort_values(by='TicketDateTime', ascending=False)
        alarm_rows = alarm_rows[pd.notna(alarm_rows['TicketDateTime'])]

        if alarm_rows.empty:
            skip_log.append(f"Row {idx+1} skipped: All tracker tickets for AlarmKey '{alarm_key}' have missing TicketDateTime.")
            continue

        # Eligible tickets: TicketDateTime >= child.Date
        eligible = alarm_rows[alarm_rows['TicketDateTime'] >= child_dt]
        if eligible.empty:
            skip_log.append(f"Row {idx+1} skipped: No tracker ticket with TicketDateTime >= child.Date for AlarmKey '{alarm_key}'.")
            continue

        # 1) CHILD-first among eligible (latest first)
        child_candidates = eligible[eligible.apply(is_child_row, axis=1)]
        chosen = None
        selection_type = None

        if not child_candidates.empty:
            chosen = child_candidates.iloc[0]
            selection_type = 'child'
        else:
            # 2) Parent (AppSupport Pending preferred, else L3 Pending)
            appsupport_candidates = eligible[eligible.apply(is_appsupport_parent_row, axis=1)]
            l3_candidates = eligible[eligible.apply(is_l3_parent_row, axis=1)]

            if not appsupport_candidates.empty:
                chosen = appsupport_candidates.iloc[0]
                selection_type = 'parent_appsupport'
            elif not l3_candidates.empty:
                chosen = l3_candidates.iloc[0]
                selection_type = 'parent_l3'
            else:
                skip_log.append(f"Row {idx+1} skipped: No eligible child/parent tickets for AlarmKey '{alarm_key}' on/after child.Date.")
                continue

        # Final safety: chosen must have non-missing TicketDateTime
        if pd.isna(chosen['TicketDateTime']):
            skip_log.append(f"Row {idx+1} skipped: Chosen tracker row has missing TicketDateTime for AlarmKey '{alarm_key}'.")
            continue

        # Fill based on selection type
        jira = chosen['JIRA Ticket No.']

        if selection_type == 'child':
            child_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = 'Acknowledged by L2 Team'
            child_df.at[idx, 'Status'] = 'Closed'
            child_df.at[idx, 'Ticketnumber'] = jira
            updates_log.append(f"Row {idx+1} updated (CHILD) for '{alarm_key}' → L2 Closed, JIRA {jira}")

        elif selection_type == 'parent_appsupport':
            child_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = 'Escalated to AppSupport team'
            child_df.at[idx, 'Status'] = 'Pending with AppSupport team'
            child_df.at[idx, 'Ticketnumber'] = jira
            updates_log.append(f"Row {idx+1} updated (PARENT) for '{alarm_key}' → AppSupport Pending, JIRA {jira}")

        elif selection_type == 'parent_l3':
            child_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = 'Escalated to L3 team'
            child_df.at[idx, 'Status'] = 'Pending with L3 team'
            child_df.at[idx, 'Ticketnumber'] = jira
            updates_log.append(f"Row {idx+1} updated (PARENT) for '{alarm_key}' → L3 Pending, JIRA {jira}")

    # --- Drop helper columns and save ---
    child_df.drop(columns=['AlarmKey', 'ChildDateTime'], inplace=True)
    child_df.to_excel(output_file, index=False, engine="openpyxl")

    # --- Print summary ---
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
        print("No rows were updated, and no eligible matches were found.")







































































# Old process: first priority to parent and later child
# import pandas as pd
# from datetime import datetime
# import os

# def parent_filling_using_ticket_tracker():
#     """
#     Updates child alarms with parent data from ticket tracker.
#     For each alarm, checks rows in descending date order until a parent condition is found.
#     If no parent found, fallback to L2 Team Closed ticket.
#     Only updates if child alarm date <= ticket date.
#     """

#     # Input files
#     tracker_file = "./required_files/day_wise_ticket_tracker_list.xlsx"
#     child_file = "./wsr/output/child_or_parent_corresponding_date_filled_in_this_day_wise_tiggered_alarms_list.xlsx"

#     # Output file
#     output_file = "./wsr/output/parent_filling_using_ticket_tracker_in_this_day_wise_tiggered_alarms_list.xlsx"

#     # Delete old output file if exists
#     if os.path.exists(output_file):
#         os.remove(output_file)
#         print(f"Old file '{output_file}' deleted.")

#     # Load files
#     tracker_df = pd.read_excel(tracker_file)
#     child_df = pd.read_excel(child_file)

#     # Normalize column names
#     tracker_df.columns = tracker_df.columns.str.strip()
#     child_df.columns = child_df.columns.str.strip()

#     # Validate required columns
#     required_tracker_cols = ['AlarmDescription', 'Ticket Assigned Date/Time', 'JIRA Ticket No.', 'Ticket Assigned To', 'Ticket Status']
#     for col in required_tracker_cols:
#         if col not in tracker_df.columns:
#             raise KeyError(f"Column '{col}' not found in tracker file. Available columns: {tracker_df.columns.tolist()}")

#     required_child_cols = ['AlarmDescription', 'EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status', 'Date']
#     for col in required_child_cols:
#         if col not in child_df.columns:
#             raise KeyError(f"Column '{col}' not found in child file. Available columns: {child_df.columns.tolist()}")

#     # Extract alarm key (before first '|')
#     tracker_df['AlarmKey'] = tracker_df['AlarmDescription'].astype(str).str.split('|').str[0].str.strip()
#     child_df['AlarmKey'] = child_df['AlarmDescription'].astype(str).str.split('|').str[0].str.strip()

#     # Convert dates to datetime
#     tracker_df['TicketDateTime'] = pd.to_datetime(tracker_df['Ticket Assigned Date/Time'], errors='coerce')
#     child_df['ChildDateTime'] = pd.to_datetime(child_df['Date'], errors='coerce')

#     # Sort tracker by latest date
#     tracker_df = tracker_df.sort_values(by='TicketDateTime', ascending=False)

#     # Build mapping with parent condition and fallback
#     parent_map = {}
#     for alarm in tracker_df['AlarmKey'].unique():
#         alarm_rows = tracker_df[tracker_df['AlarmKey'] == alarm].sort_values(by='TicketDateTime', ascending=False)
#         parent_row = None
#         fallback_row = None

#         # Check for parent condition first
#         for _, row in alarm_rows.iterrows():
#             assigned_to = str(row['Ticket Assigned To']).strip().lower()
#             status = str(row['Ticket Status']).strip().lower()
#             if (assigned_to == 'appsupport team' and status == 'pending') or \
#                (assigned_to == 'l3 team' and status == 'pending'):
#                 parent_row = row
#                 break

#         # If no parent found, check fallback (L2 Team Closed)
#         if parent_row is None:
#             for _, row in alarm_rows.iterrows():
#                 assigned_to = str(row['Ticket Assigned To']).strip().lower()
#                 status = str(row['Ticket Status']).strip().lower()
#                 if assigned_to == 'l2 team' and status == 'closed':
#                     fallback_row = row
#                     break

#         # Save whichever is found
#         if parent_row is not None:
#             parent_map[alarm] = {
#                 'Ticket Assigned To': parent_row['Ticket Assigned To'],
#                 'JIRA Ticket No.': parent_row['JIRA Ticket No.'],
#                 'Ticket Status': parent_row['Ticket Status'],
#                 'TicketDateTime': parent_row['TicketDateTime'],
#                 'Type': 'Parent'
#             }
#         elif fallback_row is not None:
#             parent_map[alarm] = {
#                 'Ticket Assigned To': fallback_row['Ticket Assigned To'],
#                 'JIRA Ticket No.': fallback_row['JIRA Ticket No.'],
#                 'Ticket Status': fallback_row['Ticket Status'],
#                 'TicketDateTime': fallback_row['TicketDateTime'],
#                 'Type': 'Fallback'
#             }

#     # Update child file
#     updates_log = []
#     for idx, row in child_df.iterrows():
#         if pd.isna(row['EscalatedtoL3/AppSupportteam']) and pd.isna(row['Ticketnumber']) and pd.isna(row['Status']):
#             alarm_key = row['AlarmKey']
#             if alarm_key in parent_map:
#                 parent_data = parent_map[alarm_key]
#                 child_date = row['ChildDateTime']
#                 parent_date = parent_data['TicketDateTime']

#                 # Skip if child alarm date > ticket date
#                 if pd.notna(child_date) and pd.notna(parent_date) and child_date > parent_date:
#                     continue

#                 # Fill based on type
#                 if parent_data['Type'] == 'Parent':
#                     if str(parent_data['Ticket Assigned To']).strip().lower() == 'appsupport team':
#                         child_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = 'Escalated to AppSupport team'
#                         child_df.at[idx, 'Status'] = 'Pending with AppSupport team'
#                     elif str(parent_data['Ticket Assigned To']).strip().lower() == 'l3 team':
#                         child_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = 'Escalated to L3 team'
#                         child_df.at[idx, 'Status'] = 'Pending with L3 team'
#                 elif parent_data['Type'] == 'Fallback':
#                     child_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = 'Acknowledged by L2 Team'
#                     child_df.at[idx, 'Status'] = 'Closed'

#                 child_df.at[idx, 'Ticketnumber'] = parent_data['JIRA Ticket No.']
#                 updates_log.append(f"Row {idx+1} updated for alarm '{alarm_key}' ({parent_data['Type']})")

#     # Drop helper columns
#     child_df.drop(columns=['AlarmKey', 'ChildDateTime'], inplace=True)

#     # Save updated file
#     child_df.to_excel(output_file, index=False)

#     # Print summary
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

# def parent_filling_using_ticket_tracker():
#     """
#     Updates child alarms with parent data from ticket tracker.
#     For each alarm, checks rows in descending date order until a parent condition is found.
#     Only updates if child alarm date <= parent ticket date.
#     """

#     # Input files
#     tracker_file = "./required_files/day_wise_ticket_tracker_list.xlsx"
#     child_file = "./wsr/output/child_or_parent_corresponding_date_filled_in_this_day_wise_tiggered_alarms_list.xlsx"

#     # Output file
#     output_file = "./wsr/output/parent_filling_using_ticket_tracker_in_this_day_wise_tiggered_alarms_list.xlsx"

#     # Delete old output file if exists
#     if os.path.exists(output_file):
#         os.remove(output_file)
#         print(f"Old file '{output_file}' deleted.")

#     # Load files
#     tracker_df = pd.read_excel(tracker_file)
#     child_df = pd.read_excel(child_file)

#     # Normalize column names
#     tracker_df.columns = tracker_df.columns.str.strip()
#     child_df.columns = child_df.columns.str.strip()

#     # Validate required columns
#     required_tracker_cols = ['AlarmDescription', 'Ticket Assigned Date/Time', 'JIRA Ticket No.', 'Ticket Assigned To', 'Ticket Status']
#     for col in required_tracker_cols:
#         if col not in tracker_df.columns:
#             raise KeyError(f"Column '{col}' not found in tracker file. Available columns: {tracker_df.columns.tolist()}")

#     required_child_cols = ['AlarmDescription', 'EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status', 'Date']
#     for col in required_child_cols:
#         if col not in child_df.columns:
#             raise KeyError(f"Column '{col}' not found in child file. Available columns: {child_df.columns.tolist()}")

#     # Extract alarm key (before first '|')
#     tracker_df['AlarmKey'] = tracker_df['AlarmDescription'].astype(str).str.split('|').str[0].str.strip()
#     child_df['AlarmKey'] = child_df['AlarmDescription'].astype(str).str.split('|').str[0].str.strip()

#     # Convert dates to datetime
#     tracker_df['TicketDateTime'] = pd.to_datetime(tracker_df['Ticket Assigned Date/Time'], errors='coerce')
#     child_df['ChildDateTime'] = pd.to_datetime(child_df['Date'], errors='coerce')

#     # Sort tracker by latest date
#     tracker_df = tracker_df.sort_values(by='TicketDateTime', ascending=False)

#     # Build parent mapping by checking rows iteratively
#     parent_map = {}
#     for alarm in tracker_df['AlarmKey'].unique():
#         alarm_rows = tracker_df[tracker_df['AlarmKey'] == alarm].sort_values(by='TicketDateTime', ascending=False)
#         parent_row = None
#         for _, row in alarm_rows.iterrows():
#             assigned_to = str(row['Ticket Assigned To']).strip().lower()
#             status = str(row['Ticket Status']).strip().lower()
#             if (assigned_to == 'appsupport team' and status == 'pending') or \
#                (assigned_to == 'l3 team' and status == 'pending'):
#                 parent_row = row
#                 break  # Stop at first matching parent condition
#         if parent_row is not None:
#             parent_map[alarm] = {
#                 'Ticket Assigned To': parent_row['Ticket Assigned To'],
#                 'JIRA Ticket No.': parent_row['JIRA Ticket No.'],
#                 'Ticket Status': parent_row['Ticket Status'],
#                 'TicketDateTime': parent_row['TicketDateTime']
#             }

#     # Update child file
#     updates_log = []
#     for idx, row in child_df.iterrows():
#         if pd.isna(row['EscalatedtoL3/AppSupportteam']) and pd.isna(row['Ticketnumber']) and pd.isna(row['Status']):
#             alarm_key = row['AlarmKey']
#             if alarm_key in parent_map:
#                 parent_data = parent_map[alarm_key]
#                 child_date = row['ChildDateTime']
#                 parent_date = parent_data['TicketDateTime']

#                 # ✅ Skip if child alarm date is greater than parent ticket date
#                 if pd.notna(child_date) and pd.notna(parent_date) and child_date > parent_date:
#                     continue

#                 # Fill data if condition passes
#                 if str(parent_data['Ticket Assigned To']).strip().lower() == 'appsupport team':
#                     child_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = 'Escalated to AppSupport team'
#                     child_df.at[idx, 'Status'] = 'Pending with AppSupport team'
#                 elif str(parent_data['Ticket Assigned To']).strip().lower() == 'l3 team':
#                     child_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = 'Escalated to L3 team'
#                     child_df.at[idx, 'Status'] = 'Pending with L3 team'
#                 child_df.at[idx, 'Ticketnumber'] = parent_data['JIRA Ticket No.']
#                 updates_log.append(f"Row {idx+1} updated for alarm '{alarm_key}'")

#     # Drop helper columns
#     child_df.drop(columns=['AlarmKey', 'ChildDateTime'], inplace=True)

#     # Save updated file
#     child_df.to_excel(output_file, index=False)

#     # Print summary
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

# def parent_filling_using_ticket_tracker():
#     """
#     Updates child alarms with parent data from ticket tracker.
#     For each alarm, checks rows in descending date order until a parent condition is found.
#     """

#     # Input files
#     tracker_file = "./required_files/day_wise_ticket_tracker_list.xlsx"
#     child_file = "./wsr/output/child_or_parent_corresponding_date_filled_in_this_day_wise_tiggered_alarms_list.xlsx"

#     # Output file
#     output_file = "./wsr/output/parent_filling_using_ticket_tracker_in_this_day_wise_tiggered_alarms_list.xlsx"

#     # Delete old output file if exists
#     if os.path.exists(output_file):
#         os.remove(output_file)
#         print(f"Old file '{output_file}' deleted.")

#     # Load files
#     tracker_df = pd.read_excel(tracker_file)
#     child_df = pd.read_excel(child_file)

#     # Normalize column names
#     tracker_df.columns = tracker_df.columns.str.strip()
#     child_df.columns = child_df.columns.str.strip()

#     # Validate required columns
#     required_tracker_cols = ['AlarmDescription', 'Ticket Assigned Date/Time', 'JIRA Ticket No.', 'Ticket Assigned To', 'Ticket Status']
#     for col in required_tracker_cols:
#         if col not in tracker_df.columns:
#             raise KeyError(f"Column '{col}' not found in tracker file. Available columns: {tracker_df.columns.tolist()}")

#     required_child_cols = ['AlarmDescription', 'EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status']
#     for col in required_child_cols:
#         if col not in child_df.columns:
#             raise KeyError(f"Column '{col}' not found in child file. Available columns: {child_df.columns.tolist()}")

#     # Extract alarm key (before first '|')
#     tracker_df['AlarmKey'] = tracker_df['AlarmDescription'].astype(str).str.split('|').str[0].str.strip()
#     child_df['AlarmKey'] = child_df['AlarmDescription'].astype(str).str.split('|').str[0].str.strip()

#     # Convert Ticket Assigned Date/Time to datetime
#     tracker_df['TicketDateTime'] = pd.to_datetime(tracker_df['Ticket Assigned Date/Time'], errors='coerce')

#     # Sort tracker by latest date
#     tracker_df = tracker_df.sort_values(by='TicketDateTime', ascending=False)

#     # Build parent mapping by checking rows iteratively
#     parent_map = {}
#     for alarm in tracker_df['AlarmKey'].unique():
#         alarm_rows = tracker_df[tracker_df['AlarmKey'] == alarm].sort_values(by='TicketDateTime', ascending=False)
#         parent_row = None
#         for _, row in alarm_rows.iterrows():
#             assigned_to = str(row['Ticket Assigned To']).strip().lower()
#             status = str(row['Ticket Status']).strip().lower()
#             if (assigned_to == 'appsupport team' and status == 'pending') or \
#                (assigned_to == 'l3 team' and status == 'pending'):
#                 parent_row = row
#                 break  # Stop at first matching parent condition
#         if parent_row is not None:
#             parent_map[alarm] = {
#                 'Ticket Assigned To': parent_row['Ticket Assigned To'],
#                 'JIRA Ticket No.': parent_row['JIRA Ticket No.'],
#                 'Ticket Status': parent_row['Ticket Status']
#             }

#     # Update child file
#     updates_log = []
#     for idx, row in child_df.iterrows():
#         if pd.isna(row['EscalatedtoL3/AppSupportteam']) and pd.isna(row['Ticketnumber']) and pd.isna(row['Status']):
#             alarm_key = row['AlarmKey']
#             if alarm_key in parent_map:
#                 parent_data = parent_map[alarm_key]
#                 if str(parent_data['Ticket Assigned To']).strip().lower() == 'appsupport team':
#                     child_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = 'Escalated to AppSupport team'
#                     child_df.at[idx, 'Status'] = 'Pending with AppSupport team'
#                 elif str(parent_data['Ticket Assigned To']).strip().lower() == 'l3 team':
#                     child_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = 'Escalated to L3 team'
#                     child_df.at[idx, 'Status'] = 'Pending with L3 team'
#                 child_df.at[idx, 'Ticketnumber'] = parent_data['JIRA Ticket No.']
#                 updates_log.append(f"Row {idx+1} updated for alarm '{alarm_key}'")

#     # Drop helper column
#     child_df.drop(columns=['AlarmKey'], inplace=True)

#     # Save updated file
#     child_df.to_excel(output_file, index=False)

#     # Print summary
#     print(f"✅ Updated file saved to {output_file}")
#     print(f"Total rows updated: {len(updates_log)}")
#     if updates_log:
#         print("\nDetails of updates:")
#         for log in updates_log:
#             print(log)
#     else:
#         print("No rows were updated.")






























































































# # Old process 
# import pandas as pd
# from datetime import datetime
# import os

# def parent_filling_using_ticket_tracker():
#     """
#     Reads the Excel file, identifies parent alarms, and fills missing columns for child alarms
#     using the latest parent data. Logs updates and saves the result with a timestamped filename.
#     """

#     # Input file
#     input_file = "./wsr/output/child_or_parent_corresponding_date_filled_in_this_day_wise_tiggered_alarms_list.xlsx"

#     # Dynamic output file name with timestamp
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     output_file = f"./wsr/output/parent_filling_using_ticket_tracker_in_this_day_wise_tiggered_alarms_list.xlsx"


#     #Delete old output file if it exists
#     if os.path.exists(output_file):
#         os.remove(output_file)
#         print(f"Old file '{output_file}' deleted.")


#     # Load the Excel file
#     df = pd.read_excel(input_file)

#     # ✅ Dynamic DateTime handling for sorting
#     try:
#         df['DateTime'] = pd.to_datetime(
#             df['Date'].astype(str).str.strip() + ' ' + df['Time'].astype(str).str.strip(),
#             errors='coerce'
#         )
#     except Exception:
#         # Fallback if format mismatch
#         df['DateTime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str), errors='coerce')

#     # Identify parent rows based on conditions
#     parent_conditions = (
#         ((df['EscalatedtoL3/AppSupportteam'] == 'Escalated to AppSupport team') & (df['Status'] == 'Pending with AppSupport team')) |
#         ((df['EscalatedtoL3/AppSupportteam'] == 'Escalated to L3 team') & (df['Status'] == 'Pending with L3 team'))
#     )
#     parents_df = df[parent_conditions].copy()

#     # Sort parents by DateTime (latest first) and keep latest per AlarmDescription
#     parents_df.sort_values(by='DateTime', ascending=False, inplace=True)
#     latest_parents = parents_df.drop_duplicates(subset=['AlarmDescription'], keep='first')

#     # Create mapping from AlarmDescription to parent details
#     parent_map = latest_parents.set_index('AlarmDescription')[['EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status']].to_dict('index')

#     # Track updates for logging
#     updates_log = []

#     # Fill missing child rows
#     for idx, row in df.iterrows():
#         # Only update if all three columns are empty
#         if pd.isna(row['EscalatedtoL3/AppSupportteam']) and pd.isna(row['Ticketnumber']) and pd.isna(row['Status']):
#             alarm_name = row['AlarmDescription']
#             if alarm_name in parent_map:
#                 df.at[idx, 'EscalatedtoL3/AppSupportteam'] = parent_map[alarm_name]['EscalatedtoL3/AppSupportteam']
#                 df.at[idx, 'Ticketnumber'] = parent_map[alarm_name]['Ticketnumber']
#                 df.at[idx, 'Status'] = parent_map[alarm_name]['Status']
#                 updates_log.append(f"Row {idx+1} updated with parent data for alarm '{alarm_name}'")

#     # Drop helper column
#     df.drop(columns=['DateTime'], inplace=True)

#     # ✅ Dynamic Date formatting
#     if 'Date' in df.columns:
#         def format_date(x):
#             if pd.isna(x) or str(x).strip() == '':
#                 return None
#             try:
#                 dt = pd.to_datetime(x, errors='coerce')
#                 return dt.strftime('%m/%d/%Y') if pd.notna(dt) else str(x)
#             except Exception:
#                 return str(x)
#         df['Date'] = df['Date'].apply(format_date)

#     # ✅ Dynamic Time formatting
#     if 'Time' in df.columns:
#         def format_time(x):
#             if pd.isna(x) or str(x).strip() == '':
#                 return None
#             try:
#                 dt = pd.to_datetime(x, errors='coerce')
#                 return dt.strftime('%I:%M:%S %p') if pd.notna(dt) else str(x)
#             except Exception:
#                 return str(x)
#         df['Time'] = df['Time'].apply(format_time)

#     # Save updated file
#     df.to_excel(output_file, index=False)

#     # Print summary log
#     print(f"✅ Updated file saved to {output_file}")
#     print(f"Total rows updated: {len(updates_log)}")
#     if updates_log:
#         print("\nDetails of updates:")
#         for log in updates_log:
#             print(log)
#     else:
#         print("No rows were updated.")

