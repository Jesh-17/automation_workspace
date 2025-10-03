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

def run_backoffice_automation_batch(file_name, output_location, user_data_dir, chrome_binary, mode):
    try:


        # Create folder
        timestamp = datetime.now().strftime("%d-%m-%Y-(At-time-%H-%M-%S)")
        folder_name = f"Backoffice-batchids-data-{timestamp}"
        output_location = os.path.join(os.path.abspath(output_location), folder_name)

        os.makedirs(output_location, exist_ok=True)

        # Setup Chrome options
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
            "download.default_directory": output_location,
            "download.prompt_for_download": False,
            "safebrowsing.enabled": False,
        })
        options.add_argument(f"user-data-dir={user_data_dir}")
        options.binary_location = chrome_binary
        options.add_argument("--log-level=3")

        driver = None
        

        try:
            driver = webdriver.Chrome(options=options)
            driver.get("https://pagos-backoffice.tigocloud.net/batch-item-reports")

            #Give user time to log in manually once opens initially if you want
            #time.sleep(60)  # Adjust this duration as needed

            try:
                id_type, id_numbers = read_input_csv(file_name, mode)
                print(f"Loaded {len(id_numbers)} IDs from CSV using ID type: {id_type}")
            except Exception as e:
                raise CSVReadException(f"Failed to read input CSV: {e}")

            processed_ids = []
            progress_bar = tqdm(id_numbers, desc="Processing IDs", unit=" ID")

            for id_number in progress_bar:
                try:
                    # Step 1: Enter ID
                    input_field = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "batchId"))
                    )
                    input_field.clear()
                    input_field.send_keys(id_number)
                    time.sleep(2)
                    input_field.send_keys(Keys.RETURN)
                    time.sleep(3)
                except TimeoutException:
                    print("\nReason: Possible login issue. Timed out while locating the input field.")
                    break
                except NoSuchElementException:
                    print("\nReason: Login page not loaded properly. Input field not found.")
                    break

                try:
                    # Step 2: Click Export CSV
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Export CSV')]"))
                    )
                    export_button = driver.find_element(By.XPATH, "//button[contains(.,'Export CSV')]")
                    export_button.click()
                    time.sleep(5)

                    print(f"Processed ID: {id_number}")
                    processed_ids.append(id_number)
                except TimeoutException:
                    print(f"\nReason: Invalid ID at {id_number}. Export button not clickable. Stopping further processing.")
                    break
                except NoSuchElementException:
                    print(f"\nReason: Invalid ID at {id_number}. Export button not found. Stopping further processing.")
                    break
                except Exception as inner_e:
                    print(f"\nUnexpected error occurred with ID {id_number}: {inner_e}. Stopping further processing.")
                    break


            progress_bar.close()

            if processed_ids:
                print("\nSuccessfully processed IDs:")
                for pid in processed_ids:
                    print(f" - {pid}")
                print("Automation completed...")
            else:
                print("\nNo IDs were successfully processed.")

        except Exception as e:
            raise WebDriverAutomationException(f"Web driver error: {e}")
        
        finally:
            if driver:
                    #time.sleep(5)
                    #input("Press Enter to close the browser...")
                    time.sleep(60)  # Keeps browser open for last 60 seconds before closing
                    driver.quit()
                    print("Driver closed...")

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise WebDriverAutomationException(f"Automation failed: {e}")
