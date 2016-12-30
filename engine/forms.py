from django import forms
from django.core.validators import RegexValidator
from . import models

def ModelFormFactory(model_class, ex=[]):
    class Form(forms.ModelForm):
        class Meta: 
            model = model_class
            exclude = ex

    return Form


class UserForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput())

    def save(self):
        models.User.objects.create_user(
            username=self.cleaned_data['username'], 
            password=self.cleaned_data['password'],
            team=self.cleaned_data['team']
        )

    class Meta: 
        model = models.User
        fields = ['username', 'password', 'team']

class BulkPasswordForm(forms.ModelForm):
    changeList = forms.CharField(
        label='Password Changes',
        help_text='Enter password changes in format \'user:password\' (no quotes), one per line',
        widget=forms.Textarea(),
        validators=[RegexValidator('^([!-~]+:[!-~]+\s*\n?)+$')])
    service = forms.ModelChoiceField(models.Service.objects.all())
    
    def save(self):
        team = self.cleaned_data['team']
        service = self.cleaned_data['service']
        for line in self.cleaned_data['changeList'].split('\n'):
            user,passwd = line.strip().split(':')
            try:
                cred = models.Credential.objects.get(team=team, username=user, services=service)
                if cred.services.count() > 1:
                    # Create new object, remove service from cred.services
                    cred.services.remove(service)
                    cred.default = None
                    cred.save()
    
                    new_cred = models.Credential.objects.create(
                        team=team,
                        username=user,
                        password=passwd,
                        default=None
                    )
                    new_cred.services.add(service)
                    new_cred.save()
                    
                else:
                    cred.password = passwd
                    cred.default=None
                    cred.save()
            except models.Credential.DoesNotExist:
                pass # User entered a credential which doesn't exist. Ignore it


    class Meta:
        model = models.Credential
        fields = ['team', 'service', 'changeList']
