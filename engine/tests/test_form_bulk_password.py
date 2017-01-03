from django.core.management import call_command
from django.test import TransactionTestCase
from django.core.exceptions import ValidationError
from .. import models, forms

import logging
logging.disable(logging.ERROR)

class BulkPasswordFormTests(TransactionTestCase):
    form_class = forms.BulkPasswordForm

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
        self.def_cred1 = models.Credential.objects.create(
            team=None, default=None, username='root', password='toor',
            services=[self.service1])
        self.def_cred2 = models.Credential.objects.create(
            team=None, default=None, username='what', password='ever',
            services=[self.service1, self.service2])
        self.cred1 = models.Credential.objects.create(
            team=self.team1, default=None, username='john', password='walker',
            services=[self.service1, self.service2])
        self.cred2 = models.Credential.objects.create(
            team=self.team2, default=None, username='tom', password='wilson',
            services=[self.service1])

    def cred_equal(self, c1, c2):
        self.assertEqual(c1.team, c2.team)
        self.assertEqual(c1.default, c2.default)
        self.assertEqual(c1.username, c2.username)
        self.assertEqual(c1.password, c2.password)
        self.assertEqual(set(c1.services.all()), set(c2.services.all()))

    def test_malformed_bulk_password_form(self):
        """Should not be able to edit credentials with malformed data
           through forms"""
        # Too little data
        data = {}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['change_list'],
            ['This field is required.'])
 
        data = {'change_list':'blah:blah'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['service'], ['This field is required.'])

        data = {'change_list':'blah:blah', 'service':self.service1.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['team'], ['This field is required.'])

        # Malformed arguments
        # ChangeList
        data = {'change_list':None, 'service':self.service1.pk,
                'team':self.team1.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['change_list'],
            ['This field is required.'])

        data = {'change_list':'', 'service':self.service1.pk,
                'team':self.team1.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['change_list'],
            ['This field is required.'])
 
        # Bad formatting of changelist is checked in separate function

        # Service
        data = {'change_list':'blah:blah', 'service':None,
                'team':self.team1.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['service'], ['This field is required.'])

        data = {'change_list':'blah:blah', 'service':'blah',
                'team':self.team1.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['service'],
            ['Select a valid choice. That choice is not one of the available choices.'])

        data = {'change_list':'blah:blah', 'service':-1,
                'team':self.team1.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['service'],
            ['Select a valid choice. That choice is not one of the available choices.'])

        # Team
        data = {'change_list':'blah:blah', 'service':self.service1.pk,
                'team':None}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['team'], ['This field is required.'])

        data = {'change_list':'blah:blah', 'service':self.service1.pk,
                'team':'blah'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['team'],
            ['Select a valid choice. That choice is not one of the available choices.'])

        data = {'change_list':'blah:blah', 'service':self.service1.pk,
                'team':-1}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['team'],
            ['Select a valid choice. That choice is not one of the available choices.'])

    def test_bulk_password_form_invalid_change_list(self):
        """Change lists which don't match the proper format should not be
           accepted"""
        data = {'service':self.service1.pk, 'team':self.team1.pk}

        data['change_list'] = ' '
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['change_list'],
            ['This field is required.'])

        data['change_list'] = 'a'
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['change_list'],
            ['Enter a valid value.'])

        data['change_list'] = '\n\n\n\n\n\n'
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['change_list'],
            ['This field is required.'])

        data['change_list'] = 'blah:blah\na'
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['change_list'],
            ['Enter a valid value.'])

        data['change_list'] = ':'
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['change_list'],
            ['Enter a valid value.'])

        data['change_list'] = ':\n:\n'
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['change_list'],
            ['Enter a valid value.'])

        data['change_list'] = 'blah:x\n:\n'
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['change_list'],
            ['Enter a valid value.'])

        data['change_list'] = 'blah:x\nx:\n'
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['change_list'],
            ['Enter a valid value.'])

        data['change_list'] = 'blah:x\n:x\n'
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['change_list'],
            ['Enter a valid value.'])

        data['change_list'] = 'what ever:say'
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['change_list'],
            ['Enter a valid value.'])

        data['change_list'] = 'whatever:you say'
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['change_list'],
            ['Enter a valid value.'])

    def test_bulk_password_form_correct(self):
        """Correctly formatted bulk password forms are allowed"""
        data = {'change_list':'x:lol', 'service':self.service1.pk,
                'team':self.team1.pk}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())

        data = {'change_list':'john:test', 'service':self.service2.pk,
                'team':self.team2.pk}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())

        data = {'change_list':'john:test\nblah:blah\n',
                'service':self.service2.pk, 'team':self.team2.pk}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())

        data = {'change_list':' john:test',
                'service':self.service2.pk, 'team':self.team2.pk}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())

        data = {'change_list':' john:test\n\n\n\n',
                'service':self.service2.pk, 'team':self.team2.pk}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())

        data = {'change_list':'john:te::::st\n\n\n\n',
                'service':self.service2.pk, 'team':self.team2.pk}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())

        data = {'change_list':'john:te::::st\n\n\n\n',
                'service':self.service2.pk, 'team':self.team2.pk}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())

        data = {'change_list':'  john:test    ',
                'service':self.service2.pk, 'team':self.team2.pk}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())

        data = {'change_list':'john:test     \n\n\n\n',
                'service':self.service2.pk, 'team':self.team2.pk}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        
    def test_bulk_password_form_nonexistent_credential(self):
        """A password change for a credential which does not exist
           should have no effect and cause no errors"""
        creds = list(models.Credential.objects.all())

        data = {'change_list':'john:wilson',
                'service':self.service2.pk, 'team':self.team2.pk}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        form.save()

        for c in creds:
            self.cred_equal(c, models.Credential.objects.get(pk=c.pk))

        data = {'change_list':'john:wilson',
                'service':self.service1.pk, 'team':self.team2.pk}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(models.Credential.objects.count(), 8)
        for c in creds:
            self.cred_equal(c, models.Credential.objects.get(pk=c.pk))

    def test_bulk_password_form_existent_credential_single_service(self):
        """A password change for a single-service credential combo which does
           exist should go through. It should only affect that one credential"""
        # Non-default
        creds = list(models.Credential.objects.exclude(pk=self.cred2.pk))
        data = {'change_list':'tom:crafty',
                'service':self.service1.pk, 'team':self.team2.pk}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(models.Credential.objects.count(), 8)
        for c in creds:
            self.cred_equal(c, models.Credential.objects.get(pk=c.pk))

        c_check = models.Credential.objects.get(pk=self.cred2.pk)
        self.assertEqual(c_check.team, self.team2)
        self.assertEqual(c_check.default, None)
        self.assertEqual(c_check.username, 'tom')
        self.assertEqual(c_check.password, 'crafty')
        self.assertEqual(set(c_check.services.all()), set([self.service1]))

        # Default
        c_check = models.Credential.objects.get(default=self.def_cred1,
                                                team=self.team1)
        creds = list(models.Credential.objects.exclude(pk=c_check.pk))
        data = {'change_list':'root:password',
                'service':self.service1.pk, 'team':self.team1.pk}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(models.Credential.objects.count(), 8)
        for c in creds:
            self.cred_equal(c, models.Credential.objects.get(pk=c.pk))

        c_check = models.Credential.objects.get(pk=c_check.pk)
        self.assertEqual(c_check.team, self.team1)
        self.assertEqual(c_check.default, None)
        self.assertEqual(c_check.username, 'root')
        self.assertEqual(c_check.password, 'password')
        self.assertEqual(set(c_check.services.all()), set([self.service1]))

    def test_bulk_password_form_existent_credential_multi_service(self):
        """A password change for a multi-service credential combo which does
           exist should go through. It should create a separate credential
           and the old one should lose the service."""
        # Non-default
        creds = list(models.Credential.objects.exclude(pk=self.cred1.pk))
        data = {'change_list':'john:smith',
                'service':self.service1.pk, 'team':self.team1.pk}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(models.Credential.objects.count(), 9)
        for c in creds:
            self.cred_equal(c, models.Credential.objects.get(pk=c.pk))
        # Old is same, but w/o service1        
        c_check = models.Credential.objects.get(pk=self.cred1.pk)
        self.assertEqual(c_check.team, self.team1)
        self.assertEqual(c_check.default, None)
        self.assertEqual(c_check.username, 'john')
        self.assertEqual(c_check.password, 'walker')
        self.assertEqual(set(c_check.services.all()), set([self.service2]))
        # New has updated password and only service1
        c_check = models.Credential.objects.latest('pk')
        self.assertEqual(c_check.team, self.team1)
        self.assertEqual(c_check.default, None)
        self.assertEqual(c_check.username, 'john')
        self.assertEqual(c_check.password, 'smith')
        self.assertEqual(set(c_check.services.all()), set([self.service1]))

        # Default
        c_check = models.Credential.objects.get(default=self.def_cred2,
                                                team=self.team2)
        creds = list(models.Credential.objects.exclude(pk=c_check.pk))
        data = {'change_list':'what:name',
                'service':self.service2.pk, 'team':self.team2.pk}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(models.Credential.objects.count(), 10)
        for c in creds:
            self.cred_equal(c, models.Credential.objects.get(pk=c.pk))
        # Old is same, but w/o service2 and no default
        c_check = models.Credential.objects.get(pk=c_check.pk)
        self.assertEqual(c_check.team, self.team2)
        self.assertEqual(c_check.default, None)
        self.assertEqual(c_check.username, 'what')
        self.assertEqual(c_check.password, 'ever')
        self.assertEqual(set(c_check.services.all()), set([self.service1]))
        # New has updated password and only service2
        c_check = models.Credential.objects.latest('pk')
        self.assertEqual(c_check.team, self.team2)
        self.assertEqual(c_check.default, None)
        self.assertEqual(c_check.username, 'what')
        self.assertEqual(c_check.password, 'name')
        self.assertEqual(set(c_check.services.all()), set([self.service2]))

