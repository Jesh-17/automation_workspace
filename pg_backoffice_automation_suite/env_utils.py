import os
from dotenv import load_dotenv

class CustomEnvException(Exception):
    """Raised when Environment variables missing and its paths are incorrect"""
    pass

load_dotenv()  # Loads from .env (default)

def get_env_vars(mode="oi"):
    
    # Switch-case like logic to load the correct .env file
    if mode == "oi":
        file_name = os.getenv("ORDER_INPUT_FILE")
        output_location = os.getenv("ORDER_OUTPUT_LOCATION")
        user_data_dir = os.getenv("ORDER_CHROME_USER_DATA_DIR")
    elif mode == "bi":
        file_name = os.getenv("BATCH_INPUT_FILE")
        output_location = os.getenv("BATCH_OUTPUT_LOCATION")
        user_data_dir = os.getenv("BATCH_CHROME_USER_DATA_DIR")

    else:
        raise CustomEnvException("Invalid input type. Choose 'oi' or 'bi'.")

    
    # Fetch environment variables
    #file_name = os.getenv("INPUT_FILE")
    #output_location = os.getenv("OUTPUT_LOCATION")
    #user_data_dir = os.getenv("CHROME_USER_DATA_DIR")
    chrome_binary = os.getenv("CHROME_BINARY_LOCATION")

    # Validate environment variables
    if not file_name or not output_location or not user_data_dir or not chrome_binary:
        raise CustomEnvException("One or more environment variables are missing from the .env file")

    if not os.path.isfile(file_name):
        raise CustomEnvException(f"Input file path not found: {file_name}")
    if not os.path.isdir(user_data_dir):
        raise CustomEnvException(f"Chrome user data directory path not found: {user_data_dir}")
    if not os.path.isfile(chrome_binary):
        raise CustomEnvException(f"Chrome binary path not found: {chrome_binary}")

    return file_name, output_location, user_data_dir, chrome_binary

