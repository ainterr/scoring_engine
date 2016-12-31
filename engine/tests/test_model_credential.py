from django.core.management import call_command
from django.test import TransactionTestCase
from django.core.exceptions import ValidationError
from .. import models

class CredentialTests(TransactionTestCase):
    def setUp(self):
        call_command('registerplugins')
        self.http = models.Plugin.objects.get(name='http')
        self.smb = models.Plugin.objects.get(name='smb')
        self.service1 = models.Service.objects.create(
            name='Service1', subnet_host=1, port=80, plugin=self.http)
        self.service2 = models.Service.objects.create(
            name='Service2', subnet_host=2, port=38, plugin=self.smb)
        self.team1 = models.Team.objects.create(
            name='Team1', subnet='192.168.1.0', netmask='255.255.255.0')
        self.team2 = models.Team.objects.create(
            name='Team2', subnet='192.168.2.0', netmask='255.255.255.0')

    def test_malformed_credential(self):
        """Should not be able to create credentials with malformed data"""
        # Too little data
        with self.assertRaises(ValidationError):
            models.Credential.objects.create()
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(team=None)
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(default=None)
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(username='tom')
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(password='test')
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(team=None, default=None)
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(team=None, username='tom')
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(team=None, password='toor')
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(default=None, username='john')
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(default=None, password='john')
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(
                team=None, default=None, username='john')
        with self.assertRaises(ValidationError):
            models.Credential.objects.create(
                team=None, default=None, password='john')

        # Malformed arguments
        ## Team
        with self.assertRaises(ValueError): # Team is not a model or None
            models.Credential.objects.create(
                team='Team1', default=None, username='tom', password='john')
        ## Default
        with self.assertRaises(ValueError): # Default is not a Credential
            models.Credential.objects.create(
                team=None, default=5, username='tom', password='john')
        # Username
        with self.assertRaises(ValidationError): # Username is None
            models.Credential.objects.create(
                team=None, default=None, username=None, password='john')
        with self.assertRaises(ValidationError): # Username is empty string
            models.Credential.objects.create(
                team=None, default=None, username='', password='john')
        with self.assertRaises(ValidationError): # Username is too long
            models.Credential.objects.create(
                team=None, default=None, username='a'*21, password='john')
        # Password
        with self.assertRaises(ValidationError): # Password is None
            models.Credential.objects.create(
                team=None, default=None, username='tom', password=None)
        with self.assertRaises(ValidationError): # Password is empty string
            models.Credential.objects.create(
                team=None, default=None, username='tom', password='')
        with self.assertRaises(ValidationError): # Password is too long
            models.Credential.objects.create(
                team=None, default=None, username='tom', password='b'*41)

    def test_credentials_correct(self):
        """Credentials with the correct arguments are allowed"""
        self.assertEqual(models.Credential.objects.count(), 0)
        models.Credential.objects.create(
            team=self.team1, default=None, username='what', password='krit')
        self.assertEqual(models.Credential.objects.count(), 1)
        models.Credential.objects.create(
            team=self.team2, default=None, username='kdls', password='kdl')
        self.assertEqual(models.Credential.objects.count(), 2)
        models.Credential.objects.create(
            team=None, default=None, username='test', password='toor')
        self.assertEqual(models.Credential.objects.count(), 5)
        # With services
        models.Credential.objects.create(
            team=self.team1, default=None, username='lol', password='what',
            services=[self.service1])
        self.assertEqual(models.Credential.objects.count(), 6)
        models.Credential.objects.create(
            team=None, default=None, username='john', password='lkf',
            services=[self.service1, self.service2])
        self.assertEqual(models.Credential.objects.count(), 9)
        
    def test_credential_services(self):
        """Credential services should be properly assigned when created"""
        c = models.Credential.objects.create(
            team=self.team1, default=None, username='lol', password='what',
            services=[self.service1])
        self.assertEqual(models.Credential.objects.count(), 1)
        self.assertEqual(list(c.services.all()), [self.service1])

        c = models.Credential.objects.create(
            team=None, default=None, username='john', password='lkf',
            services=[self.service1, self.service2])
        self.assertEqual(models.Credential.objects.count(), 4)
        self.assertEqual(list(c.services.all()), [self.service1, self.service2])
        self.assertEqual(c.assoc_creds.count(), 2)
        for cred in c.assoc_creds.all():
            self.assertEqual(list(cred.services.all()),
                             [self.service1, self.service2])

    def test_default_credentials_populate_teams(self):
        """When a default credential is added, copies are populated to
           all teams"""
        self.assertEqual(models.Credential.objects.count(), 0)
        c = models.Credential.objects.create(
            team=None, default=None, username='test', password='toor')
        self.assertEqual(models.Credential.objects.count(), 3)
        self.assertEqual(c.assoc_creds.count(), 2)
        for cred in c.assoc_creds.all():
            self.assertEqual(cred.default, c)
 
    def test_default_credential_delete_cascade(self):
        """When a default credential is deleted, its associated
           credentials are also deleted"""
        cred = models.Credential.objects.create(
            team=None, default=None, username='test', password='toor')
        self.assertEqual(models.Credential.objects.count(), 3)
        cred.delete()
        self.assertEqual(models.Credential.objects.count(), 0)

    def test_team_delete_cascade(self):
        """When a team is deleted, its associated
           credentials are also deleted"""
        models.Credential.objects.create(
            team=self.team1, default=None, username='test', password='toor')
        models.Credential.objects.create(
            team=self.team1, default=None, username='what', password='toor')
        self.assertEqual(models.Credential.objects.count(), 2)
        self.team1.delete()
        self.assertEqual(models.Credential.objects.count(), 0)

    def test_credential_malformed_edit(self):
        """Credentials should raise errors when edited with malformed data"""
        c = models.Credential.objects.create(
            team=self.team1, default=None, username='what', password='ever',
            services=[self.service1])

        ## Team
        with self.assertRaises(ValueError): # Team is not a model or None
            c.team = 'Team1'
            c.save()
        ## Default
        with self.assertRaises(ValueError): # Default is not a Credential
            c.default = 5
            c.save()
        # Username
        with self.assertRaises(ValidationError): # Username is None
            c.username = None
            c.save()
        with self.assertRaises(ValidationError): # Username is empty string
            c.username = ''
            c.save()
        with self.assertRaises(ValidationError): # Username is too long
            c.username = 'a'*21
            c.save()
        # Password
        with self.assertRaises(ValidationError): # Password is None
            c.password = None
            c.save()
        with self.assertRaises(ValidationError): # Password is empty string
            c.password = ''
            c.save()
        with self.assertRaises(ValidationError): # Password is too long
            c.password = 'b'*41
            c.save()

    def test_credential_edit(self):
        """Credentials should be properly updated when edited"""
        c = models.Credential.objects.create(
            team=self.team1, default=None, username='what', password='ever',
            services=[self.service1])
        c.team = self.team2
        c.save()
        c = models.Credential.objects.get(pk=c.pk) # Reload from DB
        self.assertEqual(c.team, self.team2)

        c.username='blah'
        c.save()
        c = models.Credential.objects.get(pk=c.pk) # Reload from DB
        self.assertEqual(c.username, 'blah')

        c.password='blop'
        c.save()
        c = models.Credential.objects.get(pk=c.pk) # Reload from DB
        self.assertEqual(c.password, 'blop')

        c.services=[self.service1, self.service2]
        c.save()
        c = models.Credential.objects.get(pk=c.pk) # Reload from DB
        self.assertEqual(list(c.services.all()), [self.service1, self.service2])

        c.services=[]
        c.save()
        c = models.Credential.objects.get(pk=c.pk) # Reload from DB
        self.assertEqual(list(c.services.all()), [])

        def_cred = models.Credential.objects.create(
            team=None, default=None, username='blah', password='blop',
            services=[])
        c.default=def_cred
        c.save()
        c = models.Credential.objects.get(pk=c.pk) # Reload from DB
        self.assertEqual(c.default, def_cred)
        self.assertIn(c, def_cred.assoc_creds.all())

    def test_default_cred_edit_propagation(self):
        """When default credentials are edited, its associated credentials
           should also be updated"""
        def_cred = models.Credential.objects.create(
            team=None, default=None, username='test', password='toor',
            services=[self.service1])

        def_cred.username = 'what'
        def_cred.save()
        for c in def_cred.assoc_creds.all():
            self.assertEqual(c.username, 'what')

        def_cred.password = 'blah'
        def_cred.save()
        for c in def_cred.assoc_creds.all():
            self.assertEqual(c.password, 'blah')

        def_cred.services = [self.service1, self.service2]
        def_cred.save()
        for c in def_cred.assoc_creds.all():
            self.assertEqual(list(c.services.all()),
                             [self.service1, self.service2])

        def_cred.services = []
        def_cred.save()
        for c in def_cred.assoc_creds.all():
            self.assertEqual(list(c.services.all()), [])

    def test_edit_cred_remove_default(self):
        """When a credential associated with a default credential is edited,
           its default field is set to NULL"""
        models.Team.objects.create(
            name='Team3', subnet='192.168.3.0', netmask='255.255.255.0')

        def_cred = models.Credential.objects.create(
            team=None, default=None, username='test', password='toor',
            services=[self.service1])
        self.assertEqual(def_cred.assoc_creds.count(), 3)

        assoc = list(def_cred.assoc_creds.all())
        assoc[0].username = 'what'
        assoc[0].save()
        self.assertEqual(def_cred.username, 'test')
        self.assertEqual(assoc[0].username, 'what')
        self.assertIs(assoc[0].default, None)
        self.assertEqual(def_cred.assoc_creds.count(), 2)
        
        assoc[1].password = 'ever'
        assoc[1].save()
        self.assertEqual(def_cred.password, 'toor')
        self.assertEqual(assoc[1].password, 'ever')
        self.assertIs(assoc[1].default, None)
        self.assertEqual(def_cred.assoc_creds.count(), 1)

        assoc[2].services = [self.service1, self.service2]
        assoc[2].save()
        self.assertEqual(list(def_cred.services.all()), [self.service1])
        self.assertEqual(list(assoc[2].services.all()),
                         [self.service1, self.service2])
        self.assertIs(assoc[2].default, None)
        self.assertEqual(def_cred.assoc_creds.count(), 0)
