# import psutil

# class ChromeRunningException(Exception):
#     """Raised when Chrome is already running."""
#     pass

# def is_chrome_running():
#     """Checks if Chrome is currently running."""
#     for proc in psutil.process_iter():
#         if proc.name() == "chrome.exe":
#             raise ChromeRunningException(
#                 "Chrome is currently running. Please close all Chrome instances and rerun the program."
#             )
#     return False
