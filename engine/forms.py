from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
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


class DefaultCredentialForm(forms.ModelForm):
    def clean(self):
        if 'username' in self.cleaned_data and 'services' in self.cleaned_data:
            username = self.cleaned_data['username']
            services = self.cleaned_data['services']
            for c in models.Credential.objects.filter(team=None).exclude(
               pk=self.instance.pk):
                if username == c.username and \
                   not set(services).isdisjoint(set(c.services.all())):
                    raise ValidationError('A credential already has that username/service pair on this team.')
        return self.cleaned_data

    def save(self):
        self.instance.save()
        services = list(self.cleaned_data['services'].all())
        self.instance.services = services
        self.instance.save()
        return self.instance
 
    class Meta:
        model = models.Credential
        exclude = ['team', 'default']


class BulkPasswordForm(forms.Form):
    team = forms.ModelChoiceField(models.Team.objects.all())
    service = forms.ModelChoiceField(models.Service.objects.all())
    change_list = forms.CharField(
        label='Password Changes',
        help_text='Enter password changes in format \'user:password\' (no quotes), one per line',
        widget=forms.Textarea(),
        validators=[RegexValidator('^([!-~]+:[!-~]+\s*\n?)+$')])
    
    def save(self):
        team = self.cleaned_data['team']
        service = self.cleaned_data['service']
        for line in self.cleaned_data['change_list'].split('\n'):
            user,passwd = line.strip().split(':', 1)
            try:
                cred = models.Credential.objects.get(
                    team=team, username=user, services=service)
                if cred.services.count() > 1:
                    # Create new object, remove service from cred.services
                    cred.services.remove(service)
                    cred.save()
    
                    new_cred = models.Credential.objects.create(
                        team=team,
                        username=user,
                        password=passwd,
                        default=None,
                        services=[service]
                    )
                else:
                    cred.password = passwd
                    cred.save()
            except models.Credential.DoesNotExist:
                pass # User entered a credential which doesn't exist. Ignore it
