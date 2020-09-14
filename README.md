# subtitles-organizer
subtitles-organizer works with Sonarr or Radarr to add subtitles to TV shows or movies that are added to Sonarr or Radarr.

It works by monitoring a directory for any changes, when a subtitle file is moved to the directory it will be moved to the location of the episode or movie and it will be renamed to match the name of the video file.

# Installation through docker
You can find the docker image [here](https://hub.docker.com/r/m7mdalessa/subtitles-organizer)

### docker-compose
```
---
version: "2.1"
services:
  subtitles-organizer:
    image: m7mdalessa/subtitles-organizer
    container_name: subtitles-organizer
    volumes:
      - /path/to/config:/config
      - /path/to/monitored_directory:/subtitles
      - /path/to/movies:/movies
      - /path/to/tvshows:/tv          # you should add any directories used by Sonarr or Radarr
    restart: unless-stopped
```

# Configuration
After running it for the first time you should edit the config file at "/config/config.ini".

you should enable Sonarr and Raddar and add their ip and api key.
