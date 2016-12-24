from django import forms
from . import models

def ModelFormFactory(model_class):
    class Form(forms.ModelForm):
        class Meta: 
            model = model_class
            fields = '__all__'

    return Form

class UserForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput())

    def save(self):
        models.User.objects.create_user(
            username=self.cleaned_data['username'], 
            password=self.cleaned_data['password'],
            team=self.cleaned_data['team']  # This must be set in the view
        )

    def setTeam(self, team):
        self.is_valid()
        self.cleaned_data['team'] = team

    class Meta: 
        model = models.User
        fields = ['username', 'password']
