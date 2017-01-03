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

        config.SERVICES = [
            {
                'name': 'service1',
                'subnet_host': 28,
                'port': 890,
                'plugin':'test'
            }
        ]

        call_command('configure')

        service_count = models.Service.objects.count()

        self.assertEqual(service_count, 0)

    def test_configure_team_no_duplicate_teams(self):
        """
        configure should not create another team if the team has already been created.
        """

        call_command('registerplugins')

        config.TEAMS = [
            {
                'name': 'Team 1',
                'subnet':'192.168.1.0',
                'netmask':'255.255.255.0'
            },
            {
                'name': 'Team 1',
                'subnet':'192.168.1.0',
                'netmask':'255.255.255.0'
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

        config.SERVICES = [
            { 'name':'http', 'subnet_host':'100', 'port':80, 'plugin':'http' },
            { 'name':'http', 'subnet_host':'100', 'port':80, 'plugin':'http' },
        ]

        call_command('configure')

        service_count = models.Service.objects.count()

        self.assertEqual(service_count, 1)

    def test_configure_team_duplicate_service_names(self):
        """
        configure should be able to create services with matching names.
        """

        call_command('registerplugins')

        config.SERVICES = [
            { 'name':'http', 'subnet_host':'100', 'port':80, 'plugin':'http' },
            { 'name':'http', 'subnet_host':'123', 'port':8080, 'plugin':'http' },
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

        config.SERVICES = [
            { 'name':'http' },
        ]

        call_command('configure')

        service_count = models.Service.objects.count()

        self.assertEqual(service_count, 0)

    def test_configure_team_malformed_credential(self):
        """
        configure should not create a malformed credential but should create the
        parent team.
        """

        call_command('registerplugins')

        config.DEFAULT_CREDS = [
            { 'blah':'joe' }
        ]

        call_command('configure')

        credential_count = models.Credential.objects.count()

        self.assertEqual(credential_count, 0)

    def test_configure_team_duplicate_credential(self):
        """
        configure should not create duplicate credentials.
        """

        call_command('registerplugins')

        config.SERVICES = [
            { 'name':'http', 'subnet_host':'100', 'port':80, 'plugin':'http' }
        ]
        config.DEFAULT_CREDS = [
            { 'username':'joe', 'password':'test', 'services':['http'] },
            { 'username':'joe', 'password':'test', 'services':['http'] }
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

        config.SERVICES = [
            { 'name':'http', 'subnet_host':'100', 'port':80, 'plugin':'http' }
        ]
        config.DEFAULT_CREDS = [
            { 'username':'joe', 'password':'test', 'services':['http'] },
            { 'username':'joe', 'password':'test', 'services':['http'] }
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

        config.SERVICES = [
            { 'name':'http', 'subnet_host':'100', 'port':80, 'plugin':'http' }
        ]
        config.DEFAULT_CREDS = [
            { 'username':'joe', 'password':'test', 'services':['https'] },
        ]

        call_command('configure')

        credential = models.Credential.objects.first()
        service_count = credential.services.count()

        self.assertEqual(service_count, 0)

class ModelsTests(TestCase):
    def setup_db(self):
        t = models.Team(name='test', subnet='192.168.1.0', netmask='255.255.255.0')
        t.save()
        p = models.Plugin(name='http')
        p.save()
        s = models.Service(name='svc', subnet_host='1', port='80', plugin=p)
        s.save()
        c = models.Credential(username='user', password='password', team=t)
        c.save()
        r = models.Result(status=True, plugin=p, team=t, service=s)
        r.save()

    def get_counts(self):
        t = models.Team.objects.count()
        s = models.Service.objects.count()
        r = models.Result.objects.count()
        c = models.Credential.objects.count()
        p = models.Plugin.objects.count()

        return t, s, r, c, p

    def test_team_delete_removes_services_results_credentials_and_users(self):
        """
        deleting a team should delete it's services, results, credentias, and
        users from the database but not plugins.
        """
        self.setup_db()

        t = models.Team.objects.first()
        t.delete()

        t, s, r, c, p = self.get_counts()

        self.assertEqual(t, 0)
        self.assertEqual(s, 0)
        self.assertEqual(r, 0)
        self.assertEqual(c, 0)
        self.assertEqual(p, 1)

    def test_plugin_delete_removes_services_and_results(self):
        """
        deleting a plugin should delete it's corresponding services and results
        but not the team or it's credentials.
        """
        self.setup_db()

        p = models.Plugin.objects.first()
        p.delete()

        t, s, r, c, p = self.get_counts()

        self.assertEqual(t, 1)
        self.assertEqual(s, 0)
        self.assertEqual(r, 0)
        self.assertEqual(c, 1)
        self.assertEqual(p, 0)

    def test_service_delete_removes_results(self):
        """
        deleting a plugin should delete it's corresponding services and results
        but not the team or it's credentials.
        """
        self.setup_db()

        s = models.Service.objects.first()
        s.delete()

        t, s, r, c, p = self.get_counts()

        self.assertEqual(t, 1)
        self.assertEqual(s, 0)
        self.assertEqual(r, 0)
        self.assertEqual(c, 1)
        self.assertEqual(p, 1)
