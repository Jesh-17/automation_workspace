import shutil
from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile

# Your existing imports...
from env_utils import get_env_vars, CustomEnvException
from read_input_csv import read_input_csv, CSVReadException
from run_backoffice_wrapper import run_backoffice_automation_with_logging, run_backoffice_automation_batch_with_logging
from merge_csv_files import CSVMergeException
from run_backoffice_automation import WebDriverAutomationException





app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run():
    mode = request.form.get('mode', '').strip().lower()
    uploaded_file = request.files.get('file')
    output_log = []
    download_url = None  # Initialize download URL

    try:
        if not uploaded_file:
            raise CSVReadException("No CSV file uploaded.")

        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, uploaded_file.filename)
        uploaded_file.save(file_path)

        output_log.append("--------------------------------------------------------------------------------")
        output_location, user_data_dir, chrome_binary = get_env_vars(mode)
        # output_log.append("✅ Environment variables loaded successfully")
        # output_log.append(f"INPUT_FILE: {file_path}")
        # output_log.append(f"OUTPUT_LOCATION: {output_location}")
        # output_log.append(f"CHROME_USER_DATA_DIR: {user_data_dir}")
        # output_log.append(f"CHROME_BINARY_LOCATION: {chrome_binary}")
        # output_log.append("--------------------------------------------------------------------------------")

        header, ids = read_input_csv(file_path, mode)
        output_log.append("✅ CSV input information loaded successfully")
        output_log.append(f"CSV header used: {header}")
        output_log.append(f"Extracted IDs: {ids}")
        output_log.append("--------------------------------------------------------------------------------")

        if mode == "oi":
            merged_file_path = run_backoffice_automation_with_logging(file_path, output_location, user_data_dir, chrome_binary, mode, output_log)
            output_log.append("✅ Order automation completed successfully")

            if merged_file_path and os.path.exists(merged_file_path):

               
                # Clean up old oi temp download folder
                safe_download_dir = os.path.join(os.getcwd(), "temp_oi_merge_csv_downloads")
                if os.path.exists(safe_download_dir):
                    shutil.rmtree(safe_download_dir)
                    print(f"Deleted old oi temp folder: {safe_download_dir}")
                # Create a temp download folder inside your Flask app directory
                os.makedirs(safe_download_dir, exist_ok=True)


                # Copy file there
                safe_filename = os.path.basename(merged_file_path)
                safe_file_path = os.path.join(safe_download_dir, safe_filename)
                shutil.copy(merged_file_path, safe_file_path)
            
                # Generate URL
                download_url = f"/download/temp_oi_merge_csv_downloads/{safe_filename}"
                #output_log.append(f"✅ Merged CSV ready for download: {safe_filename}")

            else:
                output_log.append("❌ As there is no merged CSV file associated with the order IDs, the download button will not be shown.")

        elif mode == "bi":
            output_bi_folder = run_backoffice_automation_batch_with_logging(file_path, output_location, user_data_dir, chrome_binary, mode, output_log)
            output_log.append("✅ Batch automation completed successfully")

            if output_bi_folder and os.path.exists(output_bi_folder):
               
                # Clean up old bi temp download folder
                safe_download_dir = os.path.join(os.getcwd(), "temp_bi_downloads")
                if os.path.exists(safe_download_dir):
                    shutil.rmtree(safe_download_dir)
                    print(f"Deleted old bi temp folder: {safe_download_dir}")
                # Create a temp download folder inside your Flask app directory
                os.makedirs(safe_download_dir, exist_ok=True)


                # Create ZIP file
                zip_name = os.path.basename(output_bi_folder) + ".zip"
                zip_path = os.path.join(safe_download_dir, zip_name)
                shutil.make_archive(zip_path.replace(".zip", ""), "zip", output_bi_folder)

                # Generate download URL
                download_url = f"/download/temp_bi_downloads/{zip_name}"
                #output_log.append(f"✅ ZIP created for batch ids: {zip_name}")
                
            else:
                output_log.append("❌ As there are no processed batch ID CSV files to zip, the download button will not be shown.")

        output_log.append("✅ Automation completed successfully")
        output_log.append("--------------------------------------------------------------------------------")


    except CustomEnvException as e:
        output_log.append(f"❌ Environment validation failed: {e}")
    except WebDriverAutomationException as e:
        output_log.append(f"❌ WebDriver automation failed: {e}")
    except CSVReadException as e:
        output_log.append(f"❌ CSV read failed: {e}")
    except CSVMergeException as e:
        output_log.append(f"❌ CSV merge failed: {e}")
    except Exception as e:
        output_log.append(f"❌ Unexpected error: {e}")


    return jsonify({
            "output": "\n".join(output_log),
            "download_url": download_url
    })



@app.route('/download/<folder>/<filename>', methods=['GET'])
def download(folder, filename):
    
    if folder not in ["temp_oi_merge_csv_downloads", "temp_bi_downloads"]:
            return jsonify({"error": "Invalid folder"}), 400

    safe_download_dir = os.path.join(os.getcwd(), folder)
    file_path = os.path.join(safe_download_dir, filename)
 
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0', port=5000, debug=True)

































































































































































