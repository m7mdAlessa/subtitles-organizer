from configparser import ConfigParser
from log import Log
import os
from pathlib import Path


class Config:

    def __init__(self):
        self.config_object = ConfigParser()

    def load_config(self):
        if (not os.path.isdir("config")):
            Log.logger.debug("creating config directory")
            os.makedirs("config")

        if (os.path.isfile(Path("config/config.ini"))):
            Log.logger.debug("reading config file")
            self.config_object.read(os.path.join("config", "config.ini"))
        else:
            Log.logger.debug("creating config file")
            self.config_object["GENERAL"] = {
                "subtitles_path": "subtitles/"
            }
            self.config_object["SONARR"] = {
                "enabled": "false",
                "ip": "localhost",
                "port": "8989",
                "api_key": ""
            }
            self.config_object["RADARR"] = {
                "enabled": "false",
                "ip": "localhost",
                "port": "7878",
                "api_key": ""
            }
            with open(Path("config/config.ini"), 'w') as conf:
                self.config_object.write(conf)
