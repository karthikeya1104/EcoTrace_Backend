import logging
import sys
from logging.handlers import RotatingFileHandler
import os

# Check if running in production (Render, etc.)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

# Configure logging
logger = logging.getLogger("ecotrace")
logger.setLevel(logging.DEBUG)

# Format for logs
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Console handler (always output to console - captured by Render logs)
console_handler = logging.StreamHandler(sys.stdout)
console_level = logging.INFO if IS_PRODUCTION else logging.INFO
console_handler.setLevel(console_level)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler only in development (not persistent on Render)
if not IS_PRODUCTION:
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    file_handler = RotatingFileHandler(
        "logs/ecotrace.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# Export logger
get_logger = lambda name: logging.getLogger(f"ecotrace.{name}")
