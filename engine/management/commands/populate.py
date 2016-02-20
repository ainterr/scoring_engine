from django.core.management.base import BaseCommand, CommandError
from engine import models

import random

class Command(BaseCommand):
    help = 'A TEMPORARY command for populating the database with dummy data for dev purposes'
    
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        team = models.Team(name='NUCCDC')
        team.save()

        credential = models.Credential(username='joe', password='Sup3rSecret!', team=team)
        credential.save()
        
        plugin_http = models.Plugin(name='http')
        plugin_http.save()
        plugin_https = models.Plugin(name='https')
        plugin_https.save()
        
        service_http = models.Service(
            name='http', 
            ip='10.0.0.100', 
            port='80', 
            team=team, 
            plugin=plugin_http
        )
        service_http.save()
        service_https = models.Service(
            name='https', 
            ip='10.0.0.100', 
            port='443', 
            team=team, 
            plugin=plugin_https
        )
        service_https.save()
        
        for i in range(100):
            result = models.Result(
                status=bool(random.getrandbits(1)),
                team=team, 
                service=service_http, 
                plugin=plugin_http
            )
            result.save()
        
            result = models.Result(
                status=bool(random.getrandbits(1)),
                team=team, 
                service=service_https, 
                plugin=plugin_https
            )
            result.save()
