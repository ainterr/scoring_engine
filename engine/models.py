from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class Plugin(models.Model):
    name = models.CharField(max_length=20, blank=False)

    # Service creates a field here called 'services'
    # Result creates a field here called 'results'

    def __str__(self):
        return '{}'.format(self.name)

class Team(models.Model):
    name = models.CharField(max_length=20, blank=False)

    # UserProfile creates a field here called 'users'
    # Service creates a field here called 'services'
    # Credential creates a field here called 'credentials'
    # Result creates a field here called 'results'

    def __str__(self):
        return '{}, id={}'.format(self.name, self.id)

class UserManager(BaseUserManager):
    def _create_user(self, username, team, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')

        try:
            team = Team.objects.get(pk=team)
        except Team.DoesNotExist:
            raise ValueError('The specified team ID does not exist')

        user = self.model(username=username, team=team, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, username, team, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, team, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, team, password, **extra_fields)

class User(AbstractUser):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='users')

    objects = UserManager()

    REQUIRED_FIELDS = ['team']

    def __str__(self):
        return '{} team={}'.format(self.username, self.team.id)

class Service(models.Model):
    name = models.CharField(max_length=20, blank=False)
    ip = models.GenericIPAddressField(blank=False)
    port = models.PositiveIntegerField(blank=False)

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='services')
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='services')

    # Result creates a field here called 'results'
    # Credential creates a field here called 'credentials'

    def __str__(self):
        return '{} ip={}, port={}, team={}, plugin={}'.format(
            self.name, 
            self.ip, 
            self.port, 
            self.team.id, 
            self.plugin.id
        )

class Credential(models.Model):
    username = models.CharField(max_length=20, blank=False)
    password = models.CharField(max_length=40, blank=False)

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='credentials')

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
