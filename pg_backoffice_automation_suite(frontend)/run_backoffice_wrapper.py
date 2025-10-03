from run_backoffice_automation import run_backoffice_automation
from run_backoffice_automation_batch import run_backoffice_automation_batch

def run_backoffice_automation_with_logging(file_name, output_location, user_data_dir, chrome_binary, mode, output_log):
    import builtins
    original_print = builtins.print

    def custom_print(*args, **kwargs):
        message = " ".join(str(arg) for arg in args)
        output_log.append(message)
        original_print(*args, **kwargs)

    builtins.print = custom_print

    try:
        run_backoffice_automation(file_name, output_location, user_data_dir, chrome_binary, mode)
    finally:
        builtins.print = original_print  # Restore original print


def run_backoffice_automation_batch_with_logging(file_name, output_location, user_data_dir, chrome_binary, mode, output_log):
    import builtins
    original_print = builtins.print

    def custom_print(*args, **kwargs):
        message = " ".join(str(arg) for arg in args)
        output_log.append(message)
        original_print(*args, **kwargs)

    builtins.print = custom_print

    try:
        run_backoffice_automation_batch(file_name, output_location, user_data_dir, chrome_binary, mode)
    finally:
        builtins.print = original_print  # Restore original print