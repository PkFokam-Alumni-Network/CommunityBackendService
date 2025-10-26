import logging
import os
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json
from datetime import datetime, timezone
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    Makes logs easily parseable for analysis tools.
    """
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "endpoint"):
            log_data["endpoint"] = record.endpoint
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
            
        return json.dumps(log_data)


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "/app/logs",
    enable_console: bool = True,
    enable_file: bool = True,
    json_format: bool = True,
):
    """
    Configure application-wide logging with file rotation.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        enable_console: Whether to log to console
        enable_file: Whether to log to files
        json_format: Whether to use JSON formatting (recommended for production)
    """
    
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Choose formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    handlers = []
    
    # Console Handler (for Docker logs)
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)
    
    # File Handlers
    if enable_file:
        # General application logs (rotates daily, keeps 30 days)
        app_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_dir, "app.log"),
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8",
        )
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(formatter)
        app_handler.suffix = "%Y-%m-%d"
        handlers.append(app_handler)
        
        # Error logs (rotates at 10MB, keeps 10 files)
        error_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, "error.log"),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        handlers.append(error_handler)
        
        # Access logs (rotates daily, keeps 7 days)
        access_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_dir, "access.log"),
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8",
        )
        access_handler.setLevel(logging.INFO)
        access_handler.setFormatter(formatter)
        access_handler.suffix = "%Y-%m-%d"
        # Only handle access logs
        access_handler.addFilter(lambda record: "access" in record.name.lower())
        handlers.append(access_handler)
    
    # Add all handlers to root logger
    for handler in handlers:
        root_logger.addHandler(handler)
    
    return root_logger


# Initialize logger based on environment
ENV = os.getenv("ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", "/app/logs")

# Setup logging
setup_logging(
    log_level=LOG_LEVEL,
    log_dir=LOG_DIR,
    enable_console=True,
    enable_file=True,
    json_format=(ENV == "production"),  # JSON in production, readable in dev
)

# Export logger for use in other modules
LOGGER = logging.getLogger("fastapi_app")
ACCESS_LOGGER = logging.getLogger("fastapi_app.access")