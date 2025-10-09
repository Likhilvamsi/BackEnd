# app/core/logger.py
import logging
from logging.handlers import RotatingFileHandler
import os

# Ensure logs directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logger
logger = logging.getLogger("my_app_logger")
logger.setLevel(logging.INFO)  # INFO, DEBUG, ERROR, etc.

# File handler (rotates logs when > 5MB, keeps 3 backups)
file_handler = RotatingFileHandler(
    f"{LOG_DIR}/app.log", maxBytes=5*1024*1024, backupCount=3
)
file_handler.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Format
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers only once
if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
