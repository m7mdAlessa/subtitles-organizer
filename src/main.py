from log import Log
from config import Config
import os
from watcher import Watcher
from pathlib import Path
import sys
import requests
from organizer import Organizer
import time

def start():
    conf = Config()
    conf.load_config()
    monitored_dir = Path(conf.config_object["GENERAL"]["subtitles_path"])
    if (not os.path.isdir(monitored_dir)):
        Log.logger.critical("Can't find the subtitles directory")
        raise Exception("Can't find the subtitles directory")
    sonarr = conf.config_object["SONARR"]
    radarr = conf.config_object["RADARR"]
    son_enabled = sonarr.getboolean("enabled")
    rad_enabled = radarr.getboolean("enabled")
    if ((not son_enabled) & (not rad_enabled)):
        Log.logger.critical("sonarr and raddar are both disabled")
        raise Exception("sonarr and raddar are both disabled")
    elif ((not son_enabled) | (not rad_enabled)):
        Log.logger.warning(("radarr" if son_enabled else "sonarr") + "is disabled")

    if (son_enabled):
        url_sonarr = "http://" + sonarr["ip"] + ":" + sonarr["port"] + "/api/system/status?apikey=" + sonarr["api_key"]
        try:
            r = requests.get(url_sonarr, timeout=60)
        except requests.exceptions.HTTPError:
            Log.logger.exception("Error trying to connect to Sonarr. Http error.")
            conf.config_object["SONARR"]["enabled"] = "false"
        except requests.exceptions.ConnectionError:
            Log.logger.exception("Error trying to connect to Sonarr. Connection Error.")
            conf.config_object["SONARR"]["enabled"] = "false"
        except requests.exceptions.Timeout:
            Log.logger.exception("Error trying to connect to Sonarr. Timeout Error.")
            conf.config_object["SONARR"]["enabled"] = "false"
        except requests.exceptions.RequestException:
            Log.logger.exception("Error trying to connect to Sonarr.")
            conf.config_object["SONARR"]["enabled"] = "false"
        else:
            Log.logger.info("Connected successfully to sonarr.")
    if (rad_enabled):
        url_radarr = "http://" + radarr["ip"] + ":" + radarr["port"] + "/api/system/status?apikey=" + radarr["api_key"]
        try:
            r = requests.get(url_radarr, timeout=60)
        except requests.exceptions.HTTPError:
            Log.logger.exception("Error trying to connect to radarr. Http error.")
            conf.config_object["RADARR"]["enabled"] = "false"
        except requests.exceptions.ConnectionError:
            Log.logger.exception("Error trying to connect to radarr. Connection Error.")
            conf.config_object["RADARR"]["enabled"] = "false"
        except requests.exceptions.Timeout:
            Log.logger.exception("Error trying to connect to radarr. Timeout Error.")
            conf.config_object["RADARR"]["enabled"] = "false"
        except requests.exceptions.RequestException:
            Log.logger.exception("Error trying to connect to radarr.")
            conf.config_object["RADARR"]["enabled"] = "false"
        else:
            Log.logger.info("Connected successfully to radarr.")

    if ((not son_enabled) & (not rad_enabled)):
        Log.logger.critical("couldn't connect to sonarr or raddar")
        raise Exception("couldn't connect to sonarr or raddar")

    Organizer.init_settings(sonarr, radarr)
    watcher = Watcher(monitored_dir)
    Log.logger.info("started monitoring " + str(monitored_dir))
    watcher.run()


if __name__ == '__main__':
    os.umask(0)
    Log.create_log()
    while True:
        try:
            start()
        except Exception as e:
            Log.logger.debug(e)
            time.sleep(10)