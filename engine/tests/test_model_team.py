from django.test import TransactionTestCase
from django.core.exceptions import ValidationError
from .. import models

# TODO: IPv6 tests

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

        models.Credential.objects.create( # Default Credential w/o service
            team=None, default=True, username='test', password='toor')
        self.assertEqual(models.Credential.objects.count(), 2)
        models.Team.objects.create(
            name='Team2', subnet='192.168.2.0', netmask='255.255.255.0')
        self.assertEqual(models.Credential.objects.count(), 3)
