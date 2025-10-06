import os
import time
from dotenv import load_dotenv

class CustomEnvException(Exception):
    """Raised when Environment variables missing and its paths are incorrect"""
    pass


# Detect OS and load appropriate .env file
env_file_map = {
    "nt": ".env.windows",
    "posix": ".env.linux"
}

env_file = env_file_map.get(os.name)

if not env_file:
    raise CustomEnvException(f"Unsupported OS: {os.name}. No matching .env file.")


load_dotenv(env_file)

def get_env_vars(mode="oi"):
    if mode == "oi":
        output_location = os.getenv("ORDER_OUTPUT_LOCATION")
        user_data_dir = os.getenv("ORDER_CHROME_USER_DATA_DIR")
    elif mode == "bi":
        output_location = os.getenv("BATCH_OUTPUT_LOCATION")
        user_data_dir = os.getenv("BATCH_CHROME_USER_DATA_DIR")
    else:
        raise CustomEnvException("Invalid input type. Choose 'oi' or 'bi'.")

    chrome_binary = os.getenv("CHROME_BINARY_LOCATION")


    if not chrome_binary:
        possible_paths = {  # Windows
            "nt": [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            ],
            "posix": [      # Linux/macOS
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/snap/bin/chromium",
                "/usr/bin/chromium",
                "/usr/bin/chrome",
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            ]
        }.get(os.name, [])

        for path in possible_paths:
            if os.path.isfile(path):
                chrome_binary = path
                break


    # Validate environment variables
    if not output_location or not user_data_dir:
        raise CustomEnvException("One or more environment variables are missing from the .env file or could not be auto-detected.")
    
    # Create user_data_dir if it doesn't exist, It must created before running automation
    if not os.path.isdir(user_data_dir):
        os.makedirs(user_data_dir)
        time.sleep(1)  # Let the OS register the new folder

    # Create output_location if it doesn't exist
    if not os.path.isdir(output_location):
        os.makedirs(output_location)
        time.sleep(1) 
    
    if not os.path.isfile(chrome_binary):
        raise CustomEnvException(f"Chrome binary path not found: {chrome_binary}")

    return output_location, user_data_dir, chrome_binary


