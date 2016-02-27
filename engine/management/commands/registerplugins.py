from django.core.management.base import BaseCommand, CommandError

from engine import models, poller

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'This generates database models for the newly added plugins. It should be run every time plugins are changed'
    
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for plugin in poller.PLUGINS:
            matches = models.Plugin.objects.filter(name=plugin)

            if matches.count() == 0:
                models.Plugin(name=plugin).save()
                logger.info('Registered plugin {}'.format(plugin))
            else:
                logger.info('Plugin {} already registered'.format(plugin))
