
import pandas as pd
import os


def priorities_and_handledbyl2_filling():
    # File paths
    day_wise_file = "./required_files/day_wise_tiggered_alarms_list.xlsx"
    all_alarms_file = "./required_files/all_alarms_list.xlsx"

    output_file = f"./wsr/output/priorities_and_handledbyl2/priorities_and_handledbyl2_filled_in_this_day_wise_tiggered_alarms_list.xlsx"

    #Delete old output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Old file '{output_file}' deleted.")

    print("Processing priorities and HandledbyL2 columns...")

    # Load Excel files
    day_wise_df = pd.read_excel(day_wise_file)
    all_alarms_df = pd.read_excel(all_alarms_file)

    # Normalize column names
    day_wise_df.columns = day_wise_df.columns.str.strip()
    all_alarms_df.columns = all_alarms_df.columns.str.strip()

    # Replace empty strings with NaN
    day_wise_df[['Priority', 'HandledbyL2']] = day_wise_df[['Priority', 'HandledbyL2']].replace('', pd.NA)

    # ✅ Robust missing handling: catch spaces/'nan'/'None' as missing for both columns
    for col in ['Priority', 'HandledbyL2']:
        day_wise_df[col] = day_wise_df[col].astype('string').str.strip()
        day_wise_df[col] = day_wise_df[col].replace({'': pd.NA, 'nan': pd.NA, 'None': pd.NA})

    # Ensure target columns are object type
    day_wise_df['Priority'] = day_wise_df['Priority'].astype('string')
    day_wise_df['HandledbyL2'] = day_wise_df['HandledbyL2'].astype('string')

    # ✅ Preserve original AlarmDescription for output
    day_wise_df['OriginalAlarmDescription'] = day_wise_df['AlarmDescription']

    # ✅ Create normalized columns for matching
    day_wise_df['NormalizedAlarmDescription'] = day_wise_df['AlarmDescription'].apply(lambda x: str(x).split('|')[0].strip().lower())
    all_alarms_df['NormalizedAlarmDescription'] = all_alarms_df['AlarmDescription'].apply(lambda x: str(x).split('|')[0].strip().lower())

    # Create lookup dictionary using normalized names
    alarm_priority_map = dict(zip(all_alarms_df['NormalizedAlarmDescription'], all_alarms_df['Priority']))

    skipped_alarms = []

    # Iterate and update
    for idx, row in day_wise_df.iterrows():
        alarm_desc = row['NormalizedAlarmDescription']

        # Update if either Priority or HandledbyL2 is empty
        if pd.isna(row['Priority']) or pd.isna(row['HandledbyL2']):
            if alarm_desc in alarm_priority_map:
                if pd.isna(row['Priority']):
                    day_wise_df.at[idx, 'Priority'] = alarm_priority_map[alarm_desc]
                if pd.isna(row['HandledbyL2']):
                    day_wise_df.at[idx, 'HandledbyL2'] = "Yes"
            else:
                skipped_alarms.append(row['OriginalAlarmDescription'])  # Keep original name for skipped list

        # ✅ Fallback: if HandledbyL2 is missing but Priority is present (either originally or after fill), set it to "Yes"
        if pd.isna(day_wise_df.at[idx, 'HandledbyL2']) and pd.notna(day_wise_df.at[idx, 'Priority']):
            day_wise_df.at[idx, 'HandledbyL2'] = "Yes"

    # ✅ Dynamically handle Date column formatting
    if 'Date' in day_wise_df.columns:
        def format_date(x):
            if pd.isna(x) or str(x).strip() == '':
                return None
            try:
                dt = pd.to_datetime(x, errors='coerce')
                return dt.strftime('%m/%d/%Y') if pd.notna(dt) else str(x)
            except Exception:
                return str(x)  # Fallback: keep original if parsing fails

        day_wise_df['Date'] = day_wise_df['Date'].apply(format_date)

    # ✅ Dynamically handle Time column formatting (12h output by default per your original code)
    if 'Time' in day_wise_df.columns:
        def format_time(x):
            if pd.isna(x) or str(x).strip() == '':
                return None
            try:
                # Try parsing as datetime
                dt = pd.to_datetime(x, errors='coerce')
                return dt.strftime('%I:%M:%S %p') if pd.notna(dt) else str(x)
            except Exception:
                return str(x)  # Fallback: keep original if parsing fails

        day_wise_df['Time'] = day_wise_df['Time'].apply(format_time)

    # ✅ Restore original AlarmDescription before saving
    day_wise_df['AlarmDescription'] = day_wise_df['OriginalAlarmDescription']
    day_wise_df.drop(columns=['NormalizedAlarmDescription', 'OriginalAlarmDescription'], inplace=True)

    # Save updated file
    day_wise_df.to_excel(output_file, index=False)
    print(f"✅ Updated file saved as {output_file}")
    print(f"⚠ Skipped alarms (not found in all_alarms_list): {len(skipped_alarms)}")
    if skipped_alarms:
        print(skipped_alarms)




