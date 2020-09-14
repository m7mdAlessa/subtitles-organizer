import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from log import Log
from organizer import Organizer


class Watcher:

    def __init__(self, directory):
        self.observer = Observer()
        self.DIRECTORY_TO_WATCH = directory

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
                if (not self.observer.is_alive()):
                    Log.logger.critical("observer Error")
                    break
        except:
            self.observer.stop()
            Log.logger.critical("observer Error")

        self.observer.join()


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        elif (event.event_type == 'created'):
            if (os.path.isfile(event.src_path)):
                if (event.src_path.lower().endswith(('.srt', '.smi', '.ssa', '.ass', '.vtt'))):
                    Log.logger.debug("found file:" + event.src_path)
                    size = os.stat(event.src_path).st_size
                    while True:
                        time.sleep(0.5)
                        new_size = os.stat(event.src_path).st_size
                        if (new_size - size == 0):
                            break
                        size = new_size

                    try:
                        Organizer.organize(event.src_path)
                    except Exception as e:
                        Log.logger.debug(e)
                        try:
                            Organizer.organize_ptn(event.src_path)
                        except Exception:
                            Log.logger.error("couldn't move the file" + os.path.basename(event.src_path))
