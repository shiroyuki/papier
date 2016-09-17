import logging
import time

from imagination.debug import get_logger
from watchdog.events   import FileSystemEventHandler

log = get_logger('watcher', level = logging.DEBUG)


class FSEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print(event)

    def on_created(self, event):
        pass

    def on_deleted(self, event):
        pass

    def on_modified(self, event):
        pass

    def on_moved(self, event):
        pass


class LiveUpdateService(object):
    def __init__(self, observer, handler):
        self.observer = observer
        self.handler  = handler

    def watch(self, path):
        self.observer.schedule(self.handler, path, recursive = True)
        log.debug('Will observe {}'.format(path))

    def start(self):
        self.observer.start()

    def stop(self):
        self.observer.stop()

    def join(self):
        self.observer.join()

    def run_blocking_observation(self):
        self.start()

        log.debug('Started the file watcher')

        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            log.debug('Stoping the file watcher')
            self.stop()

        self.join()
        log.debug('Stopped the file watcher')
