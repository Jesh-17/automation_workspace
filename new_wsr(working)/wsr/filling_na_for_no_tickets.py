
import pandas as pd
import os
from datetime import datetime
import glob

def filling_na_for_no_tickets():
    # File paths
    input_file = "./wsr/output/parent_filling_using_previous_week_alarm_sheet/parent_filling_using_previous_week_alarm_sheet_in_this_day_wise_tiggered_alarms_list.xlsx"

    # Add date and time to output file name
    timestamp = datetime.now().strftime("%H%M%S(%d-%m-%Y)")
    output_file = f"./wsr/output/final_result/filled_na_for_no_tickets_in_this_day_wise_tiggered_alarms_list_{timestamp}.xlsx"

    # Delete all old timestamped output files
    for old_file in glob.glob("./wsr/output/final_result/filled_na_for_no_tickets_in_this_day_wise_tiggered_alarms_list_*.xlsx"):
        try:
            os.remove(old_file)
            print(f"Deleted old file: {old_file}")
        except Exception as e:
            print(f"Could not delete {old_file}: {e}")

    print("Processing EscalatedtoL3/AppSupportteam, Ticketnumber, and Status columns...")

    # Load Excel file
    alarms_df = pd.read_excel(input_file, engine="openpyxl")

    # ✅ Normalize column names
    alarms_df.columns = alarms_df.columns.str.strip()

    # ✅ Ensure target columns exist
    cols_to_fill = ['EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status']
    for col in cols_to_fill:
        if col not in alarms_df.columns:
            alarms_df[col] = pd.NA  # create missing columns as empty

    # ✅ Robust empty normalization: treat NaN, '', whitespace, 'nan', 'none', 'null', 'n/a', 'na', '-' as empty
    def normalize_empty(val):
        if pd.isna(val):
            return pd.NA
        if isinstance(val, str):
            s = val.strip()
            if s == "" or s.lower() in {"nan", "none", "null", "n/a", "na", "-"}:
                return pd.NA
            return s  # preserve actual text
        return val

    alarms_df[cols_to_fill] = alarms_df[cols_to_fill].map(normalize_empty).astype("object")

    # ✅ Build mask: fill ONLY rows where all three columns are empty
    mask_all_empty = alarms_df[cols_to_fill].isna().all(axis=1)

    # For visibility before filling
    total_rows = len(alarms_df)
    empty_rows_count = int(mask_all_empty.sum())
    print(f"Total rows: {total_rows}, rows with all 3 columns empty: {empty_rows_count}")

    # ✅ Vectorized fill for all-NA rows
    alarms_df.loc[mask_all_empty, 'EscalatedtoL3/AppSupportteam'] = "Acknowledged by L2 Team"
    alarms_df.loc[mask_all_empty, 'Ticketnumber'] = "N/A"
    alarms_df.loc[mask_all_empty, 'Status'] = "Closed"

    # ✅ Optional: If you want to avoid overwriting partially filled rows,
    # we already only fill rows where ALL three are empty.

    # ✅ Dynamic Date formatting (write blanks as None)
    if 'Date' in alarms_df.columns:
        def format_date(x):
            # Keep blanks as None for Excel
            if pd.isna(x) or str(x).strip() == '':
                return None
            dt = pd.to_datetime(x, errors='coerce')
            return dt.strftime('%m/%d/%Y') if pd.notna(dt) else x
        alarms_df['Date'] = alarms_df['Date'].apply(format_date)

    # ✅ Dynamic Time formatting (write blanks as None)
    if 'Time' in alarms_df.columns:
        def format_time(x):
            if pd.isna(x) or str(x).strip() == '':
                return None
            dt = pd.to_datetime(x, errors='coerce')
            return dt.strftime('%I:%M:%S %p') if pd.notna(dt) else x
        alarms_df['Time'] = alarms_df['Time'].apply(format_time)

    # Save updated file
    alarms_df.to_excel(output_file, index=False, engine="openpyxl")
    print(f"✅ Updated file saved as {output_file}")




# import pandas as pd
# import os
# from datetime import datetime
# import glob

# def filling_na_for_no_tickets():
#     # File paths
#     input_file = "./wsr/output/parent_filling_using_previous_week_alarm_sheet_in_this_day_wise_tiggered_alarms_list.xlsx"


