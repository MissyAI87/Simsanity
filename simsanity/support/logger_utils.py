import logging, sys, os
from logging.handlers import RotatingFileHandler
from pathlib import Path

TRACE_LEVEL_NUM = 5
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")

def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        self._log(TRACE_LEVEL_NUM, message, args, **kws)

logging.Logger.trace = trace

DEBUG_MODE = os.environ.get("ECHO_DEBUG", "false").lower() == "true"
TRACE_MODE = os.environ.get("ECHO_TRACE", "false").lower() == "true"

# Project root (one level up from /support)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Log level from env or default to INFO
_ENV_LEVEL = os.environ.get("ECHO_LOG_LEVEL", "INFO").upper()
_LEVEL = getattr(logging, _ENV_LEVEL, logging.INFO)

def get_logger():
    logging.basicConfig(handlers=[])
    logging.root.handlers.clear()
    logger = logging.getLogger("echo")
    logger.propagate = False
    logger.handlers.clear()
    if logger.handlers:  # avoid duplicate handlers
        return logger
    logger.setLevel(_LEVEL)
    if TRACE_MODE:
        logger.setLevel(TRACE_LEVEL_NUM)
    elif DEBUG_MODE and not TRACE_MODE:
        logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # Stream handler to stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    # Logs are written to support/logs/echo.log by default.
    # Override with ECHO_LOG_FILE env variable.
    logs_dir = PROJECT_ROOT / "support" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = os.environ.get("ECHO_LOG_FILE", "echo.log")
    file_handler = RotatingFileHandler(
        logs_dir / log_file,
        maxBytes=5*1024*1024,
        backupCount=3,
        mode="a"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

def unified_log(message: str, level="INFO"):
    logger = get_logger()
    getattr(logger, level.lower(), logger.info)(message)
    sys.stdout.flush()

def debug_log(message: str):
    logger = get_logger()
    logger.debug(message)
    sys.stdout.flush()

def trace_log(message: str):
    if TRACE_MODE:
        logger = get_logger()
        logger.trace(message)
        sys.stdout.flush()


def log(message):
    """Universal logging wrapper for compatibility with older modules."""
    try:
        # Safely handle string or dict inputs
        if isinstance(message, dict):
            msg_str = str(message.get("message", message))
        else:
            msg_str = str(message)
        unified_log(msg_str)
    except Exception as e:
        print(f"[LOG ERROR] {e}: {message}")


# Helper: conditional debug log
def conditional_debug(message: str, condition: bool = True):
    """
    Log a debug message only if the given condition is True.
    Safe for use throughout Simsanity (used by safety/security.py and others).
    """
    if not condition:
        return
    logger = get_logger()
    logger.debug(f"[CONDITIONAL DEBUG] {message}")
    sys.stdout.flush()
