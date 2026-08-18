
import pandas as pd
import os
import re

def actual_alarm_dump():
    # Input file paths
    alarm_dump_path = './required_files/alarm_dump.xlsx'
    all_alarms_path = './required_files/all_alarms_list.xlsx'
    output_path = './dump_refinement/output/actual_alarm_dump.xlsx'
    skipped_output_path = './dump_refinement/output/skipped_alarms.xlsx'


    # Delete old output files if they exist
    for file_path in [output_path, skipped_output_path]:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Old file '{file_path}' deleted.")
        else:
            print(f"No old file found at '{file_path}'.")

    # Read input Excel files
    alarm_df = pd.read_excel(alarm_dump_path, engine='openpyxl')
    all_alarms_df = pd.read_excel(all_alarms_path, engine='openpyxl')

    # Focus on required columns
    alarm_df = alarm_df[['Subject', 'DateTimeReceived']]

    
    # Improved cleaning function
    def clean_subject(subject):
        if pd.isna(subject):
            return ''
        subject = subject.strip()
        # Remove ALARM: and optional quotes
        subject = re.sub(r'^ALARM:\s*\"?', '', subject)
        # Remove everything after the first dot
        subject = re.sub(r'\..*$', '', subject)
        # Remove region info like 'in US East (N. Virginia)' if present
        subject = re.sub(r'in\s+[A-Za-z\s\(\)\.]+$', '', subject)
        # Remove trailing quotes and spaces
        subject = subject.replace('"', '').strip()
        return subject

    alarm_df['CleanSubject'] = alarm_df['Subject'].apply(clean_subject)

    # Prepare AlarmDescription list
    all_alarms_df['AlarmDescription'] = all_alarms_df['AlarmDescription'].astype(str).str.strip()

    # Lists for skipped alarms
    skipped_rows = []
    multiple_matches_details = []

    # Function to find full alarm name and priority
    def find_alarm_details(clean_subject, original_subject, sno):
        if not clean_subject:
            skipped_rows.append({'S.No': sno, 'OriginalSubject': original_subject, 'CleanedSubject': clean_subject, 'Reason': 'Empty after cleaning'})
            return '', ''
        
        matches = all_alarms_df[all_alarms_df['AlarmDescription'].str.contains(clean_subject, case=False, na=False, regex=False)]
        
        if len(matches) == 1:
            return matches.iloc[0]['AlarmDescription'], matches.iloc[0]['Priority']
        elif len(matches) > 1:
            unique_alarms = matches['AlarmDescription'].unique()
            if len(unique_alarms) == 1:
                return unique_alarms[0], matches.iloc[0]['Priority']
            else:
                skipped_rows.append({'S.No': sno, 'OriginalSubject': original_subject, 'CleanedSubject': clean_subject, 'Reason': 'Multiple different matches for this alarm in `all_alarms_list.xlsx`'})
                # Add each possible match as a separate row
                for match in unique_alarms:
                    multiple_matches_details.append({
                        'S.No': sno,
                        'CleanedSubject': clean_subject,
                        'PossibleMatch': match
                    })
                # Add an empty row for clarity
                multiple_matches_details.append({'S.No': '', 'CleanedSubject': '', 'PossibleMatch': ''})
                return '', ''
        else:
            skipped_rows.append({'S.No': sno, 'OriginalSubject': original_subject, 'CleanedSubject': clean_subject, 'Reason': 'No match found'})
            return '', ''

    # Apply matching logic with S.No tracking
    alarm_df[['AlarmDescription', 'Priority']] = alarm_df.apply(
        lambda row: pd.Series(find_alarm_details(row['CleanSubject'], row['Subject'], row.name + 1)), axis=1
    )

    # Convert DateTimeReceived to datetime
    alarm_df['DateTimeReceived'] = pd.to_datetime(alarm_df['DateTimeReceived'], errors='coerce')
    alarm_df['Date'] = alarm_df['DateTimeReceived']
    alarm_df['Time'] = alarm_df['DateTimeReceived']

    # ✅ Dynamic Date formatting (cross-platform)
    def format_date(x):
        if pd.isna(x) or str(x).strip() == '':
            return None
        try:
            dt = pd.to_datetime(x, errors='coerce')
            if pd.notna(dt):
                return f"{dt.month}/{dt.day}/{dt.year}"  # No leading zeros
            else:
                return str(x)
        except Exception:
            return str(x)

    # ✅ Dynamic Time formatting (cross-platform)
    def format_time(x):
        if pd.isna(x) or str(x).strip() == '':
            return None
        try:
            dt = pd.to_datetime(x, errors='coerce')
            if pd.notna(dt):
                hour = dt.hour % 12 or 12
                am_pm = "AM" if dt.hour < 12 else "PM"
                return f"{hour}:{dt.minute:02}:{dt.second:02} {am_pm}"
            else:
                return str(x)
        except Exception:
            return str(x)

    alarm_df['Date'] = alarm_df['Date'].apply(format_date)
    alarm_df['Time'] = alarm_df['Time'].apply(format_time)

    # Create final DataFrame
    final_df = pd.DataFrame({
        'S.No': range(1, len(alarm_df) + 1),
        'Date': alarm_df['Date'],
        'Time': alarm_df['Time'],
        'AlarmDescription': alarm_df['AlarmDescription'],
        'Priority': alarm_df['Priority'],
        'HandledbyL2': '',
        'EscalatedtoL3/AppSupportteam': '',
        'Ticketnumber': '',
        'Status': ''
    })

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write main output file
    final_df.to_excel(output_path, index=False, engine='openpyxl')

    # Write skipped alarms log with two sheets
    if skipped_rows:
        with pd.ExcelWriter(skipped_output_path, engine='openpyxl') as writer:
            pd.DataFrame(skipped_rows).to_excel(writer, sheet_name='Skipped_Alarms', index=False)
            if multiple_matches_details:
                pd.DataFrame(multiple_matches_details).to_excel(writer, sheet_name='all_Multiple_Matches', index=False)
        print(f"Skipped alarms logged in {skipped_output_path}")

    print(f"File successfully created at {output_path} with {len(final_df)} rows.")
















































