from pydantic import BaseModel
from os import getenv

class LogConfig(BaseModel):

    LOGGER_NAME: str = "geniki-tracker"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = getenv("LOG_LEVEL", "INFO").upper()

    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    }
    loggers: dict= {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }
