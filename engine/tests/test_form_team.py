from django.test import TransactionTestCase, Client
from django.core.exceptions import ValidationError
from .. import models, forms

# TODO: IPv6 tests
import logging
logging.disable(logging.ERROR)

class TeamFormTests(TransactionTestCase):
    form_class = forms.ModelFormFactory(models.Team)

    def test_malformed_team_form(self):
        """Should not be able to submit a form for teams with malformed data"""
        # Too little data
        data = {}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['This field is required.'])
    
        data = {'name':'Team1'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet'], ['This field is required.'])
   
        data = {'subnet':'192.168.1.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['This field is required.'])
  
        data = {'netmask':'255.255.255.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['This field is required.'])

        data = {'name':'Team1', 'subnet':'192.168.1.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['netmask'],
                         ['This field is required.'])

        data = {'name':'Team1', 'netmask':'255.255.255.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet'], ['This field is required.'])
 
        data = {'subnet':'192.168.1.0', 'netmask':'255.255.255.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['This field is required.'])
           
        # Malformed arguments
        ## Name
        data = {'name':'', 'subnet':'192.168.1.0', 'netmask':'255.255.255.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team should not have a blank name.'])

        data = {'name':None, 'subnet':'192.168.1.0', 'netmask':'255.255.255.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team should not have a blank name.'])

        data = {'name':'a'*21, 'subnet':'192.168.1.0',
                'netmask':'255.255.255.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['Ensure this value has at most 20 characters (it has 21).'])
        ## Subnet
        data = {'name':'Team1', 'subnet':None, 'netmask':'255.255.255.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team subnet/netmask should be a valid IP network.'])

        data = {'name':'Team1', 'subnet':'blah', 'netmask':'255.255.255.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team subnet/netmask should be a valid IP network.'])

        data = {'name':'Team1', 'subnet':'192.1688.1.0',
                'netmask':'255.255.255.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team subnet/netmask should be a valid IP network.'])

        data = {'name':'Team1', 'subnet':'192.-168.1.0',
                'netmask':'255.255.255.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team subnet/netmask should be a valid IP network.'])

        data = {'name':'Team1', 'subnet':'192.168.1', 'netmask':'255.255.255.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team subnet/netmask should be a valid IP network.'])

        data = {'name':'Team1', 'subnet':'300.0.1.0', 'netmask':'255.255.255.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team subnet/netmask should be a valid IP network.'])

        ## Netmask
        data = {'name':'Team1', 'subnet':'300.0.1.0', 'netmask':None}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team subnet/netmask should be a valid IP network.'])

        data = {'name':'Team1', 'subnet':'192.168.1.0', 'netmask':'what'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team subnet/netmask should be a valid IP network.'])

        data = {'name':'Team1', 'subnet':'192.168.1.0',
                'netmask':'255.3255.255.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team subnet/netmask should be a valid IP network.'])

        data = {'name':'Team1', 'subnet':'192.168.1.0',
                'netmask':'255.255.-255.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team subnet/netmask should be a valid IP network.'])

        data = {'name':'Team1', 'subnet':'192.168.1', 'netmask':'255.255.255'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team subnet/netmask should be a valid IP network.'])

        data = {'name':'Team1', 'subnet':'300.0.1.0', 'netmask':'255.450.255.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team subnet/netmask should be a valid IP network.'])

    def test_team_same_names_form(self):
        """Teams with the same name are not allowed"""
        models.Team.objects.create(
            name='Team1', subnet='192.168.1.0', netmask='255.255.255.0')

        data = {'name':'Team1', 'subnet':'192.168.2.0',
                'netmask':'255.255.255.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['Team with this Name already exists.'])

    def test_team_overlapping_subnet_form(self):
        """Teams with overlapping subnets are not allowed"""
        models.Team.objects.create(
            name='Team1', subnet='192.168.1.0', netmask='255.255.255.0')

        data = {'name':'Team2', 'subnet':'192.168.1.128',
                'netmask':'255.255.255.0'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team subnets should not overlap.'])

        models.Team.objects.create(
            name='Team3', subnet='192.168.2.128', netmask='255.255.255.0')

        data = {'name':'Team4', 'subnet':'192.168.2.197',
                'netmask':'255.255.255.128'}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team subnets should not overlap.'])

    def test_team_correct_form(self):
        """Correctly created teams should be allowed"""
        self.assertEqual(models.Team.objects.count(), 0)
        data = {'name':'Team1', 'subnet':'192.168.1.0',
                'netmask':'255.255.255.0'}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(models.Team.objects.count(), 1)

        data = {'name':'Team2', 'subnet':'192.168.2.0', 
                'netmask':'255.255.255.0'}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(models.Team.objects.count(), 2)

        # Smaller subnets
        data = {'name':'Team3', 'subnet':'192.168.3.0',
                'netmask':'255.255.255.128'}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(models.Team.objects.count(), 3)

        data = {'type':'team', 'name':'Team4', 'subnet':'192.168.3.129',
                'netmask':'255.255.255.128'}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(models.Team.objects.count(), 4)

    def test_team_default_credentials_form(self):
        """New teams should be populated with default credentials
           if they are available"""
        # Creating a new team w/ no default creds set
        self.assertEqual(models.Credential.objects.count(), 0)
        data = {'name':'Team1', 'subnet':'192.168.1.0',
                'netmask':'255.255.255.0'}
        form = self.form_class(data)
        form.save()
        self.assertEqual(models.Credential.objects.count(), 0)

        c = models.Credential.objects.create( # Default Credential w/o service
            team=None, default=None, username='test', password='toor')
        self.assertEqual(models.Credential.objects.count(), 2)

        data = {'name':'Team2', 'subnet':'192.168.2.0',
                'netmask':'255.255.255.0'}
        form = self.form_class(data)
        form.save()
        self.assertEqual(models.Credential.objects.count(), 3)

    def test_team_malformed_edit_form(self):
        """Team forms should raise an error when edited with malformed data"""
        t = models.Team.objects.create(
            name='Team1', subnet='192.168.1.0', netmask='255.255.255.0')
        data = {'name':'Team1', 'subnet':'192.168.1.0',
                 'netmask':'255.255.255.0'}
         ## Name
        data['name'] = ''
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['This field is required.'])
      
        data['name'] = None
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['This field is required.'])

        data['name'] = 'a'*21
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['Ensure this value has at most 20 characters (it has 21).'])

        ## Subnet
        data['name'] = 'Team1'
        data['subnet'] = None
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet'],
            ['This field is required.'])

        data['subnet'] = 'blah'
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet'],
            ['Enter a valid IPv4 or IPv6 address.'])

        data['subnet'] = '192.1688.1.0'
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet'],
            ['Enter a valid IPv4 or IPv6 address.'])

        data['subnet'] = '192.-168.1.0'
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet'],
            ['Enter a valid IPv4 or IPv6 address.'])

        data['subnet'] = '192.168.1'
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet'],
            ['Enter a valid IPv4 or IPv6 address.'])

        data['subnet'] = '300.0.1.0'
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subnet'],
            ['Enter a valid IPv4 or IPv6 address.'])

        ## Netmask
        data['subnet'] = '192.168.1.0'
        data['netmask'] = None
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['netmask'],
            ['This field is required.'])

        data['netmask'] = 'what'
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['netmask'],
            ['Enter a valid IPv4 or IPv6 address.'])

        data['netmask'] = '255.3255.255.0'
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['netmask'],
            ['Enter a valid IPv4 or IPv6 address.'])

        data['netmask'] = '255.255.-255.0'
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['netmask'],
            ['Enter a valid IPv4 or IPv6 address.'])

        data['netmask'] = '255.255.255'
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['netmask'],
            ['Enter a valid IPv4 or IPv6 address.'])

        data['netmask'] = '255.450.255.0'
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['netmask'],
            ['Enter a valid IPv4 or IPv6 address.'])

    def test_team_edit_same_name(self):
        """Teams with the same name are not allowed, when editing"""
        models.Team.objects.create(
            name='Team1', subnet='192.168.1.0', netmask='255.255.255.0')
        t = models.Team.objects.create(
            name='Team2', subnet='192.168.2.0', netmask='255.255.255.0')

        data = {'name':'Team1', 'subnet':'192.168.2.0',
                'netmask':'255.255.255.0'}
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'],
            ['Team with this Name already exists.'])

    def test_team_edit_overlapping_subnet(self):
        """Teams with overlapping subnets are not allowed"""
        models.Team.objects.create(
            name='Team1', subnet='192.168.1.0', netmask='255.255.255.0')
        t = models.Team.objects.create(
            name='Team2', subnet='192.168.2.0', netmask='255.255.255.0')

        data = {'name':'Team2', 'subnet':'192.168.1.128',
                'netmask':'255.255.255.0'}
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team subnets should not overlap.'])

        models.Team.objects.create(
            name='Team3', subnet='192.168.3.0', netmask='255.255.255.128')
        t = models.Team.objects.create(
            name='Team4', subnet='192.168.3.128', netmask='255.255.255.128')

        data = {'name':'Team4', 'subnet':'192.168.3.128',
                'netmask':'255.255.255.0'}
        form = self.form_class(data, instance=t)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
            ['Team subnets should not overlap.'])

    def test_team_edit(self):
        """Fields should be properly updated when a team is edited"""
        t = models.Team.objects.create(
            name='Team1', subnet='192.168.1.0', netmask='255.255.255.0')

        data =  {'id':t.pk, 'type':'team', 'name':'Team2',
            'subnet':'192.168.1.0', 'netmask':'255.255.255.0'}
        form = self.form_class(data, instance=t)
        self.assertTrue(form.is_valid())
        form.save()
        t = models.Team.objects.get(pk=t.pk) # Reload from DB
        self.assertEqual(t.name, 'Team2')

        data['subnet'] = '192.168.2.0'
        form = self.form_class(data, instance=t)
        self.assertTrue(form.is_valid())
        form.save()
        t = models.Team.objects.get(pk=t.pk) # Reload from DB
        self.assertEqual(t.subnet, '192.168.2.0')

        data['netmask'] = '255.255.255.128'
        form = self.form_class(data, instance=t)
        self.assertTrue(form.is_valid())
        form.save()
        t = models.Team.objects.get(pk=t.pk) # Reload from DB
        self.assertEqual(t.netmask, '255.255.255.128')