# import pandas as pd
# import os
# import re

# def actual_alarm_dump():
#     # Input file paths
#     alarm_dump_path = './dump_required_files/alarm_dump.xlsx'
#     all_alarms_path = './required_files/all_alarms_list.xlsx'
#     output_path = './dump/actual_alarm_dump.xlsx'
#     skipped_output_path = './dump/skipped_alarms.xlsx'

#     # Read input Excel files
#     alarm_df = pd.read_excel(alarm_dump_path, engine='openpyxl')
#     all_alarms_df = pd.read_excel(all_alarms_path, engine='openpyxl')

#     # Focus on required columns
#     alarm_df = alarm_df[['Subject', 'DateTimeReceived']]

#     # Improved cleaning function
#     def clean_subject(subject):
#         if pd.isna(subject):
#             return ''
#         subject = subject.strip()
#         subject = re.sub(r'^ALARM:\s*\"?', '', subject)
#         subject = re.sub(r'\.\.\..*$', '', subject)
#         subject = re.sub(r'in\s+[A-Za-z\s\(\)\.]+$', '', subject)
#         subject = subject.replace('"', '').strip()
#         return subject

#     alarm_df['CleanSubject'] = alarm_df['Subject'].apply(clean_subject)

#     # Prepare AlarmDescription list
#     all_alarms_df['AlarmDescription'] = all_alarms_df['AlarmDescription'].astype(str).str.strip()

#     # Lists for skipped alarms
#     skipped_rows = []

#     # Function to find full alarm name and priority
#     def find_alarm_details(clean_subject, original_subject):
#         if not clean_subject:
#             skipped_rows.append({'OriginalSubject': original_subject, 'CleanedSubject': clean_subject, 'Reason': 'Empty after cleaning'})
#             return '', ''
        
#         matches = all_alarms_df[all_alarms_df['AlarmDescription'].str.contains(clean_subject, case=False, na=False, regex=False)]
        
#         if len(matches) == 1:
#             return matches.iloc[0]['AlarmDescription'], matches.iloc[0]['Priority']
#         elif len(matches) > 1:
#             unique_alarms = matches['AlarmDescription'].unique()
#             if len(unique_alarms) == 1:
#                 return unique_alarms[0], matches.iloc[0]['Priority']
#             else:
#                 skipped_rows.append({'OriginalSubject': original_subject, 'CleanedSubject': clean_subject, 'Reason': 'Multiple different matches in `all_alarms_list.xlsx`'})
#                 return '', ''
#         else:
#             skipped_rows.append({'OriginalSubject': original_subject, 'CleanedSubject': clean_subject, 'Reason': 'No match found'})
#             return '', ''

#     alarm_df[['AlarmDescription', 'Priority']] = alarm_df.apply(
#         lambda row: pd.Series(find_alarm_details(row['CleanSubject'], row['Subject'])), axis=1
#     )

#     # Convert DateTimeReceived to datetime
#     alarm_df['DateTimeReceived'] = pd.to_datetime(alarm_df['DateTimeReceived'], errors='coerce')
#     alarm_df['Date'] = alarm_df['DateTimeReceived']
#     alarm_df['Time'] = alarm_df['DateTimeReceived']

#     # ✅ Dynamic Date formatting (cross-platform)
#     def format_date(x):
#         if pd.isna(x) or str(x).strip() == '':
#             return None
#         try:
#             dt = pd.to_datetime(x, errors='coerce')
#             if pd.notna(dt):
#                 # Use custom formatting for Windows compatibility
#                 return f"{dt.month}/{dt.day}/{dt.year}"
#             else:
#                 return str(x)
#         except Exception:
#             return str(x)

#     # ✅ Dynamic Time formatting (cross-platform)
#     def format_time(x):
#         if pd.isna(x) or str(x).strip() == '':
#             return None
#         try:
#             dt = pd.to_datetime(x, errors='coerce')
#             if pd.notna(dt):
#                 hour = dt.hour % 12 or 12
#                 am_pm = "AM" if dt.hour < 12 else "PM"
#                 return f"{hour}:{dt.minute:02}:{dt.second:02} {am_pm}"
#             else:
#                 return str(x)
#         except Exception:
#             return str(x)

#     alarm_df['Date'] = alarm_df['Date'].apply(format_date)
#     alarm_df['Time'] = alarm_df['Time'].apply(format_time)

#     # Create final DataFrame
#     final_df = pd.DataFrame({
#         'S.No': range(1, len(alarm_df) + 1),
#         'Date': alarm_df['Date'],
#         'Time': alarm_df['Time'],
#         'AlarmDescription': alarm_df['AlarmDescription'],
#         'Priority': alarm_df['Priority'],
#         'HandledbyL2': '',
#         'EscalatedtoL3/AppSupportteam': '',
#         'Ticketnumber': '',
#         'Status': ''
#     })

#     # Ensure output directory exists
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)

#     # Write main output file
#     final_df.to_excel(output_path, index=False, engine='openpyxl')

#     # Write skipped alarms log
#     if skipped_rows:
#         skipped_df = pd.DataFrame(skipped_rows)
#         skipped_df.to_excel(skipped_output_path, index=False, engine='openpyxl')
#         print(f"Skipped alarms logged in {skipped_output_path}")

#     print(f"File successfully created at {output_path} with {len(final_df)} rows.")





















































































































































































































