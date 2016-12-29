from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

from ipaddress import ip_network

class Plugin(models.Model):
    name = models.CharField(max_length=20, blank=False)

    # Service creates a field here called 'services'
    # Result creates a field here called 'results'

    def __str__(self):
        return '{}'.format(self.name)

class Team(models.Model):
    name = models.CharField(max_length=20, blank=False, unique=True)
    subnet = models.GenericIPAddressField(blank=False, unique=True)
    netmask = models.GenericIPAddressField(blank=False)

    # UserProfile creates a field here called 'users'
    # Credential creates a field here called 'credentials'
    # Result creates a field here called 'results'

    def __str__(self):
        return '{}, id={}'.format(self.name, self.id)

    def save(self, *args, **kwargs):
        new_team = self.pk is None
        super(Team, self).save(*args, **kwargs)
        if new_team:
            for c in Credential.objects.filter(team=None):
                new_cred = Credential(
                    team=self,
                    default=True,
                    username=c.username,
                    password=c.password)
                new_cred.save()
                new_cred.services.set(c.services.all())        
 

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
    name = models.CharField(max_length=20, blank=False)
    subnet_host = models.PositiveIntegerField(blank=False)
    port = models.PositiveIntegerField(blank=False)

    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='services')

    # Result creates a field here called 'results'
    # Credential creates a field here called 'credentials'

    def ip(self, subnet, netmask):
      network = ip_network('{}/{}'.format(subnet, netmask))
      ip = network.network_address + self.subnet_host
      return '{}'.format(ip)

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
    default = models.BooleanField(default=True)

    team = models.ForeignKey(Team, null=True, on_delete=models.CASCADE, related_name='credentials')

    services = models.ManyToManyField(Service, related_name='credentials')

    def __str__(self):
        return '{}:{}'.format(self.username, self.password)

class Result(models.Model):
    status = models.BooleanField(default=False)
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='results')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='results')
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='results')

    def __str__(self):
        return '{}'.format('PASSED' if self.status else 'FAILED')
