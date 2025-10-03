# Payment Gateway Backoffice Automation Suite (Frontend)
Backoffice Application Automation for extracting Payment Information, using Python with flask and Selenium

   - ## Dependencies
      1. Python 3 (Windows Installation)
      2. VSCode
      3. requirements.txt (libraries Installation using PIP)
      4. Excel
      5. Command Prompt Or Powershell (For Execution)

   - ## Environment
      1. Windows 11 Enterprise
      2. Google Chrome

   - ## Objective
      1. Application facilitates automated fetching of Payment information of individual order IDs, batch IDs with different payment statuses in a database during events such as RDS failure or other payment failures. 
      2. The code utilizes the PG Backoffice Application and the Selenium browser automation tool to emulate user actions and download CSV files for each order ID provided in a list. These individual CSV files are then merged into a consolidated output list and saved to a specified path. 
      3. Also this code utilizes the PG Backoffice Application and the Selenium browser automation tool to emulate user actions and download CSV files for each batch ID provided in a list 
      4. By automating these actions, the tool eliminates the need for manual intervention and streamlines the entire process from start to end.

   - ## Prerequisites
      
      1. While running the script, It shows the frontend link `http://127.0.0.1:5000` in the terminal, copy this link and paste it in your browser (Here we are using the `flask`). Now select as your requirement either `Order Input (oi)` or `Batch Input (oi)` and `upload the corresponding input CSV file` then click on `Run Automation`. Now It opens the corresponding application site and if site is asking the login credentials give those and wait for script to be completed. Once done, 're-run the script again' and follow the same previous process it will work. (Note: We can use One tab for: `Order Input (oi)` and another tab for: `Batch Input (oi)` for both of them follow this step 1)

         - ### Check below for Order Input (oi),

            <div align="center">
                  <img src="./images/oi.png" alt="order-input">
                  <img src="./images/oi_app_loggedout.png" alt="order-input">
            </div>

            - #### Error handling, if user `haven't logged in (or) logged-in first time after session expired`, wait for script to be completed then browser will close and we will see the output like below,

               <div align="center">
                     <img src="./images/oi_app_not_loggedin_or_loggedInFirstTimeAfterSessionExpired.png" alt="order-input">
               </div>

            - #### Error handling, if user `haven't logged in and close the browser`, wait for script to be completed then we will see the output like below,

               <div align="center">
                     <img src="./images/oibrowser_closed.png" alt="order-input">
                     <img src="./images/oibrowser_closed_continuation.png" alt="order-input">
               </div>

         Note: But under `output-data-order-id` a empty `Backoffice-orderids-data-DD-MM-YYYY-(At-time-HH-MM-SS)\merge-output-data\` folder will be created
            
         - ### Check below for Batch Input (bi),

            <div align="center">
                  <img src="./images/bi.png" alt="batch-input">
                  <img src="./images/bi_app_loggedout.png" alt="batch-input">
            </div>

            - #### Error handling, if user `haven't logged in (or) logged-in first time after session expired`, wait for script to be completed then browser will close and we will see the output like below,

               <div align="center">
                     <img src="./images/bi_app_not_loggedin_or_loggedInFirstTimeAfterSessionExpired.png" alt="batch-input">
               </div>

            - #### Error handling, if user `haven't logged in and close the browser`, wait for script to be completed  then we will see the output like below,

               <div align="center">
                     <img src="./images/bibrowser_closed.png" alt="batch-input">
                     <img src="./images/bibrowser_closed_continuation.png" alt="batch-input">
               </div>

         Note: But under `output-data-batch-id` a empty `Backoffice-batchids-data-DD-MM-YYYY-(At-time-HH-MM-SS)\` folder will be created


   - ## Usage
      1. Clone this repository to your local machine.
      2. Install the necessary dependencies using `pip install -r requirements.txt`.
      3. Set up the required environment variables in a `.env` file:

         ```
            ORDER_OUTPUT_LOCATION=".\\output-data-order-id"
            ORDER_CHROME_USER_DATA_DIR="C:\\orderid_chrome_user_data_directory"

            BATCH_OUTPUT_LOCATION=".\\output-data-batch-id"
            BATCH_CHROME_USER_DATA_DIR="C:\\batchid_chrome_user_data_directory"

            CHROME_BINARY_LOCATION="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

         ```
         Replace the paths with your actual paths as needed if you want.

      4. Run the script `app.py` using `python app.py` in the terminal.

         - ### Order Input (oi)
            1. The script will navigate to the backoffice application and start fetching payment information for the order IDs specified in the order input csv file by uploading it.
            2. The order input csv file includes data with a single column and a header. Please ensure that the header is either `orderId` or `transactionId`, as the data under that header will be processed accordingly.
            3. The downloaded CSV files will be saved to the `\output-data-order-id\Backoffice-orderids-data-DD-MM-YYYY-(At-time-HH-MM-SS)\` folder. Once all CSV files are downloaded, they will be merged into a single CSV file named `\Backoffice-orderids-data-DD-MM-YYYY-(At-time-HH-MM-SS)\merge-output-data\` in the same output folder.
            4. If `input order IDs are perfect` then,

               <div align="center">
                  <img src="./images/oi_ids_perfect.png" alt="order-input">
               </div>

            - #### Error handling,
               - If `No order IDs` are present then,

                  <div align="center">
                     <img src="./images/oi_no_ids.png" alt="order-input">
                  </div>

               - If Nothing is there in uploaded input csv..like empty file then,
                  <div align="center">
                     <img src="./images/oi_csv_empty.png" alt="order-input">
                  </div>

               - If `any ID is invalid` then It stops the further processing of IDs and it only merges the processed IDs.
                  <div align="center">
                     <img src="./images/oi_invalid_id.png" alt="order-input">
                  </div>


         - ### Batch Input (bi)
            1. The script will navigate to the backoffice application and start fetching payment information for the batch IDs specified in the batch input csv file by uploading it.
            2. The batch input csv file includes data with a single column and a header. Please ensure that the header is `batchId` `, as the data under that header will be processed accordingly.
            3. The downloaded CSV files will be saved to the `\output-data-batch-id\Backoffice-batchids-data-DD-MM-YYYY-(At-time-HH-MM-SS)\` folder.
            4. If `input batch IDs are perfect` then,

               <div align="center">
                  <img src="./images/bi_ids_perfect.png" alt="batch-input">
               </div>

            - #### Error handling,

               - If `No batch IDs` are present then,
                  <div align="center">
                     <img src="./images/bi_no_ids.png" alt="batch-input">
                  </div>

               - If Nothing is there in uploaded input csv..like empty file then,
                  <div align="center">
                     <img src="./images/bi_csv_empty.png" alt="batch-input">
                  </div>
               - If `any ID is invalid` then It stops the further processing of IDs.
                  <div align="center">
                     <img src="./images/bi_invalid_id.png" alt="batch-input">
                  </div>

      - ### Note: if `any modification or changes` are done in the script, then you should `re-run` the script to effect the changes

   
   - ## Common Error Handling
      
      - ### Handling invalid uploaded csv, if input type is Order Input (oi) given then
        1. If user uploaded wrong input csv,
           <div align="center">
                  <img src="./images/oi_input_csv_invalid.png" alt="order-input">
           </div>


      - ### Handling invalid uploaded csv if input type is Batch Input (bi) given then
        1. If user uploaded wrong input csv,
           <div align="center">
                  <img src="./images/bi_input_csv_invalid.png" alt="batch-input">
           </div>

      - ### Uploaded input csv data columns are different names then,
        1. In the uploaded input csv of `Order Input (oi)` column names are different,
           <div align="center">
                  <img src="./images/oi_invalid_csv_column_name.png" alt="order-input">
            </div>
         
        2. In the uploaded input csv of `Batch Input (bi)` column names are different,
           <div align="center">
                  <img src="./images/bi_invalid_csv_column_name.png" alt="batch-input">
            </div>

      - ### Handling .env variable errors
         - #### Order Input (oi)
            1. In .env, if any variable had names are modified or missed otherthan `CHROME_BINARY_LOCATION` variable, then
               <div align="center">
                     <img src="./images/oi_missing_env_var.png" alt="order-input">
               </div>

            2. In .env, `CHROME_BINARY_LOCATION` path is incorrect then
               <div align="center">
                     <img src="./images/oi_chrome_binary_path_invalid.png" alt="order-input">
               </div>

         - #### Brder Input (oi)
            1. In .env, if any variable had names are modified or missed otherthan `CHROME_BINARY_LOCATION` variable, then
               <div align="center">
                     <img src="./images/bi_missing_env_var.png" alt="batch-input">
               </div>

            2. In .env, `CHROME_BINARY_LOCATION` path is incorrect then
               <div align="center">
                     <img src="./images/bi_chrome_binary_path_invalid.png" alt="batch-input">
               </div>

      - ### Dependency Errors
         - During Chrome Version Upgrades, Selenium library might lose its compatibility with chrome drivers. It will throw exceptions Like Error Message: Session not created: This Version of Chromedriver only supports Chrome Version. During Such Instances, use below command to Upgrade packages `pip install --upgrade -r requirements.txt`


   - ## Contributing
      - If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request. Your contributions are welcome and highly appreciated!