# import pandas as pd
# import os


# def priorities_and_handledbyl2_filling():
#     # File paths
#     day_wise_file = "./required_files/day_wise_tiggered_alarms_list.xlsx"
#     all_alarms_file = "./required_files/all_alarms_list.xlsx"

#     output_file = f"./wsr/output/priorities_and_handledbyl2_filled_in_this_day_wise_tiggered_alarms_list.xlsx"

#     #Delete old output file if it exists
#     if os.path.exists(output_file):
#         os.remove(output_file)
#         print(f"Old file '{output_file}' deleted.")

    
#     print("Processing priorities and HandledbyL2 columns...")

#     # Load Excel files
#     day_wise_df = pd.read_excel(day_wise_file)
#     all_alarms_df = pd.read_excel(all_alarms_file)

#     # Normalize column names
#     day_wise_df.columns = day_wise_df.columns.str.strip()
#     all_alarms_df.columns = all_alarms_df.columns.str.strip()

#     # Replace empty strings with NaN
#     day_wise_df[['Priority', 'HandledbyL2']] = day_wise_df[['Priority', 'HandledbyL2']].replace('', pd.NA)

#     # Ensure target columns are object type
#     day_wise_df['Priority'] = day_wise_df['Priority'].astype('string')
#     day_wise_df['HandledbyL2'] = day_wise_df['HandledbyL2'].astype('string')

#     # ✅ Preserve original AlarmDescription for output
#     day_wise_df['OriginalAlarmDescription'] = day_wise_df['AlarmDescription']

#     # ✅ Create normalized columns for matching
#     day_wise_df['NormalizedAlarmDescription'] = day_wise_df['AlarmDescription'].apply(lambda x: str(x).split('|')[0].strip().lower())
#     all_alarms_df['NormalizedAlarmDescription'] = all_alarms_df['AlarmDescription'].apply(lambda x: str(x).split('|')[0].strip().lower())

#     # Create lookup dictionary using normalized names
#     alarm_priority_map = dict(zip(all_alarms_df['NormalizedAlarmDescription'], all_alarms_df['Priority']))

#     skipped_alarms = []

#     # Iterate and update
#     for idx, row in day_wise_df.iterrows():
#         alarm_desc = row['NormalizedAlarmDescription']

#         # Update if either Priority or HandledbyL2 is empty
#         if pd.isna(row['Priority']) or pd.isna(row['HandledbyL2']):
#             if alarm_desc in alarm_priority_map:
#                 if pd.isna(row['Priority']):
#                     day_wise_df.at[idx, 'Priority'] = alarm_priority_map[alarm_desc]
#                 if pd.isna(row['HandledbyL2']):
#                     day_wise_df.at[idx, 'HandledbyL2'] = "Yes"
#             else:
#                 skipped_alarms.append(row['OriginalAlarmDescription'])  # Keep original name for skipped list

#     # ✅ Dynamically handle Date column formatting
#     if 'Date' in day_wise_df.columns:
#         def format_date(x):
#             if pd.isna(x) or str(x).strip() == '':
#                 return None
#             try:
#                 dt = pd.to_datetime(x, errors='coerce')
#                 return dt.strftime('%m/%d/%Y') if pd.notna(dt) else str(x)
#             except Exception:
#                 return str(x)  # Fallback: keep original if parsing fails

#         day_wise_df['Date'] = day_wise_df['Date'].apply(format_date)

#     # ✅ Dynamically handle Time column formatting
#     if 'Time' in day_wise_df.columns:
#         def format_time(x):
#             if pd.isna(x) or str(x).strip() == '':
#                 return None
#             try:
#                 # Try parsing as datetime
#                 dt = pd.to_datetime(x, errors='coerce')
#                 return dt.strftime('%I:%M:%S %p') if pd.notna(dt) else str(x)
#             except Exception:
#                 return str(x)  # Fallback: keep original if parsing fails

#         day_wise_df['Time'] = day_wise_df['Time'].apply(format_time)

#     # ✅ Restore original AlarmDescription before saving
#     day_wise_df['AlarmDescription'] = day_wise_df['OriginalAlarmDescription']
#     day_wise_df.drop(columns=['NormalizedAlarmDescription', 'OriginalAlarmDescription'], inplace=True)

#     # Save updated file
#     day_wise_df.to_excel(output_file, index=False)
#     print(f"✅ Updated file saved as {output_file}")
#     print(f"⚠ Skipped alarms (not found in all_alarms_list): {len(skipped_alarms)}")
#     if skipped_alarms:
#         print(skipped_alarms)

