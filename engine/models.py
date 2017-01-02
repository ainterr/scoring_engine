from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError

from ipaddress import ip_network, ip_address
from . import plugins
import os

class Plugin(models.Model):
    name = models.CharField(max_length=20, blank=False, unique=True)

    # Service creates a field here called 'services'
    # Result creates a field here called 'results'

    def clean(self):
        if self.pk is not None:
            raise ValidationError('Plugins cannot be edited')
        ps = os.listdir(plugins.__path__[0])
        py_file = '{}.py'.format(self.name)
        name_is_in = [py_file == p for p in ps]
        if not any(name_is_in):
            raise ValidationError(
                'Not a valid plugin name:{}'.format(self.name))

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Plugin, self).save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.name)

class Team(models.Model):
    name = models.CharField(max_length=20, blank=False, unique=True)
    subnet = models.GenericIPAddressField(blank=False, unique=True)
    netmask = models.GenericIPAddressField(blank=False)

    # UserProfile creates a field here called 'users'
    # Credential creates a field here called 'credentials'
    # Result creates a field here called 'results'

    def clean(self):
        if not isinstance(self.name, str):
            raise ValidationError('Team name must be a string.')
        if self.name == '':
            raise ValidationError('Team should not have a blank name.')

        try:
            net = ip_network('{}/{}'.format(self.subnet, self.netmask),
                             strict=False)
        except ValueError:
            raise ValidationError('Team subnet/netmask should be a valid IP network.')
        for team in Team.objects.exclude(pk=self.pk):
          other_net = ip_network('{}/{}'.format(team.subnet, team.netmask),
                                 strict=False)
          if net.overlaps(other_net):
              raise ValidationError('Team subnets should not overlap.')

    def __str__(self):
        return '{}, id={}'.format(self.name, self.id)

    def save(self, *args, **kwargs):
        self.full_clean()
        new_team = self.pk is None
        super(Team, self).save(*args, **kwargs)
        if new_team:
            for c in Credential.objects.filter(team=None):
                c.populate_teams()
 

class UserManager(BaseUserManager):
    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)

class User(AbstractUser):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='users', blank=True, null=True)

    objects = UserManager()

    REQUIRED_FIELDS = []

    def __str__(self):
        return '{} team={}'.format(self.username, self.team.id)

class Service(models.Model):
    name = models.CharField(max_length=20, blank=False, unique=True)
    subnet_host = models.PositiveIntegerField(blank=False)
    port = models.PositiveIntegerField(blank=False)

    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='services')

    # Result creates a field here called 'results'
    # Credential creates a field here called 'credentials'

    def ip(self, subnet, netmask):
      network = ip_network('{}/{}'.format(subnet, netmask), strict=False)
      ip = network.network_address + self.subnet_host
      return '{}'.format(ip)

    def clean(self):
        if self.name == '':
            raise ValidationError('Service should not have blank name')

        if not isinstance(self.subnet_host, int) or self.subnet_host < 0:
            raise ValidationError('Service subnet host must be positive')

        if self.port not in range(1, 65536):
            raise ValidationError('Service port not in valid range 1-65535')

        for service in Service.objects.exclude(pk=self.pk):
            if self.subnet_host == service.subnet_host and \
               self.port == service.port:
                raise ValidationError('Service already exists on host {} port {}'.format(self.subnet_host, self.port))

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Service, self).save(*args, **kwargs)

    def __str__(self):
        return '{} ip={}, port={}, plugin={}'.format(
            self.name, 
            self.subnet_host, 
            self.port, 
            self.plugin.id
        )

class Credential(models.Model):
    username = models.CharField(max_length=20, blank=False)
    password = models.CharField(max_length=40, blank=False)

    team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.CASCADE, related_name='credentials')
    default = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='assoc_creds') # If this is default, points to the default cred

    services = models.ManyToManyField(Service, related_name='credentials')

    def __init__(self, *args, services=[], **kwargs):
        super(Credential, self).__init__(*args, **kwargs)
        self.services_tmp = services

    def clean(self):
        if self.username == '':
            raise ValidationError('Credential should not have blank username')
        if self.password == '':
            raise ValidationError('Credential should not have blank password')

    def populate_teams(self):
        """If this is a default cred, populate all teams with copies of self"""
        if self.team is not None: # This is not a default cred
            return

        team_pks = [c.team.pk for c in self.assoc_creds.all()]
        for t in Team.objects.exclude(pk__in=team_pks):
            c = Credential.objects.create(team=t, username=self.username,
                                      password=self.password, default=self,
                                      services=self.services.all())

    def save(self, *args, **kwargs):
        self.full_clean()
        new_cred = self.pk is None

        if not new_cred and self.default is not None and \
           (self.username != self.default.username or \
           self.password != self.default.password or \
           list(self.services.all()) != list(self.default.services.all())):
            self.default = None # Assoc_cred is edited, unlink it

        super(Credential, self).save(*args, **kwargs)

        if self.services_tmp != []: # Update m2m, now that saving is done
            self.services = self.services_tmp
            self.services_tmp = []

        if new_cred and self.team is None: # New default cred
            self.populate_teams()
        if not new_cred and self.team is None: # Editing default cred
            for c in self.assoc_creds.all():
                c.username = self.username
                c.password = self.password
                c.services = self.services.all()
                c.save()

    def __str__(self):
        return '{}:{}'.format(self.username, self.password)

class Result(models.Model):
    status = models.BooleanField(default=False)
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='results')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='results')

    def clean(self):
        if self.pk is not None:
            raise ValidationError('Results cannot be edited')
        if self.status is None:
            raise ValidationError('Result status cannot be None')

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Result, self).save(*args, **kwargs)

    def __str__(self):
        return '{}'.format('PASSED' if self.status else 'FAILED')
