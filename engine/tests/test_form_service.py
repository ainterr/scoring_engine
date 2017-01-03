from django.test import TransactionTestCase
from django.core.exceptions import ValidationError
from django.core.management import call_command
from .. import models, forms

class ServiceTests(TransactionTestCase):
    form_class = forms.ModelFormFactory(models.Service)

    def setUp(self):
        call_command('registerplugins')
        self.http = models.Plugin.objects.get(name='http')
        self.smb = models.Plugin.objects.get(name='smb')

    def test_malformed_service_form(self):
        """Should not be able to submit service forms with malformed data"""
        # Too little data
        data = {}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['This field is required.'])

        data = {'name':'Service1'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet_host'],
            ['This field is required.'])

        data = {'subnet_host':2}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['This field is required.'])

        data = {'port':80}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['This field is required.'])

        data = {'plugin':self.http.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['This field is required.'])

        data = {'name':'Service1', 'subnet_host':1}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['port'],
            ['This field is required.'])

        data = {'name':'Service1', 'port':90}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet_host'],
            ['This field is required.'])

        data = {'name':'Service1', 'plugin':self.http.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet_host'],
            ['This field is required.'])

        data = {'subnet_host':2, 'port':93}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['This field is required.'])

        data = {'subnet_host':2, 'plugin':self.smb.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['This field is required.'])

        data = {'port':2, 'plugin':self.smb.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['This field is required.'])

        data = {'name':'Service1', 'subnet_host':2, 'port':44}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['plugin'],
            ['This field is required.'])

        data = {'name':'Service1', 'subnet_host':2, 'plugin':self.smb.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['port'],
            ['This field is required.'])

        data = {'name':'Service1', 'port':32, 'plugin':self.smb.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet_host'],
            ['This field is required.'])

        data = {'subnet_host':38, 'port':32, 'plugin':self.smb.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['This field is required.'])

        # Malformed arguments
        ## Name
        data = {'name':None, 'subnet_host':1, 'port':93, 'plugin':self.http.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['This field is required.'])

        data = {'name':'', 'subnet_host':1, 'port':93, 'plugin':self.http.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['This field is required.'])

        data = {'name':'a'*21, 'subnet_host':1, 'port':93, 'plugin':self.http.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['Ensure this value has at most 20 characters (it has 21).'])

        ## Subnet_host
        data = {'name':'Service', 'subnet_host':None, 'port':93,
                'plugin':self.http.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet_host'],
            ['This field is required.'])

        data = {'name':'Service', 'subnet_host':'hi', 'port':93,
                'plugin':self.http.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet_host'],
            ['Enter a whole number.'])

        data = {'name':'Service', 'subnet_host':-1, 'port':93,
                'plugin':self.http.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet_host'],
            ['Ensure this value is greater than or equal to 0.'])

        # Port
        data = {'name':'Service', 'subnet_host':1, 'port':None,
                'plugin':self.http.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['port'],
            ['This field is required.'])

        data = {'name':'Service', 'subnet_host':1, 'port':'oh',
                'plugin':self.http.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['port'],
            ['Enter a whole number.'])

        data = {'name':'Service', 'subnet_host':1, 'port':-1,
                'plugin':self.http.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['port'],
            ['Ensure this value is greater than or equal to 0.'])

        data = {'name':'Service', 'subnet_host':1, 'port':0, 'plugin':self.http.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Service port not in valid range 1-65535.'])

        data = {'name':'Service', 'subnet_host':1, 'port':65536,
                'plugin':self.http.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Service port not in valid range 1-65535.'])

        # Plugin
        data = {'name':'Service', 'subnet_host':1, 'port':15,
                'plugin':None}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['plugin'],
            ['This field is required.'])

        data = {'name':'Service', 'subnet_host':1, 'port':15,
                'plugin':'http'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['plugin'],
            ['Select a valid choice. That choice is not one of the available choices.'])

    def test_service_same_names_form(self):
        """Service form submissions with the same name are not allowed"""
        models.Service.objects.create(
            name='Service1', subnet_host=1, port=30, plugin=self.http)

        data = {'name':'Service1', 'subnet_host':2, 'port':38,
                'plugin':self.http.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['Service with this Name already exists.'])

    def test_service_same_host_port_form(self):
        """Service form submissions with the same host/port combo
           are not allowed"""
        models.Service.objects.create(
            name='Service1', subnet_host=1, port=30, plugin=self.http)

        data = {'name':'Service2', 'subnet_host':1, 'port':30,
                'plugin':self.smb.pk}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Service already exists on host 1 port 30.'])

    def test_service_correct_form(self):
        """Correctly subitted service forms should be allowed"""
        self.assertEqual(models.Service.objects.count(), 0)
        data = {'name':'Service1', 'subnet_host':1, 'port':80,
                'plugin':self.http.pk}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(models.Service.objects.count(), 1)

        data = {'name':'Service2', 'subnet_host':4, 'port':38,
                'plugin':self.smb.pk}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(models.Service.objects.count(), 2)

        data = {'name':'Service3', 'subnet_host':1, 'port':38,
                'plugin':self.http.pk} # Same host different port
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(models.Service.objects.count(), 3)

        data = {'name':'Service4', 'subnet_host':2, 'port':80,
                'plugin':self.http.pk} # Different host same port
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(models.Service.objects.count(), 4)

    def test_service_malformed_edit_form(self):
        """Service forms should raise an error when
           edited with malformed data"""
        s = models.Service.objects.create(
            name='Service', subnet_host=1, port=93, plugin=self.http)

        data = {'name':'Service', 'subnet_host':1, 'port':93,
                'plugin':self.http.pk}
        # Malformed arguments
        ## Name
        data['name'] = None
        form = self.form_class(data, instance=s)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['This field is required.'])

        data['name'] = ''
        form = self.form_class(data, instance=s)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['This field is required.'])

        data['name'] = 'a'*21
        form = self.form_class(data, instance=s)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['Ensure this value has at most 20 characters (it has 21).'])

        ## Subnet_host
        data['name'] = 'Service'
        data['subnet_host'] = None
        form = self.form_class(data, instance=s)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet_host'],
            ['This field is required.'])

        data['subnet_host'] = 'hi'
        form = self.form_class(data, instance=s)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet_host'],
            ['Enter a whole number.'])

        data['subnet_host'] = -1
        form = self.form_class(data, instance=s)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet_host'],
            ['Ensure this value is greater than or equal to 0.'])

        # Port
        data['subnet_host'] = 1
        data['port'] = None
        form = self.form_class(data, instance=s)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['port'],
            ['This field is required.'])

        data['port'] = 'oh'
        form = self.form_class(data, instance=s)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['port'],
            ['Enter a whole number.'])

        data['port'] = -1
        form = self.form_class(data, instance=s)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['port'],
            ['Ensure this value is greater than or equal to 0.'])

        data['port'] = 0
        form = self.form_class(data, instance=s)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Service port not in valid range 1-65535.'])

        data['port'] = 65536
        form = self.form_class(data, instance=s)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Service port not in valid range 1-65535.'])

        # Plugin
        data['port'] = 93
        data['plugin'] = None
        form = self.form_class(data, instance=s)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['plugin'],
            ['This field is required.'])

        data['plugin'] = 'http'
        form = self.form_class(data, instance=s)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['plugin'],
            ['Select a valid choice. That choice is not one of the available choices.'])

    def test_service_edit_form(self):
        """Service fields should be updated when properly edited
           through a form"""
        s = models.Service.objects.create(
            name='Service', subnet_host=1, port=93, plugin=self.http)
        data = {'name':'kdkdkdkd', 'subnet_host':1, 'port':93,
                'plugin':self.http.pk}

        data['name']= 'kdkdkdkd'
        form = self.form_class(data, instance=s)
        self.assertTrue(form.is_valid())
        form.save()
        s = models.Service.objects.get(pk=s.pk)
        self.assertEqual(s.name, 'kdkdkdkd')

        data['subnet_host'] = 5
        form = self.form_class(data, instance=s)
        self.assertTrue(form.is_valid())
        form.save()
        s = models.Service.objects.get(pk=s.pk)
        self.assertEqual(s.subnet_host, 5)

        data['port'] = 5
        form = self.form_class(data, instance=s)
        self.assertTrue(form.is_valid())
        form.save()
        s = models.Service.objects.get(pk=s.pk)
        self.assertEqual(s.port, 5)

        data['plugin'] = self.smb.pk
        form = self.form_class(data, instance=s)
        self.assertTrue(form.is_valid())
        form.save()
        s = models.Service.objects.get(pk=s.pk)
        self.assertEqual(s.plugin, self.smb)

    def test_service_edit_same_names_form(self):
        """Services with the same name are not allowed when editing
           through forms"""
        models.Service.objects.create(
            name='Service1', subnet_host=1, port=30, plugin=self.http)
        s = models.Service.objects.create(
            name='Service2', subnet_host=2, port=38, plugin=self.http)

        data = {'name':'Service2', 'subnet_host':2, 'port':38,
                'plugin':self.http.pk}
        data['name'] = 'Service1'
        form = self.form_class(data, instance=s)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['Service with this Name already exists.'])

    def test_service_edit_same_host_port_form(self):
        """Services with the same host/port combo are not allowed
           when editing through forms"""
        models.Service.objects.create(
            name='Service1', subnet_host=1, port=30, plugin=self.http)

        s = models.Service.objects.create(
            name='Service2', subnet_host=2, port=30, plugin=self.smb)
        data = {'name':'Service2', 'subnet_host':2, 'port':30,
                'plugin':self.smb.pk}

        data['subnet_host'] = 1
        form = self.form_class(data, instance=s)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Service already exists on host 1 port 30.'])

        s = models.Service.objects.create(
            name='Service3', subnet_host=1, port=50, plugin=self.smb)
        data = {'name':'Service3', 'subnet_host':1, 'port':50,
                'plugin':self.smb.pk}

        data['port'] = 30
        form = self.form_class(data, instance=s)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Service already exists on host 1 port 30.'])
