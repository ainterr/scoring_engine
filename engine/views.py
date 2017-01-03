from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from . import models, forms

def model_from_str(model_str):
    if model_str == 'user':
        model = models.User
    elif model_str == 'service':
        model = models.Service
    elif model_str == 'credential':
        model = models.Credential
    elif model_str == 'team':
        model = models.Team
    return model

def simple_add_modify(request, ex=[]):
    model = model_from_str(request.POST['type'])
    
    if 'id' in request.POST: # Editing
        inst = model.objects.get(pk=request.POST['id'])
    else: # New
        inst = None

    form = forms.ModelFormFactory(model, ex)(request.POST, instance=inst)

    if form.is_valid():
        form.save()

def delete(post_req):
    model = model_from_str(post_req['type'])
    pk = post_req['id']

    model.objects.get(pk=pk).delete()

def gen_model_forms(form, model):
    """Creates a dict of forms. model_forms[0] is a blank form used for adding
       new model objects. model_forms[m.pk] is an editing form pre-populated
       the fields of m"""
    model_forms = {0: form()}
    for m in model.objects.all():
        model_forms[m.pk] = form(instance=m)
    return model_forms

def get_status(team):
    check_results = []
    for service in models.Service.objects.all():
        results = service.results.filter(team=team)

        if results.count() != 0:
            last_result = results.last()

            status = '{}'.format(last_result)
            total = results.count()
            total_passed = results.filter(status=True).count()
            percent = '{:.2f}'.format(total_passed/float(total)*100)
            style = 'success' if last_result.status else 'danger'
        else:
            status = 'UNKNOWN'
            total = 0
            total_passed = 0
            percent = '{:.2f}'.format(0.0)
            style = 'default'

        check_results.append({
            'service': service.name,
            'status': status,
            'passed': total_passed,
            'run': total,
            'percent': percent,
            'style': style
        })

    return check_results

def is_admin(user):
    return user.is_superuser

def is_not_admin(user):
    return not user.is_superuser

def index(request):
    context = {}

    teams = models.Team.objects.all()

    context['teams'] = []
    for team in teams:
        context['teams'].append({
            'name': team.name,
            'id': team.id,
            'results': get_status(team)
        })

    return render(request, 'index.html', context)

@login_required
@user_passes_test(is_not_admin, login_url='index', redirect_field_name=None)
def status(request):
    team = request.user.team

    context = {}
    context['results'] = get_status(team)
    return render(request, 'status.html', context)
    #return render(request, 'not_found.html', context)

@login_required
@user_passes_test(is_admin, login_url='index', redirect_field_name=None)
def teams(request):
    context = {}

    if request.method == 'POST':
        if 'delete' in request.POST:
            delete(request.POST)
        else:
            simple_add_modify(request)
    
    form = forms.ModelFormFactory(models.Team)
    context['teams'] = models.Team.objects.all()
    context['team_forms'] = gen_model_forms(form, models.Team)
    
    return render(request, 'teams.html', context)

@login_required
@user_passes_test(is_admin, login_url='index', redirect_field_name=None)
def team_detail(request, pk):
    context = {}

    if request.method == 'POST':
        if 'delete' in request.POST:
            delete(request.POST)
        elif 'reset' in request.POST:
            model = models.User.objects.get(pk=request.POST['id'])
            model.set_password(request.POST['password'])
            model.save()
        else:
            if request.POST['type'] == 'user': # Special case for user forms
                form = forms.UserForm(request.POST)
                if form.is_valid():
                    form.cleaned_data['team'] = models.Team.objects.get(id=pk)
                    form.save()
                else:
                    context['invalid_'+request.POST['type']] = True
            else:
                simple_add_modify(request)

    try:
        team = models.Team.objects.get(pk=pk)
    except models.Team.DoesNotExist:
        return render(request, 'not_found.html', context)

    context['team'] = team
    context['users'] = team.users.all()
    context['user_form'] = forms.UserForm
    context['services'] = models.Service.objects.all()
    context['service_form'] = forms.ModelFormFactory(models.Service)
    context['credentials'] = team.credentials.all()
    context['credential_form'] = forms.ModelFormFactory(models.Credential)

    return render(request, 'team_detail.html', context)

@login_required
@user_passes_test(is_admin, login_url='index', redirect_field_name=None)
def services(request):
    context = {}

    if request.method == 'POST':
        if 'delete' in request.POST:
            delete(request.POST)
        else:
            simple_add_modify(request)

    form = forms.ModelFormFactory(models.Service)
    context['services'] = models.Service.objects.all()
    context['service_forms'] = gen_model_forms(form, models.Service)
    return render(request, 'services.html', context)

@login_required
@user_passes_test(is_admin, login_url='index', redirect_field_name=None)
def default_creds(request):
    context = {}

    if request.method == 'POST':
        if 'delete' in request.POST:
            delete(request.POST)
        else:
            if 'id' in request.POST:
                inst = models.Credential.objects.get(pk=request.POST['id'])
            else:
                inst = None
            form = forms.DefaultCredentialForm(request.POST, instance=inst)
            if form.is_valid():
                form.save()

    form = forms.DefaultCredentialForm
    context['credentials'] = models.Credential.objects.filter(team=None)
    context['credential_forms'] = gen_model_forms(form, models.Credential)
    context['services'] = models.Service.objects.all()

    return render(request, 'credentials.html', context)

@login_required
@user_passes_test(is_admin, login_url='index', redirect_field_name=None)
def bulk_password(request):
    context = {}
    if request.method == 'POST':
        form = forms.BulkPasswordForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            messages.error(request, 'Bad form input')
    else:
        form = forms.BulkPasswordForm()
        
    context['teams'] = models.Team.objects.all()
    context['services'] = models.Service.objects.all()
    context['password_form'] = form
    return render(request, 'bulk_password.html', context)
