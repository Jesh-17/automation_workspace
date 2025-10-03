from flask import Flask, render_template, request, jsonify
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
            run_backoffice_automation_with_logging(file_path, output_location, user_data_dir, chrome_binary, mode, output_log)
            output_log.append("✅ Order automation completed successfully")
        elif mode == "bi":
            run_backoffice_automation_batch_with_logging(file_path, output_location, user_data_dir, chrome_binary, mode, output_log)
            output_log.append("✅ Batch automation completed successfully")

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

    return jsonify({"output": "\n".join(output_log)})


if __name__ == '__main__':
    app.run(debug=True)











































































































































































