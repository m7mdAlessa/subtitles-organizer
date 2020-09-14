import PTN
import os
import shutil
import requests
from log import Log
from pathlib import Path
import pysrt


class Organizer:

    @classmethod
    def init_settings(cls, sonarr, radarr):
        cls.son_enabled = sonarr.getboolean("enabled")
        cls.son_url = "http://" + sonarr["ip"] + ":" + sonarr["port"]
        cls.son_key = sonarr["api_key"]
        cls.rad_enabled = radarr.getboolean("enabled")
        cls.rad_url = "http://" + radarr["ip"] + ":" + radarr["port"]
        cls.rad_key = radarr["api_key"]

    @classmethod
    def organize(cls, path):
        file_name = os.path.basename(path)
        ext = os.path.splitext(file_name)[1]
        name = os.path.splitext(file_name)[0]
        if (not cls.son_enabled):
            Log.logger.warning("sonarr is not enabled")
            raise Exception
        parse = requests.get(
            str(cls.son_url) + "/api/parse?title=" + name.replace(" ", "%20") + "&apikey=" + str(cls.son_key)).json()
        if ("series" in parse and "title" in parse["series"]):
            e_id = parse["episodes"][0]["episodeFileId"]

            Log.logger.debug("TV Show : " + str(parse["series"]["title"]))
            Log.logger.debug("season : " + str(parse["episodes"][0]["seasonNumber"]))
            Log.logger.debug("episode : " + str(parse["episodes"][0]["episodeNumber"]))

            try:
                episode_response = requests.get(
                    str(cls.son_url) + "/api/episodefile/id=" + str(e_id) + "?apikey=" + str(cls.son_key)).json()
            except requests.exceptions.HTTPError:
                Log.logger.exception("Error trying to connect to Sonarr. Http error.")
                raise Exception
            except requests.exceptions.ConnectionError:
                Log.logger.exception("Error trying to connect to Sonarr. Connection Error.")
                raise Exception
            except requests.exceptions.Timeout:
                Log.logger.exception("Error trying to connect to Sonarr. Timeout Error.")
                raise Exception
            except requests.exceptions.RequestException:
                Log.logger.exception("Error trying to connect to Sonarr.")
                raise Exception

            if (not "path" in episode_response):
                Log.logger.error("can't find episode.")
                raise Exception

            episode_path = episode_response["path"]
            new_path = os.path.splitext(episode_path)[0]
            if (os.path.exists(episode_path)):
                Log.logger.info("moved from" + path + "to" + new_path + ext)
                if (ext == ".srt"):
                    try:
                        sub = pysrt.open(path)
                        sub.save(new_path + ext, encoding="utf-8")
                        os.remove(path)
                    except Exception:
                        try:
                            sub = pysrt.open(path, encoding="windows-1256")
                            sub.save(new_path + ext, encoding="utf-8")
                            os.remove(path)
                        except Exception:
                            shutil.move(path, new_path + ext)
                else:
                    shutil.move(path, new_path + ext)
                os.chmod(new_path + ext, 0o0777)



        else:
            info = PTN.parse(name)
            if (not cls.rad_enabled):
                Log.logger.error("radarr is not enabled")
                raise Exception

            title = info["title"]
            if ("year" in info):
                title = title + " (" + str(info["year"]) + ")"
            Log.logger.debug("Movie : " + title)
            try:
                response1 = requests.get(
                    str(cls.rad_url) + "/api/movie/lookup?term=" + title.replace(" ", "%20") + "&apikey=" + str(
                        cls.rad_key)).json()
                response2 = requests.get(str(cls.rad_url) + "/api/movie?apikey=" + str(cls.rad_key)).json()
            except requests.exceptions.HTTPError:
                Log.logger.exception("Error trying to connect to radarr. Http error.")
                raise Exception
            except requests.exceptions.ConnectionError:
                Log.logger.exception("Error trying to connect to radarr. Connection Error.")
                raise Exception
            except requests.exceptions.Timeout:
                Log.logger.exception("Error trying to connect to radarr. Timeout Error.")
                raise Exception
            except requests.exceptions.RequestException:
                Log.logger.exception("Error trying to connect to radarr.")
                raise Exception

            found = False

            for i in response1:
                tmdbid = i["tmdbId"]
                for j in response2:
                    if (j["tmdbId"] == tmdbid):
                        rad_info = j
                        found = True
                        break

            if (not found):
                Log.logger.error("can't find movie.")
                raise Exception
            if (not "path" in rad_info):
                Log.logger.error("can't find path.")
                raise Exception
            mov_path = Path(rad_info["path"] + "/" + (rad_info["movieFile"])["relativePath"])
            if (os.path.exists(mov_path)):
                new_path = os.path.splitext(mov_path)[0]
                Log.logger.info("moved from" + path + "to" + new_path + ext)
                if (ext == ".srt"):
                    try:
                        sub = pysrt.open(path)
                        sub.save(new_path + ext, encoding="utf-8")
                        os.remove(path)
                    except Exception:
                        try:
                            sub = pysrt.open(path, encoding="windows-1256")
                            sub.save(new_path + ext, encoding="utf-8")
                            os.remove(path)
                        except Exception:
                            shutil.move(path, new_path + ext)
                else:
                    shutil.move(path, new_path + ext)
                os.chmod(new_path + ext, 0o0777)

    @classmethod
    def organize_ptn(cls, path):
        file_name = os.path.basename(path)
        ext = os.path.splitext(file_name)[1]
        name = os.path.splitext(file_name)[0]
        info = PTN.parse(name)
        if ("season" in info):
            if (not cls.son_enabled):
                Log.logger.error("sonarr is not enabled")
                return

            title = info["title"]
            season = info["season"]
            if (not "episode" in info):
                Log.logger.warning("can't find episode number")
                parse = requests.get(
                    str(cls.son_url) + "/api/parse?title=" + name.replace(" ", "%20") + "&apikey=" + str(
                        cls.son_key)).json()
                episode = parse["episodes"][0]["episodeNumber"]
                season = parse["episodes"][0]["seasonNumber"]
            else:
                episode = info["episode"]

            if (isinstance(episode, list)):
                episode = episode[0]

            Log.logger.debug("TV Show : " + str(title))
            Log.logger.debug("season : " + str(season))
            Log.logger.debug("episode : " + str(episode))

            try:
                response1 = requests.get(
                    str(cls.son_url) + "/api/series/lookup?term=" + title.replace(" ", "%20") + "&apikey=" + str(
                        cls.son_key)).json()
                response2 = requests.get(str(cls.son_url) + "/api/series?apikey=" + str(cls.son_key)).json()
            except requests.exceptions.HTTPError:
                Log.logger.exception("Error trying to connect to Sonarr. Http error.")
                return
            except requests.exceptions.ConnectionError:
                Log.logger.exception("Error trying to connect to Sonarr. Connection Error.")
                return
            except requests.exceptions.Timeout:
                Log.logger.exception("Error trying to connect to Sonarr. Timeout Error.")
                return
            except requests.exceptions.RequestException:
                Log.logger.exception("Error trying to connect to Sonarr.")
                return
            found = False
            for i in response1:
                tvdbid = i["tvdbId"]
                for j in response2:
                    if (j["tvdbId"] == tvdbid):
                        son_info = j
                        found = True
                        break
            if (not found):
                Log.logger.error("can't find tv show.")
                return

            series_id = son_info["id"]

            try:
                episodes_response = requests.get(
                    str(cls.son_url) + "/api/episode?seriesId=" + str(series_id) + "&apikey=" + str(cls.son_key)).json()
            except requests.exceptions.HTTPError:
                Log.logger.exception("Error trying to connect to Sonarr. Http error.")
                return
            except requests.exceptions.ConnectionError:
                Log.logger.exception("Error trying to connect to Sonarr. Connection Error.")
                return
            except requests.exceptions.Timeout:
                Log.logger.exception("Error trying to connect to Sonarr. Timeout Error.")
                return
            except requests.exceptions.RequestException:
                Log.logger.exception("Error trying to connect to Sonarr.")
                return
            found = False

            for i in episodes_response:
                if (i["seasonNumber"] == season):
                    if (i["episodeNumber"] == episode):
                        e_info = i
                        found = True
                        break
                    elif ("absoluteEpisodeNumber" in i):
                        if (i["absoluteEpisodeNumber"] == episode):
                            e_info = i
                            found = True
                            break

            if (not found):
                Log.logger.error("can't find episode.")
                return
            if (not "hasFile" in e_info):
                return
            if (not e_info["hasFile"]):
                Log.logger.error("can't find episode file.")
                return

            episodefile = e_info["episodeFile"]
            episode_path = episodefile["path"]
            new_path = os.path.splitext(episode_path)[0]
            if (os.path.exists(episode_path)):
                Log.logger.info("moved from" + path + "to" + new_path + ext)
                if (ext == ".srt"):
                    try:
                        sub = pysrt.open(path)
                        sub.save(new_path + ext, encoding="utf-8")
                        os.remove(path)
                    except Exception:
                        try:
                            sub = pysrt.open(path, encoding="windows-1256")
                            sub.save(new_path + ext, encoding="utf-8")
                            os.remove(path)
                        except Exception:
                            shutil.move(path, new_path + ext)
                else:
                    shutil.move(path, new_path + ext)
                os.chmod(new_path + ext, 0o0777)
        else:
            if (not cls.rad_enabled):
                Log.logger.error("radarr is not enabled")
                return

            title = info["title"]
            Log.logger.debug("Movie : " + title)
            try:
                response1 = requests.get(
                    str(cls.rad_url) + "/api/movie/lookup?term=" + title.replace(" ", "%20") + "&apikey=" + str(
                        cls.rad_key)).json()
                response2 = requests.get(str(cls.rad_url) + "/api/movie?apikey=" + str(cls.rad_key)).json()
            except requests.exceptions.HTTPError:
                Log.logger.exception("Error trying to connect to radarr. Http error.")
                return
            except requests.exceptions.ConnectionError:
                Log.logger.exception("Error trying to connect to radarr. Connection Error.")
                return
            except requests.exceptions.Timeout:
                Log.logger.exception("Error trying to connect to radarr. Timeout Error.")
                return
            except requests.exceptions.RequestException:
                Log.logger.exception("Error trying to connect to radarr.")
                return

            found = False

            for i in response1:
                tmdbid = i["tmdbId"]
                for j in response2:
                    if (j["tmdbId"] == tmdbid):
                        rad_info = j
                        found = True
                        break

            if (not found):
                Log.logger.error("can't find movie.")
                return
            if (not "path" in rad_info):
                Log.logger.error("can't find path.")
                return
            mov_path = Path(rad_info["path"] + "/" + (rad_info["movieFile"])["relativePath"])
            if (os.path.exists(mov_path)):
                new_path = os.path.splitext(mov_path)[0]
                Log.logger.info("moved from" + path + "to" + new_path + ext)
                if (ext == ".srt"):
                    try:
                        sub = pysrt.open(path)
                        sub.save(new_path + ext, encoding="utf-8")
                        os.remove(path)
                    except Exception:
                        try:
                            sub = pysrt.open(path, encoding="windows-1256")
                            sub.save(new_path + ext, encoding="utf-8")
                            os.remove(path)
                        except Exception:
                            shutil.move(path, new_path + ext)
                else:
                    shutil.move(path, new_path + ext)
                os.chmod(new_path + ext, 0o0777)
