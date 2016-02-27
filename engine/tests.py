from django.test import TestCase
from django.core.management import call_command

from . import models, config

import logging
logging.disable(logging.ERROR)

class ManagementTests(TestCase):
    def test_registerplugins_registers_plugins(self):
        """
        registerplugins should add new plugins to the DB
        """
        call_command('registerplugins')

        num_plugins = models.Plugin.objects.count()
        self.assertNotEqual(num_plugins, 0)

    def test_registerplugins_doesnt_recreate_plugins(self):
        """
        registerplugins should not add plugins twice
        """
        call_command('registerplugins')
        num_plugins_before = models.Plugin.objects.count()
        call_command('registerplugins')
        num_plugins_after = models.Plugin.objects.count()

        self.assertEqual(num_plugins_before, num_plugins_after)

    def test_configure_team_no_services(self):
        """
        configure should not create a team if it has no services configured.
        """

        call_command('registerplugins')

        config.TEAMS = [
            {
                'name': 'Team 1',
                'services': [],
                'credentials': [
                    { 'username':'joe', 'password':'test', 'services':['http'] }
                ]
            }
        ]

        call_command('configure')

        self.assertEqual(models.Team.objects.count(), 0)

    def test_configure_team_no_credentials(self):
        """
        configure should not create a team if it has no credentials configured.
        """

        call_command('registerplugins')

        config.TEAMS = [
            {
                'name': 'Team 1',
                'services': [
                    { 'name':'http', 'ip':'10.0.0.100', 'port':80 },
                ],
                'credentials': []
            }
        ]

        call_command('configure')

        self.assertEqual(models.Team.objects.count(), 0)

    def test_configure_malformed_team(self):
        """
        configure should not create a malformed team.
        """

        call_command('registerplugins')

        config.TEAMS = [
            {
                'blah': 'Team 1',
            },
        ]

        call_command('configure')

        team_count = models.Team.objects.count()

        self.assertEqual(team_count, 0)

    def test_configure_team_no_plugin_found_for_service(self):
        """
        configure should not create a service (but should create a team) if it doesn't have a plugin to score a service.
        """

        call_command('registerplugins')

        config.TEAMS = [
            {
                'name': 'Team 1',
                'services': [
                    { 'name':'test', 'ip':'10.0.0.100', 'port':80 },
                ],
                'credentials': [
                    { 'username':'joe', 'password':'test', 'services':['http'] }
                ]
            }
        ]

        call_command('configure')

        team_count = models.Team.objects.count()
        service_count = models.Service.objects.count()

        self.assertEqual(team_count, 1)
        self.assertEqual(service_count, 0)

    def test_configure_team_no_duplicate_teams(self):
        """
        configure should not create another team if the team has already been created.
        """

        call_command('registerplugins')

        config.TEAMS = [
            {
                'name': 'Team 1',
                'services': [
                    { 'name':'http', 'ip':'10.0.0.100', 'port':80 },
                ],
                'credentials': [
                    { 'username':'joe', 'password':'test', 'services':['http'] }
                ]
            },
            {
                'name': 'Team 1',
                'services': [
                    { 'name':'https', 'ip':'10.0.0.100', 'port':80 },
                ],
                'credentials': [
                    { 'username':'joe', 'password':'test', 'services':['https'] }
                ]
            }
        ]

        call_command('configure')

        team_count = models.Team.objects.count()

        self.assertEqual(team_count, 1)

    def test_configure_team_no_duplicate_services(self):
        """
        configure should not create another service if the service has already been created.
        """

        call_command('registerplugins')

        config.TEAMS = [
            {
                'name': 'Team 1',
                'services': [
                    { 'name':'http', 'ip':'10.0.0.100', 'port':80 },
                    { 'name':'http', 'ip':'10.0.0.100', 'port':80 },
                ],
                'credentials': [
                    { 'username':'joe', 'password':'test', 'services':['http'] }
                ]
            },
        ]

        call_command('configure')

        service_count = models.Service.objects.count()

        self.assertEqual(service_count, 1)

    def test_configure_team_duplicate_service_names(self):
        """
        configure should be able to create services with matching names.
        """

        call_command('registerplugins')

        config.TEAMS = [
            {
                'name': 'Team 1',
                'services': [
                    { 'name':'http', 'ip':'10.0.0.100', 'port':80 },
                    { 'name':'http', 'ip':'10.0.0.123', 'port':8080 },
                ],
                'credentials': [
                    { 'username':'joe', 'password':'test', 'services':['http'] }
                ]
            },
        ]

        call_command('configure')

        service_count = models.Service.objects.count()

        self.assertEqual(service_count, 2)

    def test_configure_team_malformed_service(self):
        """
        configure should not create a malformed service but should create the
        parent team.
        """

        call_command('registerplugins')

        config.TEAMS = [
            {
                'name': 'Team 1',
                'services': [
                    { 'name':'http' },
                ],
                'credentials': [
                    { 'username':'joe', 'password':'test', 'services':['http'] }
                ]
            },
        ]

        call_command('configure')

        service_count = models.Service.objects.count()
        team_count = models.Team.objects.count()

        self.assertEqual(service_count, 0)
        self.assertEqual(team_count, 1)

    def test_configure_team_malformed_credential(self):
        """
        configure should not create a malformed credential but should create the
        parent team.
        """

        call_command('registerplugins')

        config.TEAMS = [
            {
                'name': 'Team 1',
                'services': [
                    { 'name':'http', 'ip':'10.0.0.100', 'port':80 },
                ],
                'credentials': [
                    { 'blah':'joe' }
                ]
            },
        ]

        call_command('configure')

        credential_count = models.Credential.objects.count()

        self.assertEqual(credential_count, 0)

    def test_configure_team_duplicate_credential(self):
        """
        configure should not create duplicate credentials.
        """

        call_command('registerplugins')

        config.TEAMS = [
            {
                'name': 'Team 1',
                'services': [
                    { 'name':'http', 'ip':'10.0.0.100', 'port':80 },
                ],
                'credentials': [
                    { 'username':'joe', 'password':'test', 'services':['http'] },
                    { 'username':'joe', 'password':'test', 'services':['http'] }
                ]
            },
        ]

        call_command('configure')

        credential_count = models.Credential.objects.count()

        self.assertEqual(credential_count, 1)

    def test_configure_team_duplicate_credential_no_duplicate_m2ms(self):
        """
        configure should not create multiple many to many relationships for
        duplicate service to credential mappings.
        """

        call_command('registerplugins')

        config.TEAMS = [
            {
                'name': 'Team 1',
                'services': [
                    { 'name':'http', 'ip':'10.0.0.100', 'port':80 },
                ],
                'credentials': [
                    { 'username':'joe', 'password':'test', 'services':['http'] },
                    { 'username':'joe', 'password':'test', 'services':['http'] }
                ]
            },
        ]

        call_command('configure')

        credential = models.Credential.objects.first()
        service_count = credential.services.count()

        self.assertEqual(service_count, 1)

    def test_configure_team_credential_invalid_service_valid_plugin(self):
        """
        configure should not create a service mapping if the service does not
        exist for a credential (even if the plugin exists).
        """

        call_command('registerplugins')

        config.TEAMS = [
            {
                'name': 'Team 1',
                'services': [
                    { 'name':'http', 'ip':'10.0.0.100', 'port':80 },
                ],
                'credentials': [
                    { 'username':'joe', 'password':'test', 'services':['https'] },
                ]
            },
        ]

        call_command('configure')

        credential = models.Credential.objects.first()
        service_count = credential.services.count()

        self.assertEqual(service_count, 0)
