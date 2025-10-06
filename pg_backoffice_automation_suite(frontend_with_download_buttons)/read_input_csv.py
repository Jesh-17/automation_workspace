import pandas as pd

class CSVReadException(Exception):
    """Raised when the input CSV file cannot be processed correctly."""
    pass

def read_input_csv(file_name, mode="oi"):
    try:
        df = pd.read_csv(file_name)
        df.columns = [col.strip() for col in df.columns]  # Clean column names
        columns_lower = [col.lower() for col in df.columns]

        if mode == "oi":
            if "orderid" in columns_lower:
                header = df.columns[columns_lower.index("orderid")]
            elif "transactionid" in columns_lower:
                header = df.columns[columns_lower.index("transactionid")]
            else:
                raise CSVReadException(
                    "CSV must contain either 'orderId' or 'transactionId' for order-input(oi) mode."
                )
        elif mode == "bi":
            if "batchid" in columns_lower:
                header = df.columns[columns_lower.index("batchid")]
            else:
                raise CSVReadException(
                    "CSV must contain 'batchId' for batch-input(bi) mode."
                )
        else:
            raise CSVReadException("Invalid mode. Use 'oi' or 'bi'.")

        df = df.drop_duplicates(subset=[header])
        numpy_array = df[header].dropna().astype(str).to_numpy()
        return header, numpy_array.tolist()

    except Exception as e:
        raise CSVReadException(f"Error reading CSV file: {e}")
