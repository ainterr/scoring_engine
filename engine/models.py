from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=20, blank=False)
    ip = models.GenericIPAddressField(blank=False)
    port = models.PositiveIntegerField(blank=False)

    # Plugin creates a field here called  'plugin'
    # Team creates a field here called 'teams'
    # Result creates a field here called 'results'

class Plugin(models.Model):
    servce = models.OneToOneField(Service, on_delete=models.CASCADE, related_name='plugin')

    name = models.CharField(max_length=20, blank=False)

class Team(models.Model):
    name = models.CharField(max_length=20, blank=False)

    services = models.ManyToManyField(Service, related_name='teams')

    # UserProfile creates a field here called 'users'
    # Credential creates a field here called 'credentials'
    # Result creates a field here called 'results'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='users')

class Credential(models.Model):
    username = models.CharField(max_length=20, blank=False)
    password = models.CharField(max_length=40, blank=False)

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='credentials')

class Result(models.Model):
    status = models.BooleanField(default=False)
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='results')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='results')
