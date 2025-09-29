import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from tqdm import tqdm

from read_input_csv import CSVReadException, read_input_csv
from merge_csv_files import CSVMergeException, merge_csv_files

class WebDriverAutomationException(Exception):
    """Raised when WebDriver automation fails."""
    pass


def run_backoffice_automation(file_name, output_location, user_data_dir, chrome_binary, mode):
    try:

        # Create folder
        timestamp = datetime.now().strftime("%d-%m-%Y-(At-time-%H-%M-%S)")
        folder_name = f"Backoffice-orderids-data-{timestamp}"
        output_location = os.path.join(os.path.abspath(output_location), folder_name)

        os.makedirs(output_location, exist_ok=True)
        
        # Setup Chrome options
        options = webdriver.ChromeOptions()
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": output_location,
                "download.prompt_for_download": False,
                "safebrowsing.enabled": False,
            },
        )
        options.add_argument(f"user-data-dir={user_data_dir}")
        options.binary_location = chrome_binary
        options.add_argument("--log-level=3")

        driver = None

        try:
            driver = webdriver.Chrome(options=options)
            driver.get("https://pagos-backoffice.tigocloud.net/reports")
            input("\033[33mPlease (log in manually / if already logged in, just press 'Enter')..\033[0m")

            try:
                id_type, id_numbers = read_input_csv(file_name, mode)
                print(f"Loaded {len(id_numbers)} IDs from CSV using ID type: {id_type}")
            except Exception as e:
                raise CSVReadException(f"Failed to read input CSV: \033[31m{e}\033[0m")

            processed_ids = []
            progress_bar = tqdm(id_numbers, desc="Processing IDs", unit=" ID")

            for id_number in progress_bar:
                try:
                    input_field = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "orderId"))
                    )
                    input_field.clear()
                    input_field.send_keys(id_number)
                    time.sleep(2)
                    input_field.send_keys(Keys.RETURN)
                    time.sleep(3)

                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Export CSV')]"))
                    )
                    export_button = driver.find_element(By.XPATH, "//button[contains(.,'Export CSV')]")
                    export_button.click()
                    time.sleep(5)

                    progress_bar.write(f"Processed ID: {id_number}")
                    processed_ids.append(id_number)

                except (TimeoutException, NoSuchElementException):
                    #progress_bar.write(f"\033[31mInvalid or unresponsive ID at: {id_number}. So stopped further processing IDs....\033[0m")
                    progress_bar.write(f"\033[31m(--May be login issue, so stopped at initial ID: {id_number}--) or (--Invalid ID at: {id_number}, so stopped further processing IDs....--)\033[0m")
                    break

                except Exception as inner_e:
                    progress_bar.write(f"Unexpected error with ID {id_number}: {inner_e}")
                    break

            progress_bar.close()

            if processed_ids:
                print("\n\033[32mSuccessfully processed IDs:\033[0m")
                for pid in processed_ids:
                    print(f" - {pid}")
            else:
                print("\nNo IDs were successfully processed.")           

        except Exception as e:
            raise WebDriverAutomationException(f"Web driver error: \033[31m{e}\033[0m")

        finally:
            try:
                merge_csv_files(output_location)
                print("Merging process completed...")
                print("Automation completed...")
            except CSVMergeException as e:
                print(f"CSV merge failed: \033[31m{e}\033[0m")
            if driver:
                driver.quit()
                print("Driver closed...")

    except Exception as e:
        print(f"Unexpected error: \033[31m{e}\033[0m")
        raise WebDriverAutomationException(f"Automation failed: \033[31m{e}\033[0m")
