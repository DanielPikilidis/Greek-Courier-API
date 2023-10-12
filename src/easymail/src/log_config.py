from pydantic import BaseModel
from os import getenv

class LogConfig(BaseModel):

    LOGGER_NAME: str = getenv("LOG_NAME", "easymail-tracker")
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = getenv("LOG_LEVEL", "INFO").upper()
    LOG_PATH: str = getenv("LOG_PATH", "/tmp")

    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "default",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": f"{LOG_PATH}/{LOGGER_NAME}",
            "when": "midnight",
            "interval": 1,
            "backupCount": 14,
        }
    }
    loggers = {
        LOGGER_NAME: {"handlers": ["default", "file"], "level": LOG_LEVEL},
    }
