from loguru import logger
import os, sys

# Ensure the logs directory exists
logs_dir = "logs"
os.makedirs(logs_dir, exist_ok=True)

# Configure the logger to write to a single log file
log_file = os.path.join(logs_dir, "app.log")
logger.add(log_file, rotation="10 MB", retention="4 weeks", backtrace=True, diagnose=True)

# Optionally, configure the logger to also log to stdout
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")
