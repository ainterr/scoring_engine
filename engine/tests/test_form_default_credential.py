from django.core.management import call_command
from django.test import TransactionTestCase
from django.core.exceptions import ValidationError
from .. import models, forms

import logging
logging.disable(logging.ERROR)

class DefaultCredentialFormTests(TransactionTestCase):
    form_class = forms.DefaultCredentialForm

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

    def test_malformed_default_credential_form(self):
        """Should not be able to create default credentials with malformed data
           through forms"""
        # Too little data
        data = {}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This field is required.'])
 
        data = {'username':'tom'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'], ['This field is required.'])

        data = {'password':'test'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This field is required.'])

        data = {'username':'tom', 'password':'test'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['services'], ['This field is required.'])

        # Malformed arguments
        # Username
        data = {'username':None, 'password':'test'} # Username is None
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This field is required.'])

        data = {'username':'', 'password':'test'} # Username is empty string
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This field is required.'])

        data = {'username':'a'*21, 'password':'test'} # Username is too long
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'],
            ['Ensure this value has at most 20 characters (it has 21).'])

        # Password
        data = {'username':'tom', 'password':None} # Password is None
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'], ['This field is required.'])

        data = {'username':'tom', 'password':''} # Password is empty string
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'], ['This field is required.'])

        data = {'username':'tom', 'password':'a'*41} # Password is too long
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'],
            ['Ensure this value has at most 40 characters (it has 41).'])

        # Services
        data = {'username':'tom', 'password':'test', 'services':None}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['services'], ['This field is required.'])

        data = {'username':'tom', 'password':'test', 'services':'http'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['services'], ['Enter a list of values.'])

        data = {'username':'tom', 'password':'test', 'services':[]}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['services'], ['This field is required.'])

    def test_default_credentials_correct_form(self):
        """Default credentials with the correct arguments are
           allowed in forms"""
        # With services
        data = {'username':'lol', 'password':'what', 'services':[self.service1]}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(models.Credential.objects.count(), 3)

        data = {'username':'j'*20, 'password':'l'*40,
                'services':[self.service1, self.service2]}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(models.Credential.objects.count(), 6)
        
    def test_default_credential_services_form(self):
        """Default credential services should be properly assigned when created
           through forms"""
        data = {'username':'lol', 'password':'what', 'services':[self.service1]}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        c = form.save()
        self.assertEqual(models.Credential.objects.count(), 3)
        self.assertEqual(set(c.services.all()), set([self.service1]))

        self.assertEqual(c.assoc_creds.count(), 2)
        for cred in c.assoc_creds.all():
            self.assertEqual(set(cred.services.all()),
                             set([self.service1]))

    def test_default_credential_forms_populate_teams(self):
        """When a default credential is added through a form,
           copies are populated to all teams"""
        self.assertEqual(models.Credential.objects.count(), 0)
        data = {'username':'test', 'password':'toor',
                'services':[self.service1]}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        c = form.save()
        self.assertEqual(models.Credential.objects.count(), 3)
        self.assertEqual(c.assoc_creds.count(), 2)
        for cred in c.assoc_creds.all():
            self.assertEqual(cred.default, c)
 
    def test_default_credential_form_malformed_edit(self):
        """Default credentials should raise errors when edited through a form 
           with malformed data"""
        c = models.Credential.objects.create(
            team=None, default=None, username='what', password='ever',
            services=[self.service1])
        data = {'username':'what', 'password':'ever',
                'services':[self.service1]}

        # Username
        data['username'] = None
        form = self.form_class(data, instance=c)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This field is required.'])

        data['username'] = ''
        form = self.form_class(data, instance=c)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This field is required.'])

        data['username'] = 'a'*21
        form = self.form_class(data, instance=c)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'],
            ['Ensure this value has at most 20 characters (it has 21).'])

        # Password
        data['password'] = None
        form = self.form_class(data, instance=c)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'], ['This field is required.'])

        data['password'] = ''
        form = self.form_class(data, instance=c)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'], ['This field is required.'])

        data['password'] = 'a'*41
        form = self.form_class(data, instance=c)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'],
            ['Ensure this value has at most 40 characters (it has 41).'])

        # Services
        data['services'] = None
        form = self.form_class(data, instance=c)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['services'], ['This field is required.'])

        data['services'] = 'http'
        form = self.form_class(data, instance=c)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['services'], ['Enter a list of values.'])

        data['services'] = []
        form = self.form_class(data, instance=c)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['services'], ['This field is required.'])

    def test_default_credential_edit_form(self):
        """Default credentials should be properly updated when edited through
           a form"""
        c = models.Credential.objects.create(
            team=None, default=None, username='what', password='ever',
            services=[self.service1])
        data = {'username':'what', 'password':'ever',
                'services':[self.service1]}

        data['username'] = 'blah'
        form = self.form_class(data, instance=c)
        self.assertTrue(form.is_valid())
        form.save()
        c = models.Credential.objects.get(pk=c.pk) # Reload from DB
        self.assertEqual(c.username, 'blah')
        self.assertEqual(models.Credential.objects.count(), 3)

        data['password'] = 'blop'
        form = self.form_class(data, instance=c)
        self.assertTrue(form.is_valid())
        form.save()
        c = models.Credential.objects.get(pk=c.pk) # Reload from DB
        self.assertEqual(c.password, 'blop')
        self.assertEqual(models.Credential.objects.count(), 3)

        data['services'] = [self.service1, self.service2]
        form = self.form_class(data, instance=c)
        self.assertTrue(form.is_valid())
        form.save()
        c = models.Credential.objects.get(pk=c.pk) # Reload from DB
        self.assertEqual(set(c.services.all()),
                         set([self.service1, self.service2]))
        self.assertEqual(models.Credential.objects.count(), 3)

    def test_default_cred_form_edit_propagation(self):
        """When default credentials are edited through a form,
           its associated credentials should also be updated"""
        def_cred = models.Credential.objects.create(
            team=None, default=None, username='test', password='toor',
            services=[self.service1])
        data = {'username':'test', 'password':'toor',
                'services':[self.service1]}

        data['username'] = 'what'
        form = self.form_class(data, instance=def_cred)
        self.assertTrue(form.is_valid())
        form.save()
        for c in def_cred.assoc_creds.all():
            self.assertEqual(c.username, 'what')

        data['password'] = 'blah'
        form = self.form_class(data, instance=def_cred)
        self.assertTrue(form.is_valid())
        form.save()
        for c in def_cred.assoc_creds.all():
            self.assertEqual(c.password, 'blah')

        data['services'] = [self.service1, self.service2]
        form = self.form_class(data, instance=def_cred)
        self.assertTrue(form.is_valid())
        form.save()
        for c in def_cred.assoc_creds.all():
            self.assertEqual(set(c.services.all()),
                             set([self.service1, self.service2]))
