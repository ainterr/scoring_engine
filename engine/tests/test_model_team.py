from django.test import TransactionTestCase
from django.core.exceptions import ValidationError
from .. import models

# TODO: IPv6 tests
import logging
logging.disable(logging.ERROR)

class TeamTests(TransactionTestCase):
    def test_malformed_team(self):
        """Should not be able to create teams with malformed data"""
        # Too little data
        with self.assertRaises(ValidationError):
            models.Team.objects.create()
        with self.assertRaises(ValidationError):
            models.Team.objects.create(name='Team1')
        with self.assertRaises(ValidationError):
            models.Team.objects.create(subnet='192.168.1.0')
        with self.assertRaises(ValidationError):
            models.Team.objects.create(netmask='255.255.255.0')
        with self.assertRaises(ValidationError):
            models.Team.objects.create(
                name='Team1', subnet='192.168.1.0')
        with self.assertRaises(ValidationError):
            models.Team.objects.create(
                name='Team1', netmask='255.255.255.0')
        with self.assertRaises(ValidationError):
            models.Team.objects.create(
                subnet='192.168.1.0', netmask='255.255.255.0')
        # Malformed arguments
        ## Name
        with self.assertRaises(ValidationError): # Name is empty
            models.Team.objects.create(
                name='', subnet='192.168.1.0', netmask='255.255.255.0')
        with self.assertRaises(ValidationError): # Name is None
            models.Team.objects.create(
                name=None, subnet='192.168.1.0', netmask='255.255.255.0')
        with self.assertRaises(ValidationError): # Name is too long
            models.Team.objects.create(
                name='a'*21, subnet='192.168.1.0', netmask='255.255.255.0')
        ## Subnet
        with self.assertRaises(ValidationError): # Subnet is not IP
            models.Team.objects.create(
                name='Team1', subnet='blah', netmask='255.255.255.0')
        with self.assertRaises(ValidationError): # Subnet is invalid IP
            models.Team.objects.create(
                name='Team1', subnet='192.1688.1.0', netmask='255.255.255.0')
        with self.assertRaises(ValidationError): # Subnet is invalid IP
            models.Team.objects.create(
                name='Team1', subnet='192.-168.1.0', netmask='255.255.255.0')
        with self.assertRaises(ValidationError): # Subnet is invalid IP
            models.Team.objects.create(
                name='Team1', subnet='192.168.1', netmask='255.255.255.0')
        with self.assertRaises(ValidationError): # Subnet IP is out of range
            models.Team.objects.create(
                name='Team1', subnet='300.0.1.0', netmask='255.255.255.0')
        with self.assertRaises(ValidationError): # Subnet IP is None
            models.Team.objects.create(
                name='Team1', subnet=None, netmask='255.255.255.0')
        ## Netmask
        with self.assertRaises(ValidationError): # Netmask is not IP
            models.Team.objects.create(
                name='Team1', subnet='192.168.1.0', netmask='what')
        with self.assertRaises(ValidationError): # Netmask is invalid IP
            models.Team.objects.create(
                name='Team1', subnet='192.168.1.0', netmask='255.3255.255.0')
        with self.assertRaises(ValidationError): # Netmask is invalid IP
            models.Team.objects.create(
                name='Team1', subnet='192.168.1.0', netmask='255.255.-255.0')
        with self.assertRaises(ValidationError): # Netmask is invalid IP
            models.Team.objects.create(
                name='Team1', subnet='192.168.1', netmask='255.255.255')
        with self.assertRaises(ValidationError): # Netmask IP is out of range
            models.Team.objects.create(
                name='Team1', subnet='300.0.1.0', netmask='255.450.255.0')
        with self.assertRaises(ValidationError): # Netmask IP is None
            models.Team.objects.create(
                name='Team1', subnet='300.0.1.0', netmask=None)

    def test_team_same_names(self):
        """Teams with the same name are not allowed"""
        models.Team.objects.create(
            name='Team1', subnet='192.168.1.0', netmask='255.255.255.0')
        with self.assertRaises(ValidationError):
            models.Team.objects.create(
                name='Team1', subnet='192.168.2.0', netmask='255.255.255.0')

    def test_team_overlapping_subnet(self):
        """Teams with overlapping subnets are not allowed"""
        models.Team.objects.create(
            name='Team1', subnet='192.168.1.0', netmask='255.255.255.0')
        with self.assertRaises(ValidationError):
            models.Team.objects.create(
                name='Team2', subnet='192.168.1.128', netmask='255.255.255.0')

        models.Team.objects.create(
            name='Team3', subnet='192.168.2.128', netmask='255.255.255.0')
        with self.assertRaises(ValidationError):
            models.Team.objects.create(
                name='Team4', subnet='192.168.2.197', netmask='255.255.255.128')

    def test_team_correct(self):
        """Correctly created teams should be allowed"""
        self.assertEqual(models.Team.objects.count(), 0)
        models.Team.objects.create(
            name='Team1', subnet='192.168.1.0', netmask='255.255.255.0')
        self.assertEqual(models.Team.objects.count(), 1)
        models.Team.objects.create(
            name='Team2', subnet='192.168.2.0', netmask='255.255.255.0')
        self.assertEqual(models.Team.objects.count(), 2)
        # Smaller subnets
        models.Team.objects.create(
            name='Team3', subnet='192.168.3.0', netmask='255.255.255.128')
        self.assertEqual(models.Team.objects.count(), 3)
        models.Team.objects.create(
            name='Team4', subnet='192.168.3.129', netmask='255.255.255.128')
        self.assertEqual(models.Team.objects.count(), 4)

    def test_team_default_credentials(self):
        """New teams should be populated with default credentials
           if they are available"""
        # Creating a new team w/ no default creds set
        self.assertEqual(models.Credential.objects.count(), 0)
        models.Team.objects.create(
            name='Team1', subnet='192.168.1.0', netmask='255.255.255.0')
        self.assertEqual(models.Credential.objects.count(), 0)

        c = models.Credential.objects.create( # Default Credential w/o service
            team=None, default=None, username='test', password='toor')
        self.assertEqual(models.Credential.objects.count(), 2)
        models.Team.objects.create(
            name='Team2', subnet='192.168.2.0', netmask='255.255.255.0')
        self.assertEqual(models.Credential.objects.count(), 3)

    def test_team_malformed_edit(self):
        """Team objects should raise an error when edited with malformed data"""
        t = models.Team.objects.create(
            name='Team1', subnet='192.168.1.0', netmask='255.255.255.0')
         ## Name
        with self.assertRaises(ValidationError): # Name is empty
            t.name = ''
            t.save()
        with self.assertRaises(ValidationError): # Name is None
            t.name = None
            t.save()
        with self.assertRaises(ValidationError): # Name is too long
            t.name = 'a'*21
            t.save()
        ## Subnet
        with self.assertRaises(ValidationError): # Subnet is not IP
            t.subnet = 'blah'
            t.save()
        with self.assertRaises(ValidationError): # Subnet is invalid IP
            t.subnet = '192.1688.1.0'
            t.save()
        with self.assertRaises(ValidationError): # Subnet is invalid IP
            t.subnet = '192.-168.1.0'
            t.save()
        with self.assertRaises(ValidationError): # Subnet is invalid IP
            t.subnet = '192.168.1'
            t.save()
        with self.assertRaises(ValidationError): # Subnet IP is out of range
            t.subnet = '300.0.1.0'
            t.save()
        with self.assertRaises(ValidationError): # Subnet IP is None
            t.subnet = None
            t.save()
        ## Netmask
        with self.assertRaises(ValidationError): # Netmask is not IP
            t.netmask = 'what'
            t.save()
        with self.assertRaises(ValidationError): # Netmask is invalid IP
            t.netmask = '255.3255.255.0'
            t.save()
        with self.assertRaises(ValidationError): # Netmask is invalid IP
            t.netmask = '255.255.-255.0'
            t.save()
        with self.assertRaises(ValidationError): # Netmask is invalid IP
            t.netmask = '255.255.255'
            t.save()
        with self.assertRaises(ValidationError): # Netmask IP is out of range
            t.netmask = '255.450.255.0'
            t.save()
        with self.assertRaises(ValidationError): # Netmask IP is None
            t.netmask = None
            t.save()

    def test_team_edit_same_name(self):
        """Teams with the same name are not allowed, when editing"""
        models.Team.objects.create(
            name='Team1', subnet='192.168.1.0', netmask='255.255.255.0')
        t = models.Team.objects.create(
            name='Team2', subnet='192.168.2.0', netmask='255.255.255.0')
        with self.assertRaises(ValidationError):
            t.name = 'Team1'
            t.save()

    def test_team_edit_overlapping_subnet(self):
        """Teams with overlapping subnets are not allowed"""
        models.Team.objects.create(
            name='Team1', subnet='192.168.1.0', netmask='255.255.255.0')
        t = models.Team.objects.create(
            name='Team2', subnet='192.168.2.0', netmask='255.255.255.0')
        with self.assertRaises(ValidationError):
            t.subnet = '192.168.1.128'
            t.save()

        models.Team.objects.create(
            name='Team3', subnet='192.168.3.0', netmask='255.255.255.128')
        t = models.Team.objects.create(
            name='Team4', subnet='192.168.3.128', netmask='255.255.255.128')
        with self.assertRaises(ValidationError):
            t.netmask = '255.255.255.0'
            t.save()

    def test_team_edit(self):
        """Fields should be properly updated when a team is edited"""
        t = models.Team.objects.create(
            name='Team1', subnet='192.168.1.0', netmask='255.255.255.0')
        
        t.name = 'Team2'
        t.save()
        t = models.Team.objects.get(pk=t.pk) # Reload from DB
        self.assertEqual(t.name, 'Team2')

        t.subnet = '192.168.2.0'
        t.save()
        t = models.Team.objects.get(pk=t.pk) # Reload from DB
        self.assertEqual(t.subnet, '192.168.2.0')

        t.netmask = '255.255.255.128'
        t.save()
        t = models.Team.objects.get(pk=t.pk) # Reload from DB
        self.assertEqual(t.netmask, '255.255.255.128')
