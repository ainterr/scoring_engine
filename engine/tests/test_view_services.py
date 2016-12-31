from django.test import TransactionTestCase, Client
from django.core.exceptions import ValidationError
from django.core.management import call_command
from .. import models

class ServicesViewTests(TransactionTestCase):
    def setUp(self):
        self.c = Client()
        user = models.User.objects.create_user(
            username='admin', password='toortoor', is_superuser=True)
        success = self.c.force_login(user)
        self.path = '/services/'

        call_command('registerplugins')
        self.http = models.Plugin.objects.get(name='http')
        self.smb = models.Plugin.objects.get(name='smb')

    def test_malformed_service(self):
        #TODO
        return
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
            models.Service.objects.create(plugin=self.http.pk)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(name='Service1', subnet_host=1)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(name='Service1', port=90)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(name='Service1', plugin=self.http.pk)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(subnet_host=2, port=93)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(subnet_host=2, plugin=self.smb.pk)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(port=2, plugin=self.smb.pk)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(
                name='Service1', subnet_host=2, port=44)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(
                name='Service1', subnet_host=32, plugin=self.smb.pk)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(
                name='Service1', port=32, plugin=self.smb.pk)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(
                subnet_host=38, port=32, plugin=self.smb.pk)
        # Malformed arguments
        ## Name
        with self.assertRaises(ValidationError): # Name is None
            models.Service.objects.create(
                name=None, subnet_host=1, port=93, plugin=self.http.pk)
        with self.assertRaises(ValidationError): # Name is empty
            models.Service.objects.create(
                name='', subnet_host=1, port=93, plugin=self.http.pk)
        with self.assertRaises(ValidationError): # Name is too long
            models.Service.objects.create(
                name='a'*21, subnet_host=1, port=93, plugin=self.http.pk)
        ## Subnet_host
        with self.assertRaises(ValidationError): # Subnet_host is None
            models.Service.objects.create(
                name='Service', subnet_host=None, port=93, plugin=self.http.pk)
        with self.assertRaises(ValidationError): # Subnet_host is not a number
            models.Service.objects.create(
                name='Service', subnet_host='hi', port=93, plugin=self.http.pk)
        with self.assertRaises(ValidationError): # Subnet_host is negative
            models.Service.objects.create(
                name='Service', subnet_host=-1, port=93, plugin=self.http.pk)
        # Port
        with self.assertRaises(ValidationError): # Port is None
            models.Service.objects.create(
                name='Service', subnet_host=1, port=None, plugin=self.http.pk)
        with self.assertRaises(ValidationError): # Port is not a number
            models.Service.objects.create(
                name='Service', subnet_host=1, port='oh', plugin=self.http.pk)
        with self.assertRaises(ValidationError): # Port is negative
            models.Service.objects.create(
                name='Service', subnet_host=1, port=-1, plugin=self.http.pk)
        with self.assertRaises(ValidationError): # Port is outside port range
            models.Service.objects.create(
                name='Service', subnet_host=1, port=65536, plugin=self.http.pk)
        with self.assertRaises(ValidationError): # Port is outside port range
            models.Service.objects.create(
                name='Service', subnet_host=1, port=0, plugin=self.http.pk)
        # Plugin
        with self.assertRaises(ValidationError): # Plugin is None
            models.Service.objects.create(
                name='Service', subnet_host=1, port=15, plugin=None)
        with self.assertRaises(ValueError): # Plugin is not a model object
            models.Service.objects.create(
                name='Service', subnet_host=1, port=15, plugin='http')

    def test_service_same_names(self):
        #TODO
        return
        """Services with the same name are not allowed"""
        models.Service.objects.create(
            name='Service1', subnet_host=1, port=30, plugin=self.http.pk)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(
                name='Service1', subnet_host=2, port=38, plugin=self.http.pk)

    def test_service_same_host_port(self):
        #TODO
        return
        """Services with the same host/port combo are not allowed"""
        models.Service.objects.create(
            name='Service1', subnet_host=1, port=30, plugin=self.http.pk)
        with self.assertRaises(ValidationError):
            models.Service.objects.create(
                name='Service2', subnet_host=1, port=30, plugin=self.smb.pk)

    def test_service_correct(self):
        """Correctly created services should be allowed"""
        self.assertEqual(models.Service.objects.count(), 0)
        self.c.post(self.path, 
            {'type':'service', 'name':'Service1', 'subnet_host':1, 
             'port':80, 'plugin':self.http.pk})
        self.assertEqual(models.Service.objects.count(), 1)
        self.c.post(self.path, 
            {'type':'service', 'name':'Service2', 'subnet_host':4, 
             'port':38, 'plugin':self.smb.pk})
        self.assertEqual(models.Service.objects.count(), 2)
        self.c.post(self.path, 
            {'type':'service', 'name':'Service3', 'subnet_host':1,
             'port':38, 'plugin':self.http.pk})
        self.assertEqual(models.Service.objects.count(), 3)
        self.c.post(self.path, 
            {'type':'service', 'name':'Service4', 'subnet_host':2,
             'port':80, 'plugin':self.http.pk})
        self.assertEqual(models.Service.objects.count(), 4)

    def test_service_malformed_edit(self):
        #TODO
        return
        """Services should raise an error when edited with malformed data"""
        s = models.Service.objects.create(
            name='Service', subnet_host=1, port=93, plugin=self.http.pk)

        with self.assertRaises(ValidationError): # Name is None
            s.name = None
            s.save()
        with self.assertRaises(ValidationError): # Name is empty
            s.name = ''
            s.save()
        with self.assertRaises(ValidationError): # Name is too long
            s.name = 'a'*21
            s.save()
        ## Subnet_host
        with self.assertRaises(ValidationError): # Subnet_host is None
            s.subnet_host = None
            s.save()
        with self.assertRaises(ValidationError): # Subnet_host is not a number
            s.subnet_host = 'hi'
            s.save()
        with self.assertRaises(ValidationError): # Subnet_host is negative
            s.subnet_host = -1
            s.save()
        # Port
        with self.assertRaises(ValidationError): # Port is None
            s.port = None
            s.save()
        with self.assertRaises(ValidationError): # Port is not a number
            s.port = 'oh'
            s.save()
        with self.assertRaises(ValidationError): # Port is negative
            s.port = -1
            s.save()
        with self.assertRaises(ValidationError): # Port is outside port range
            s.port = 65536
            s.save()
        with self.assertRaises(ValidationError): # Port is outside port range
            s.port = 0
            s.save()
        # Plugin
        with self.assertRaises(ValidationError): # Plugin is None
            s.plugin = None
            s.save()
        with self.assertRaises(ValueError): # Plugin is not a model object
            s.plugin = 'http'
            s.save()

    def test_service_edit(self):
        """Service fields should be updated when properly edited"""
        s = models.Service.objects.create(
            name='Service', subnet_host=1, port=93, plugin=self.http)
        post_data = {'id':s.pk, 'type':'service', 'name':'kdkdkdkd',
                     'subnet_host':1, 'port':93, 'plugin':self.http.pk}

        self.c.post(self.path, post_data)
        s = models.Service.objects.get(pk=s.pk)
        self.assertEqual(s.name, 'kdkdkdkd')

        post_data['subnet_host'] = 5
        self.c.post(self.path, post_data)
        s = models.Service.objects.get(pk=s.pk)
        self.assertEqual(s.subnet_host, 5)

        post_data['port'] = 5
        self.c.post(self.path, post_data)
        s = models.Service.objects.get(pk=s.pk)
        self.assertEqual(s.port, 5)

        post_data['plugin'] = self.smb.pk
        self.c.post(self.path, post_data)
        s = models.Service.objects.get(pk=s.pk)
        self.assertEqual(s.plugin, self.smb)

    def test_service_edit_same_names(self):
        #TODO
        return
        """Services with the same name are not allowed when editing"""
        models.Service.objects.create(
            name='Service1', subnet_host=1, port=30, plugin=self.http.pk)
        s = models.Service.objects.create(
            name='Service2', subnet_host=2, port=38, plugin=self.http.pk)
        with self.assertRaises(ValidationError):
            s.name = 'Service1'
            s.save()

    def test_service_edit_same_host_port(self):
        #TODO
        return
        """Services with the same host/port combo are not allowed
           when editing"""
        models.Service.objects.create(
            name='Service1', subnet_host=1, port=30, plugin=self.http.pk)

        s = models.Service.objects.create(
            name='Service2', subnet_host=2, port=30, plugin=self.smb.pk)
        with self.assertRaises(ValidationError):
            s.subnet_host = 1
            s.save()

        s = models.Service.objects.create(
            name='Service3', subnet_host=1, port=50, plugin=self.smb.pk)
        with self.assertRaises(ValidationError):
            s.port = 30
            s.save()
