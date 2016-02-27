from django.core.management.base import BaseCommand, CommandError
from engine import models, config

import random

class Command(BaseCommand):
    help = 'Run an initial database configuration based on /engine/config.py. You should run registerplugins prior to running this command'
    
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # TODO error handling - this is very fragile
        for team in config.TEAMS:
            t = models.Team(name=team['name'])
            t.save()

            for service in team['services']:
                s = models.Service(
                    name=service['name'],
                    ip=service['ip'],
                    port=service['port'],
                    team=t,
                    plugin=models.Plugin.objects.get(name=service['name'])
                )
                s.save()

            for credential in team['credentials']:
                c = models.Credential(
                    username=credential['username'],
                    password=credential['password'],
                    team=t
                )
                c.save()

                for service in credential['services']:
                    try:
                        c.services.add(t.services.get(name=service))
                    except models.Service.DoesNotExist:
                        continue

                c.save()
