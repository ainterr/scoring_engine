from django.forms import ModelForm

def ModelFormFactory(model_class):
    class Form(ModelForm):
        class Meta: 
            model = model_class
            fields = '__all__'

    return Form
