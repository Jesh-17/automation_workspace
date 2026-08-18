import pandas as pd
import warnings
import os


def child_or_parent_corresponding_date():
    # Suppress pandas UserWarnings for time parsing
    warnings.filterwarnings("ignore", category=UserWarning)

    # File paths
    ticket_tracker_file = "./required_files/day_wise_ticket_tracker_list.xlsx"

    triggered_alarms_file = "./wsr/output/priorities_and_handledbyl2/priorities_and_handledbyl2_filled_in_this_day_wise_tiggered_alarms_list.xlsx"

    output_file = f"./wsr/output/child_or_parent_corresponding_date/child_or_parent_corresponding_date_filled_in_this_day_wise_tiggered_alarms_list.xlsx"


    #Delete old output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Old file '{output_file}' deleted.")


    print("Processing tickets...")

    # Load Excel files
    tracker_df = pd.read_excel(ticket_tracker_file)
    alarms_df = pd.read_excel(triggered_alarms_file)

    # Normalize column names
    tracker_df.columns = tracker_df.columns.str.strip()
    alarms_df.columns = alarms_df.columns.str.strip()

    # ✅ Ensure target columns are string type to avoid dtype warnings
    for col in ['Ticketnumber', 'EscalatedtoL3/AppSupportteam', 'Status']:
        alarms_df[col] = alarms_df[col].astype('string')

    # ✅ Preserve original AlarmDescription for output
    alarms_df['OriginalAlarmDescription'] = alarms_df['AlarmDescription']

    # ✅ Create normalized columns for matching
    tracker_df['NormalizedAlarmDescription'] = tracker_df['AlarmDescription'].apply(lambda x: str(x).split('|')[0].strip().lower())
    alarms_df['NormalizedAlarmDescription'] = alarms_df['AlarmDescription'].apply(lambda x: str(x).split('|')[0].strip().lower())

    # Normalize team/status
    tracker_df['Ticket Assigned To'] = tracker_df['Ticket Assigned To'].str.strip().str.lower()
    tracker_df['Ticket Status'] = tracker_df['Ticket Status'].str.strip().str.lower()

    # ✅ Extract date from Ticket Assigned Date/Time
    tracker_df['Date'] = pd.to_datetime(tracker_df['Ticket Assigned Date/Time']).dt.date
    alarms_df['Date'] = pd.to_datetime(alarms_df['Date']).dt.date

    # Counters for logging
    child_updates = 0
    parent_updates = 0

    # ✅ Iterate through alarms and apply logic
    for idx, alarm_row in alarms_df.iterrows():
        alarm_date = alarm_row['Date']
        alarm_desc = alarm_row['NormalizedAlarmDescription']

        # ✅ Update only if all three columns are empty or blank
        if all(pd.isna(alarm_row[col]) or str(alarm_row[col]).strip() == '' for col in ['Ticketnumber', 'EscalatedtoL3/AppSupportteam', 'Status']):
            # Filter tracker rows for same date and alarm
            same_date_rows = tracker_df[(tracker_df['Date'] == alarm_date) &
                                        (tracker_df['NormalizedAlarmDescription'] == alarm_desc)]

            # ✅ Check for child (L2 Team, Closed)
            child = same_date_rows[(same_date_rows['Ticket Assigned To'] == 'l2 team') &
                                   (same_date_rows['Ticket Status'] == 'closed')]

            if not child.empty:
                alarms_df.at[idx, 'Ticketnumber'] = str(child.iloc[0]['JIRA Ticket No.'])
                alarms_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = 'Acknowledged by L2 Team'
                alarms_df.at[idx, 'Status'] = 'Closed'
                child_updates += 1
                continue

            # ✅ If child does not exist, check parents (AppSupport or L3)
            parents = same_date_rows[
                ((same_date_rows['Ticket Assigned To'] == 'appsupport team') |
                 (same_date_rows['Ticket Assigned To'] == 'l3 team')) &
                (same_date_rows['Ticket Status'] == 'pending')
            ]

            if not parents.empty:
                # Sort by Ticket Assigned Date/Time to get latest parent
                parents_sorted = parents.sort_values(by='Ticket Assigned Date/Time', ascending=False)
                latest_parent = parents_sorted.iloc[0]

                alarms_df.at[idx, 'Ticketnumber'] = str(latest_parent['JIRA Ticket No.'])

                if latest_parent['Ticket Assigned To'] == 'appsupport team':
                    alarms_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = 'Escalated to AppSupport team'
                    alarms_df.at[idx, 'Status'] = 'Pending with AppSupport team'
                else:
                    alarms_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = 'Escalated to L3 team'
                    alarms_df.at[idx, 'Status'] = 'Pending with L3 team'

                parent_updates += 1

    # ✅ Dynamic Date formatting
    if 'Date' in alarms_df.columns:
        def format_date(x):
            if pd.isna(x) or str(x).strip() == '':
                return None
            try:
                dt = pd.to_datetime(x, errors='coerce')
                return dt.strftime('%m/%d/%Y') if pd.notna(dt) else str(x)
            except Exception:
                return str(x)
        alarms_df['Date'] = alarms_df['Date'].apply(format_date)


    # ✅ Dynamic Time formatting
    if 'Time' in alarms_df.columns:
        def format_time(x):
            if pd.isna(x) or str(x).strip() == '':
                return None
            try:
                dt = pd.to_datetime(x, errors='coerce')
                return dt.strftime('%I:%M:%S %p') if pd.notna(dt) else str(x)
            except Exception:
                return str(x)
        alarms_df['Time'] = alarms_df['Time'].apply(format_time)

    # ✅ Replace normalized AlarmDescription with original before saving
    alarms_df['AlarmDescription'] = alarms_df['OriginalAlarmDescription']
    alarms_df.drop(columns=['NormalizedAlarmDescription', 'OriginalAlarmDescription'], inplace=True)

    # ✅ Save updated alarms file
    alarms_df.to_excel(output_file, index=False)

    # ✅ Print summary
    print(f"✅ Updated file saved as {output_file}")
    print(f"Summary: {child_updates} rows updated as Child, {parent_updates} rows updated as Parent.")

