from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from . import models

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
def status(request):
    team = request.user.team

    context = {}
    context['results'] = get_status(team)
    return render(request, 'status.html', context)
    #return render(request, 'not_found.html', context)
