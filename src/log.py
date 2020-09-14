import logging
import os
import logging.handlers
from pathlib import Path


class Log:
    logger = logging.getLogger(__name__)

    @classmethod
    def create_log(cls):
        cls.logger.setLevel(logging.DEBUG)
        if (not os.path.isdir("config")):
            os.makedirs("config")

        file_handler = logging.handlers.RotatingFileHandler(os.path.join("config","log.log"),maxBytes = 1000000,backupCount = 1)
        f = logging.Formatter('%(asctime)s|%(levelname)-8s|%(message)s|','%d/%m/%Y %H:%M:%S')
        file_handler.setFormatter(f)
        cls.logger.addHandler(file_handler)
