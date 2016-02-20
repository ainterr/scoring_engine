from threading import Thread, Event
from time import sleep
import pkgutil

import settings
import plugins

PLUGINS = []

def get_plugins():
    modules = []

    for loader, name, ispkg in pkgutil.walk_packages(path=plugins.__path__,
        prefix=plugins.__name__+'.',
        onerror=lambda x: None):
        
        module = loader.find_module(name).load_module(name)
        modules.append(module)

    return modules

def poll():
    global PLUGINS

    for plugin in PLUGINS:
        plugin.run()

class PollingThread(Thread):
    def __init__(self, interval):
        Thread.__init__(self)
        self.stop_event = Event()
        self.interval = interval

    def stop(self):
        if self.isAlive() == True:
            self.stop_event.set()
            self.join()

    def run(self):
        while not self.stop_event.is_set():
            poll()

            count = 0
            while count < self.interval:
                if self.stop_event.is_set(): break
                sleep(1)
                count += 1

def async():
    return PollingThread(settings.POLL_INTERVAL)

PLUGINS = get_plugins()
