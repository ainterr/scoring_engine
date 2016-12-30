from django.core.management import call_command
from django.test import TransactionTestCase
from django.core.exceptions import ValidationError
from .. import models

class CredentialTests(TransactionTestCase):
    def setUp(self):
        call_command('registerplugins')
        self.http = models.Plugin.objects.get(name='http')
        self.smb = models.Plugin.objects.get(name='smb')

    def test_malformed_credential(self):
        """Should not be able to create credentials with malformed data"""
        # Too little data
        with self.assertRaises(ValidationError):
            models.Credential.objects.create()
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(team=None)
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(default=True)
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(username='tom')
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(password='test')
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(team=None, default=True)
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(team=None, username='tom')
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(team=None, password='toor')
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(default=False, username='john')
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(default=False, password='john')
        with self.assertRaises(ValidationError): # Default missing, integrity
            models.Credential.objects.create(username='john', password='john')
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(
                team=None, default=False, username='john')
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(
                team=None, default=False, password='john')
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(
                team=None, username='tom', password='john')

        # Malformed arguments
        ## Team
        with self.assertRaises(ValueError): # Team is not a model or None
            models.Credential.objects.create(
                team='Team1', default=True, username='tom', password='john')
        ## Default
        with self.assertRaises(ValidationError): # Default is None
            models.Credential.objects.create(
                team=None, default=None, username='tom', password='john')
        with self.assertRaises(ValidationError): # Default is not a boolean
            models.Credential.objects.create(
                team=None, default=5, username='tom', password='john')
        # Username
        with self.assertRaises(ValidationError): # Username is None
            models.Credential.objects.create(
                team=None, default=True, username=None, password='john')
        with self.assertRaises(ValidationError): # Username is empty string
            models.Credential.objects.create(
                team=None, default=True, username='', password='john')
        with self.assertRaises(ValidationError): # Username is too long
            models.Credential.objects.create(
                team=None, default=True, username='a'*21, password='john')
        # Password
        with self.assertRaises(ValidationError): # Password is None
            models.Credential.objects.create(
                team=None, default=True, username='tom', password=None)
        with self.assertRaises(ValidationError): # Password is empty string
            models.Credential.objects.create(
                team=None, default=True, username='tom', password='')
        with self.assertRaises(ValidationError): # Password is too long
            models.Credential.objects.create(
                team=None, default=True, username='tom', password='b'*41)

# TODO Finish writing tests
