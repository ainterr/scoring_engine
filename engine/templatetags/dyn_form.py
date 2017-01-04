from django import template
from .. import forms

register = template.Library()

@register.filter
def dyn_form(forms, pk):
    return forms[pk]
