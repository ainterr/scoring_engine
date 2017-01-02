from django.test import TransactionTestCase
from django.core.exceptions import ValidationError
from django.core.management import call_command
from .. import models

import logging
logging.disable(logging.ERROR)

class ResultTests(TransactionTestCase):
    def setUp(self):
        call_command('registerplugins')
        self.t1 = models.Team.objects.create(
            name='Team1', subnet='192.168.1.0', netmask='255.255.255.0')
        self.t2 = models.Team.objects.create(
            name='Team2', subnet='192.168.2.0', netmask='255.255.255.0')
        self.http = models.Plugin.objects.get(name='http')
        self.smb = models.Plugin.objects.get(name='smb')
        self.s1 = models.Service.objects.create(
            name='Service1', subnet_host=1, port=1, plugin=self.http)
        self.s2 = models.Service.objects.create(
            name='Service2', subnet_host=2, port=2, plugin=self.smb)
       

    def test_malformed_result(self):
        """Should not be able to create results with malformed data"""
        # Too little data
        with self.assertRaises(ValidationError):
            models.Result.objects.create()
        with self.assertRaises(ValidationError):
            models.Result.objects.create(team=self.t1)
        with self.assertRaises(ValidationError):
            models.Result.objects.create(service=self.s1)
        # Malformed arguments
        with self.assertRaises(ValidationError): # Team is None
            models.Result.objects.create(team=None, service=self.s1)
        with self.assertRaises(ValidationError): # Service is None
            models.Result.objects.create(team=self.t1, service=None)
        with self.assertRaises(ValidationError): # Result is None
            models.Result.objects.create(
                team=self.t1, service=self.s1, status=None)

    def test_correct_result(self):
        """Correctly created results should be allowed"""
        self.assertEqual(models.Result.objects.count(), 0)
        models.Result.objects.create(team=self.t1, service=self.s1)
        self.assertEqual(models.Result.objects.count(), 1)
        models.Result.objects.create(team=self.t1, service=self.s1, status=True)
        self.assertEqual(models.Result.objects.count(), 2)

    def test_result_no_edit(self):
        """Result objects should not be editable"""
        r = models.Result.objects.create(team=self.t1, service=self.s1)
        with self.assertRaises(ValidationError):
            r.team = self.t2
            r.save()
        with self.assertRaises(ValidationError):
            r.service = self.s2
            r.save()
        with self.assertRaises(ValidationError):
            r.status = True
            r.save()

    def test_result_team_delete_cascade(self):
        """When a result's team is deleted, it should also be deleted"""
        models.Result.objects.create(team=self.t1, service=self.s1)
        self.assertEqual(models.Result.objects.count(), 1)
        self.t1.delete()
        self.assertEqual(models.Result.objects.count(), 0)

    def test_result_service_delete_cascade(self):
        """When a result's service is deleted, it should also be deleted"""
        models.Result.objects.create(team=self.t1, service=self.s1)
        self.assertEqual(models.Result.objects.count(), 1)
        self.s1.delete()
        self.assertEqual(models.Result.objects.count(), 0)

    def test_result_plugin_delete_cascade(self):
        """When a result's service's plugin is deleted,
           it should also be deleted"""
        models.Result.objects.create(team=self.t1, service=self.s1)
        self.assertEqual(models.Result.objects.count(), 1)
        self.http.delete()
        self.assertEqual(models.Result.objects.count(), 0)
