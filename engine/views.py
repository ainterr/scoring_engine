from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from . import models, forms

def simple_add_modify(post_req, context):
    model_str = post_req['type']
    
    if model_str == 'team':
        model = models.Team
    if model_str == 'service':
        model = models.Service
    if model_str == 'credential':
        model = models.Credential

    if 'id' in post_req:
        inst = model.objects.get(id=post_req['id'])
    else:
        inst = None

    form = forms.ModelFormFactory(model)(post_req, instance=inst)

    if form.is_valid():
        form.save()
    else:
        context['invalid_' + model_str] = True

def delete(post_req):
    model_type = post_req['type']
    pk = post_req['id']
    if model_type == 'user':
        model = models.User
    if model_type == 'service':
        model = models.Service
    if model_type == 'credential':
        model = models.Credential
    if model_type == 'team':
        model = models.Team

    model.objects.get(pk=pk).delete()

def gen_model_forms(model_type):
    form_class = forms.ModelFormFactory(model_type)
    model_forms = {0: form_class()}
    for m in model_type.objects.all():
        model_forms[m.pk] = form_class(instance=m)
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
                simple_add_modify(request.POST, context)

    context['teams'] = models.Team.objects.all()
    context['team_forms'] = gen_model_forms(models.Team)
    
    return render(request, 'teams.html', context)

@login_required
@user_passes_test(is_admin, login_url='index', redirect_field_name=None)
def team_detail(request, pk):
    context = {}

    if request.method == 'POST' and \
       request.POST['type'] in ['user', 'credential']:
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
              simple_add_modify(request.POST, context)

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

    if request.method == 'POST' and request.POST['type'] == 'service':
        if 'delete' in request.POST:
            delete(request.POST)
        else:
            simple_add_modify(request.POST, context)
    else:
        form = forms.ModelFormFactory(models.Service)()

    context['services'] = models.Service.objects.all()
    context['service_forms'] = gen_model_forms(models.Service)
    return render(request, 'services.html', context)

@login_required
@user_passes_test(is_admin, login_url='index', redirect_field_name=None)
def default_creds(request):
    context = {}

    if request.method == 'POST':
        if 'delete' in request.POST and request.POST['type'] == 'credential':
            cred = models.Credential.objects.get(pk=request.POST['id'])
            for c in models.Credential.objects.filter(
              default=True, username=cred.username, password=cred.password):
                c.delete()
        else:
            form = forms.ModelFormFactory(models.Credential,
                     ['default', 'team'])(request.POST)
            if form.is_valid():
                cred = form.save(commit=False)
                cred.default = True
                for team in models.Team.objects.all():
                    cred.pk = None
                    cred.team = team
                    cred.save()
                    form.save_m2m()
                cred.pk = None
                cred.team = None
                cred.save()
                form.save_m2m()
            else:
                context['invalid_'+request.POST['type']] = True

    context['credentials'] = models.Credential.objects.filter(team=None)
    context['credential_forms'] = gen_model_forms(models.Credential)
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
