from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from . import models, forms

def get_status(team):
    check_results = []
    for service in team.services.all():
        results = service.results

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
            team = models.Team.objects.get(pk=request.POST['id'])
            team.delete()
        else:
            form = forms.ModelFormFactory(models.Team)(request.POST)
            if form.is_valid():
                form.save()
            else:
                context['invalid'] = True

    context['results'] = models.Team.objects.all()
    context['form'] = forms.ModelFormFactory(models.Team)
    
    return render(request, 'teams.html', context)
