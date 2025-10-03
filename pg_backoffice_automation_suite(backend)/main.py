from env_utils import *
#from chrome_utils import *
from read_input_csv import *
from run_backoffice_automation import *
from run_backoffice_automation_batch import *
from merge_csv_files import *


# from env_utils import get_env_vars, CustomEnvException
# from chrome_utils import is_chrome_running, ChromeRunningException
# from read_input_csv import read_input_csv, CSVReadException
# from run_backoffice_automation import run_backoffice_automation, WebDriverAutomationException
# from merge_csv_files import CSVMergeException


def main():
    try:

        # First Check if Chrome is running 
        # is_chrome_running()
        
        print("--------------------------------------------------------------------------------")
        # Ask the user
        print("\033[33m--Below 'oi' means order-input and 'bi' means batch-input--\033[0m")
        mode= input("\033[33mEnter input type (oi/bi): \033[0m").strip().lower()
        file_name, output_location, user_data_dir, chrome_binary= get_env_vars(mode)
        print("\033[32m\t### Environment variables loaded successfully ###\t\033[0m")
        print(f"INPUT_FILE: {file_name}")
        print(f"OUTPUT_LOCATION: {output_location}")

        print(f"CHROME_USER_DATA_DIR: {user_data_dir}")
        print(f"CHROME_BINARY_LOCATION: {chrome_binary}")
        print("--------------------------------------------------------------------------------")

        print("\033[32m\t### CSV input information loaded successfully ###\t\033[0m")
        header, ids = read_input_csv(file_name, mode)
        print(f"CSV header used: {header}")
        print(f"Extracted IDs: {ids}")

        print("--------------------------------------------------------------------------------")

        # Run the appropriate automation based on mode
        if mode == "oi":
            run_backoffice_automation(file_name, output_location, user_data_dir, chrome_binary, mode)
        elif mode == "bi":
            run_backoffice_automation_batch(file_name, output_location, user_data_dir, chrome_binary, mode)
        
        print("--------------------------------------------------------------------------------")

    
    # except ChromeRunningException as e:
    #     print(f"Chrome check failed: \033[31m{e}\033[0m")
    except CustomEnvException as e:
        print(f"Environment validation failed: \033[31m{e}\033[0m")

    except WebDriverAutomationException as e:
        print(f"WebDriver automation failed: \033[31m{e}\033[0m")

    except CSVReadException as e:
        print(f"CSV read failed: \033[31m{e}\033[0m")
    except CSVMergeException as e:
        print(f"CSV merge failed: \033[31m{e}\033[0m")

    except Exception as e:
        print(f"Unexpected error: \033[31m{e}\033[0m")


if __name__ == "__main__":
    main()
