from django.test import TransactionTestCase
from django.core.exceptions import ValidationError
from .. import models

import logging
logging.disable(logging.ERROR)

class PluginTests(TransactionTestCase):
    def test_malformed_plugin(self):
        """Should not be able to create plugins with malformed data"""
        # Too little data
        with self.assertRaises(ValidationError):
            models.Plugin.objects.create()
        # Malformed arguments
        with self.assertRaises(ValidationError): # Name is empty
            models.Plugin.objects.create(name='')
        with self.assertRaises(ValidationError): # Name is None
            models.Plugin.objects.create(name=None)
        with self.assertRaises(ValidationError): # Name is too long
            models.Plugin.objects.create(name='a'*21)
        with self.assertRaises(ValidationError): # Name is not a valid plugin
            models.Plugin.objects.create(name='kdkdkdsksls')

    def test_plugin_same_name(self):
        """Plugins with the same name are not allowed"""
        models.Plugin.objects.create(name='http')
        with self.assertRaises(ValidationError):
            models.Plugin.objects.create(name='http')

    def test_correct_plugin(self):
        """Correctly created plugins should be allowed"""
        self.assertEqual(models.Plugin.objects.count(), 0)
        models.Plugin.objects.create(name='http')
        self.assertEqual(models.Plugin.objects.count(), 1)
        models.Plugin.objects.create(name='https')
        self.assertEqual(models.Plugin.objects.count(), 2)

    def test_plugin_no_edit(self):
        """Plugin objects should not be editable"""
        p = models.Plugin.objects.create(name='smb')
        with self.assertRaises(ValidationError):
            p.name = 'http'
            p.save()
