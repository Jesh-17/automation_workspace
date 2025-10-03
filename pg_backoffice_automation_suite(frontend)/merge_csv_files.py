import os
import glob
import pandas as pd
from datetime import datetime

class CSVMergeException(Exception):
    """Raised when CSV merging fails due to missing folder, files, or invalid data."""
    pass

def merge_csv_files(base_folder):
    # Ensure base_folder exists
    if not os.path.exists(base_folder):
        raise CSVMergeException(f"Base folder does not exist: {base_folder}")

    # Create merge-output-data folder if it doesn't exist
    merge_folder = os.path.join(base_folder, "merge-output-data")
    os.makedirs(merge_folder, exist_ok=True)

    # Find all CSV files in the base folder
    csv_files = glob.glob(os.path.join(base_folder, "*.csv"))
    if not csv_files:
        raise CSVMergeException("No CSV files found to merge.")

    # Read all CSVs and concatenate them
    df_list = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            df_list.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    if not df_list:
        raise CSVMergeException("No valid CSV data found to merge.")

    merged_df = pd.concat(df_list, ignore_index=True)

    # Save the merged CSV
    merged_file_name = f"merged_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    merged_file_path = os.path.join(merge_folder, merged_file_name)

    # Extra safeguard for deep paths: ensure folder exists
    os.makedirs(os.path.dirname(merged_file_path), exist_ok=True)

    merged_df.to_csv(merged_file_path, index=False)
    print(f"Order Input (oi) IDs are merged successfully into the path = {merged_file_path}")