#     #Add date and time to output file name
#     timestamp = datetime.now().strftime("%H%M%S(%d-%m-%Y)")
#     output_file = f"./wsr/output/final_result/filled_na_for_no_tickets_in_this_day_wise_tiggered_alarms_list_{timestamp}.xlsx"

#     # Delete all old timestamped output files
#     for old_file in glob.glob("./wsr/output/final_result/filled_na_for_no_tickets_in_this_day_wise_tiggered_alarms_list_*.xlsx"):
#         os.remove(old_file)
#         print(f"Deleted old file: {old_file}")


#     # #Delete old output file if it exists.  But while using this it is skiping some rows from input file
#     # output_file = f"./wsr/output/final_result/filled_na_for_no_tickets_in_this_day_wise_tiggered_alarms_list.xlsx"

#     # if os.path.exists(output_file):
#     #     os.remove(output_file)
#     #     print(f"Old file '{output_file}' deleted.")


#     print("Processing EscalatedtoL3/AppSupportteam, Ticketnumber, and Status columns...")

#     # Load Excel file
#     alarms_df = pd.read_excel(input_file)

#     # ✅ Normalize column names
#     alarms_df.columns = alarms_df.columns.str.strip()

#     # ✅ Ensure target columns exist and normalize empty values
#     cols_to_fill = ['EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status']
#     alarms_df[cols_to_fill] = alarms_df[cols_to_fill].astype('object').replace('', pd.NA)

#     # ✅ Fill only rows where all three columns are empty
#     for idx, row in alarms_df.iterrows():
#         if all(pd.isna(row[col]) for col in cols_to_fill):
#             alarms_df.at[idx, 'EscalatedtoL3/AppSupportteam'] = "Acknowledged by L2 Team"
#             alarms_df.at[idx, 'Ticketnumber'] = "N/A"
#             alarms_df.at[idx, 'Status'] = "Closed"

#     # ✅ Dynamic Date formatting
#     if 'Date' in alarms_df.columns:
#         def format_date(x):
#             if pd.isna(x) or str(x).strip() == '':
#                 return None
#             try:
#                 dt = pd.to_datetime(x, errors='coerce')
#                 return dt.strftime('%m/%d/%Y') if pd.notna(dt) else str(x)
#             except Exception:
#                 return str(x)
#         alarms_df['Date'] = alarms_df['Date'].apply(format_date)

#     # ✅ Dynamic Time formatting
#     if 'Time' in alarms_df.columns:
#         def format_time(x):
#             if pd.isna(x) or str(x).strip() == '':
#                 return None
#             try:
#                 dt = pd.to_datetime(x, errors='coerce')
#                 return dt.strftime('%I:%M:%S %p') if pd.notna(dt) else str(x)
#             except Exception:
#                 return str(x)
#         alarms_df['Time'] = alarms_df['Time'].apply(format_time)

    
#     # Save updated file
#     alarms_df.to_excel(output_file, index=False)
#     print(f"✅ Updated file saved as {output_file}")





# import pandas as pd
# import os
# from datetime import datetime
# import glob

# def filling_na_for_no_tickets():
#     # Input and output file names
#     input_file = "./wsr/output/parent_filling_using_previous_week_alarm_sheet_in_this_day_wise_tiggered_alarms_list.xlsx"
    
#     # Add date and time to output file name
#     timestamp = datetime.now().strftime("%H%M%S(%d-%m-%Y)")
#     output_file = f"updated_alarm_sheet_{timestamp}.xlsx"

#     # Delete all old timestamped output files
#     for old_file in glob.glob("updated_alarm_sheet_*.xlsx"):
#         os.remove(old_file)
#         print(f"Deleted old file: {old_file}")

#     # Read the Excel file
#     df = pd.read_excel(input_file)

#     # Check rows where all three columns are empty
#     mask = df[['EscalatedtoL3/AppSupportteam', 'Ticketnumber', 'Status']].isna().all(axis=1)

#     # Fill values for those rows
#     df.loc[mask, 'EscalatedtoL3/AppSupportteam'] = "Acknowledged by L2 Team"
#     df.loc[mask, 'Ticketnumber'] = "N/A"
#     df.loc[mask, 'Status'] = "Closed"

#     # Save the updated DataFrame to a new Excel file with timestamp
#     df.to_excel(output_file, index=False)
#     print(f"File saved as {output_file}")
