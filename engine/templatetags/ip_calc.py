from django import template
from .. import models

register = template.Library()

@register.filter(name='ip')
def ip(service, team):
  return service.ip(team.subnet, team.netmask)
