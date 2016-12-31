from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, IntegrityError
from django.core.management import call_command

from engine import models, config

import random

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run an initial database configuration based on /engine/config.py'
    
    def add_arguments(self, parser):
        pass

    @transaction.atomic
    def create_services(self):
        for service in config.SERVICES:
            try:
               with transaction.atomic():
                   try:
                       plugin=models.Plugin.objects.get(name=service['plugin'])
                   except models.Plugin.DoesNotExist:
                       raise IntegrityError('Service {} not created: No Plugin configured to score this service (Did you run registerplugins?)'.format(service['name']))

                   s, c = models.Service.objects.get_or_create(
                       name=service['name'],
                       subnet_host=service['subnet_host'],
                       port=service['port'],
                       plugin=plugin
                   )
                   s.save()

                   logger.info('{} Service "{}"'.format('Created' if c else 'Found', s.name))
            except IntegrityError as e:
                logger.warning(e)
            except KeyError:
                logger.warning('Service not created: malformed')


    @transaction.atomic
    def create_default_credentials(self):
        for credential in config.DEFAULT_CREDS:
            try:
                with transaction.atomic():
                    c, s = models.Credential.objects.get_or_create(
                        username=credential['username'],
                        password=credential['password'],
                        team=None,
                        default=None
                    )
                    c.save()

                    if len(credential['services']) == 0:
                        raise IntegrityError('Credential {}:{} not created: credentials must have at least one service'.format(credential['username'], credential['password']))

                    logger.info('{} Default Credential "{}:{}"'.format('Created' if s else 'Found', c.username, c.password))

                    for service in credential['services']:
                        try:
                            service = models.Service.objects.get(name=service)
                            c.services.add(service)
                            logger.info('Added Default Credential "{}:{}" to Service "{}"'.format(c.username, c.password, service.name))
                        except models.Service.DoesNotExist:
                            logger.warning('Credential {}:{} not applied to service {}: service does not exist'.format(credential['username'], credential['password'], service))

                    c.save()
            except IntegrityError as e:
                logger.warning(e)
            except KeyError:
                logger.warning('Credential not created: malformed')


    @transaction.atomic
    def create_teams(self):
        for team in config.TEAMS:
            try:
                with transaction.atomic():
                    t, c = models.Team.objects.get_or_create(
                        name=team['name'],
                        subnet=team['subnet'],
                        netmask=team['netmask'])
                    t.save()

                    logger.info('{} Team "{}"'.format('Created' if c else 'Found', t.name))
            except IntegrityError as e:
                logger.warning(e)
            except KeyError:
               logger.error('Team not created: malformed')


    @transaction.atomic
    def handle(self, *args, **options):
        call_command('registerplugins')
        self.create_services()
        self.create_default_credentials()
        self.create_teams()
