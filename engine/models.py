from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

class Plugin(models.Model):
    name = models.CharField(max_length=20, blank=False)

    # Service creates a field here called 'services'
    # Result creates a field here called 'results'

    def __unicode__(self):
        return '{}'.format(self.name)

class Team(models.Model):
    name = models.CharField(max_length=20, blank=False)

    # UserProfile creates a field here called 'users'
    # Service creates a field here called 'services'
    # Credential creates a field here called 'credentials'
    # Result creates a field here called 'results'

    def __unicode__(self):
        return '{}, id={}'.format(self.name, self.id)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='users')

    def __unicode__(self):
        return '{} team={}'.format(self.user, self.team.id)

class Service(models.Model):
    name = models.CharField(max_length=20, blank=False)
    ip = models.GenericIPAddressField(blank=False)
    port = models.PositiveIntegerField(blank=False)

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='services')
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='services')

    # Result creates a field here called 'results'

    def __unicode__(self):
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

    def __unicode__(self):
        return '{}:{}'.format(self.username, self.password)

class Result(models.Model):
    status = models.BooleanField(default=False)
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='results')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='results')
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='results')

    def __unicode__(self):
        return '{}'.format('PASSED' if self.status else 'FAILED')
