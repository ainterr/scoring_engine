from __future__ import unicode_literals

from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=20, blank=False)

class Credential(models.Model):
    username = models.CharField(max_length=20, blank=False)
    password = models.CharField(max_length=40, blank=False)

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='credentials')

class Plugin(models.Model):
    name = models.CharField(max_length=20, blank=False)

class Result(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='results')
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='results')
    
