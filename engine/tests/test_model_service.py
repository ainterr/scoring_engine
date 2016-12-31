from django.test import TransactionTestCase
from django.core.exceptions import ValidationError
from django.core.management import call_command
from .. import models

class ServiceTests(TransactionTestCase):
    def setUp(self):
        call_command('registerplugins')
        self.http = models.Plugin.objects.get(name='http')
        self.smb = models.Plugin.objects.get(name='smb')

    def test_malformed_service(self):
        """Should not be able to create services with malformed data"""
        # Too little data
        with self.assertRaises(ValidationError):
            models.Service.objects.create()
        with self.assertRaises(ValidationError):
            models.Service.objects.create(name='Service1')
        with self.assertRaises(ValidationError):
            models.Service.objects.create(subnet_host=2)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(port=80)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(plugin=self.http)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(name='Service1', subnet_host=1)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(name='Service1', port=90)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(name='Service1', plugin=self.http)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(subnet_host=2, port=93)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(subnet_host=2, plugin=self.smb)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(port=2, plugin=self.smb)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(
                name='Service1', subnet_host=2, port=44)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(
                name='Service1', subnet_host=32, plugin=self.smb)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(
                name='Service1', port=32, plugin=self.smb)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(
                subnet_host=38, port=32, plugin=self.smb)
        # Malformed arguments
        ## Name
        with self.assertRaises(ValidationError): # Name is None
            models.Service.objects.create(
                name=None, subnet_host=1, port=93, plugin=self.http)
        with self.assertRaises(ValidationError): # Name is empty
            models.Service.objects.create(
                name='', subnet_host=1, port=93, plugin=self.http)
        with self.assertRaises(ValidationError): # Name is too long
            models.Service.objects.create(
                name='a'*21, subnet_host=1, port=93, plugin=self.http)
        ## Subnet_host
        with self.assertRaises(ValidationError): # Subnet_host is None
            models.Service.objects.create(
                name='Service', subnet_host=None, port=93, plugin=self.http)
        with self.assertRaises(ValidationError): # Subnet_host is not a number
            models.Service.objects.create(
                name='Service', subnet_host='hi', port=93, plugin=self.http)
        with self.assertRaises(ValidationError): # Subnet_host is negative
            models.Service.objects.create(
                name='Service', subnet_host=-1, port=93, plugin=self.http)
        # Port
        with self.assertRaises(ValidationError): # Port is None
            models.Service.objects.create(
                name='Service', subnet_host=1, port=None, plugin=self.http)
        with self.assertRaises(ValidationError): # Port is not a number
            models.Service.objects.create(
                name='Service', subnet_host=1, port='oh', plugin=self.http)
        with self.assertRaises(ValidationError): # Port is negative
            models.Service.objects.create(
                name='Service', subnet_host=1, port=-1, plugin=self.http)
        with self.assertRaises(ValidationError): # Port is outside port range
            models.Service.objects.create(
                name='Service', subnet_host=1, port=65536, plugin=self.http)
        with self.assertRaises(ValidationError): # Port is outside port range
            models.Service.objects.create(
                name='Service', subnet_host=1, port=0, plugin=self.http)
        # Plugin
        with self.assertRaises(ValidationError): # Plugin is None
            models.Service.objects.create(
                name='Service', subnet_host=1, port=15, plugin=None)
        with self.assertRaises(ValueError): # Plugin is not a model object
            models.Service.objects.create(
                name='Service', subnet_host=1, port=15, plugin='http')

    def test_service_same_names(self):
        """Services with the same name are not allowed"""
        models.Service.objects.create(
            name='Service1', subnet_host=1, port=30, plugin=self.http)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(
                name='Service1', subnet_host=2, port=38, plugin=self.http)

    def test_service_same_host_port(self):
        """Services with the same host/port combo are not allowed"""
        models.Service.objects.create(
            name='Service1', subnet_host=1, port=30, plugin=self.http)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(
                name='Service2', subnet_host=1, port=30, plugin=self.smb)

    def test_service_correct(self):
        """Correctly created services should be allowed"""
        self.assertEqual(models.Service.objects.count(), 0)
        models.Service.objects.create(
            name='Service1', subnet_host=1, port=80, plugin=self.http)
        self.assertEqual(models.Service.objects.count(), 1)
        models.Service.objects.create(
            name='Service2', subnet_host=4, port=38, plugin=self.smb)
        self.assertEqual(models.Service.objects.count(), 2)
        models.Service.objects.create( # Same host different port
            name='Service3', subnet_host=1, port=38, plugin=self.http)
        self.assertEqual(models.Service.objects.count(), 3)
        models.Service.objects.create( # Different host same port
            name='Service4', subnet_host=2, port=80, plugin=self.http)
        self.assertEqual(models.Service.objects.count(), 4)

    def test_service_plugin_delete_cascade(self):
        """When a service's plugin is deleted, the service is also deleted"""
        models.Service.objects.create(
            name='Service', subnet_host=5, port=39, plugin=self.http)
        self.assertEqual(models.Service.objects.count(), 1)
        self.http.delete()
        self.assertEqual(models.Service.objects.count(), 0)

    def test_service_ip_calculation(self):
        """IPs should be properly calculated from subnet and netmask"""
        s1 = models.Service.objects.create(
            name='Service1', subnet_host=3, port=28, plugin=self.http)
        s2 = models.Service.objects.create(
            name='Service2', subnet_host=15, port=28, plugin=self.http)
        ip1 = s1.ip('192.168.1.0', '255.255.255.0')
        self.assertEqual(ip1, '192.168.1.3')
        ip2 = s2.ip('192.168.1.0', '255.255.255.0')
        self.assertEqual(ip2, '192.168.1.15')
        ip3 = s1.ip('192.168.1.0', '255.255.255.128')
        self.assertEqual(ip3, '192.168.1.3')
        ip4 = s2.ip('192.168.1.128', '255.255.255.128')
        self.assertEqual(ip4, '192.168.1.143')
