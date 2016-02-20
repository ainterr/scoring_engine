from threading import Thread, Event
from time import sleep
import pkgutil

import models, settings, plugins

PLUGINS = {}

def get_plugins():
    modules = {}

    for loader, name, ispkg in pkgutil.walk_packages(path=plugins.__path__,
        prefix=plugins.__name__+'.',
        onerror=lambda x: None):
        
        module = loader.find_module(name).load_module(name)
        modules[name.split('.')[-1]] = module

    return modules

def poll():
    global PLUGINS

    for team in models.Team.objects.all():
        credential = team.credentials.order_by('?').first()

        for service in team.services.all():
            options = {}
            options['ip'] = service.ip
            options['port'] = service.port
            options['username'] = credential.username
            options['password'] = credential.password

            try: plugin = PLUGINS[service.plugin.name]
            except KeyError:
                print('Error: no module found for configured plugin: {}'.format(service.plugin.name))
                continue
                
            success = plugin.run(options)

            models.Result(
                team=team, 
                service=service, 
                plugin=service.plugin, 
                status=success
            ).save()

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
