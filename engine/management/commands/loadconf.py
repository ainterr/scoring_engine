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
    def handle(self, *args, **options):
        call_command('registerplugins')
        for team in config.TEAMS:
            try:
                with transaction.atomic():
                    t, c = models.Team.objects.get_or_create(name=team['name'])
                    t.save()

                    if 'services' not in team or len(team['services']) == 0:
                        raise IntegrityError('Team {} not created: No services configured'.format(team['name']))

                    logger.info('{} Team "{}"'.format('Created' if c else 'Found', t.name))

                    for service in team['services']:
                        try:
                            with transaction.atomic():
                                try:
                                    plugin=models.Plugin.objects.get(name=service['name'])
                                except models.Plugin.DoesNotExist:
                                    raise IntegrityError('Service {} not created: No Plugin configured to score this service (Did you run registerplugins?)'.format(service['name']))

                                s, c = models.Service.objects.get_or_create(
                                    name=service['name'],
                                    ip=service['ip'],
                                    port=service['port'],
                                    team=t,
                                    plugin=plugin
                                )
                                s.save()

                                logger.info('{} Service "{}" for Team "{}"'.format('Created' if c else 'Found', s.name, t.name))
                        except IntegrityError as e:
                            logger.warning(e)
                        except KeyError:
                            logger.warning('Service not created: malformed')

                    if 'credentials' not in team or len(team['credentials']) == 0:
                        raise IntegrityError('Team {} not created: No credentials configured'.format(team['name']))
                    for credential in team['credentials']:
                        try:
                            with transaction.atomic():
                                c, s = models.Credential.objects.get_or_create(
                                    username=credential['username'],
                                    password=credential['password'],
                                    team=t
                                )
                                c.save()

                                if len(credential['services']) == 0:
                                    raise IntegrityError('Credential {}:{} not created: credentials must have at least one service'.format(credential['username'], credential['password']))

                                logger.info('{} Credential "{}:{}" for Team "{}"'.format('Created' if s else 'Found', c.username, c.password, t.name))

                                for service in credential['services']:
                                    try:
                                        services = t.services.filter(name=service)
                                        for s in services:
                                            c.services.add(s)
                                            logger.info('Added Credential "{}:{}" to Team "{}" Service "{}"'.format(c.username, c.password, t.name, s.name))
                                    except models.Service.DoesNotExist:
                                        logger.warning('Credential {}:{} not applied to service {}: service does not exist'.format(credential['username'], credential['password'], service))

                                c.save()
                        except IntegrityError as e:
                            logger.warning(e)
                        except KeyError:
                            logger.warning('Credential not created: malformed')
                            
            except IntegrityError as e:
                logger.warning(e)
            except KeyError:
               logger.error('Team not created: malformed')
