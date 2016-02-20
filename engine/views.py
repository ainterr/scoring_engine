from django.shortcuts import render
from django.http import HttpResponse

import models

def index(request):
    return render(request, 'index.html', {})

def status(request):
    context = {}

    # For now we're hardcoding a team name
    try:
        team = models.Team.objects.get(name='NUCCDC')
    except models.Team.DoesNotExist:
        return render(request, 'not_found.html', context)

    context['results'] = []
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

        context['results'].append({
            'service': service.name,
            'status': status,
            'passed': total_passed,
            'run': total,
            'percent': percent,
            'style': style
        })

    return render(request, 'status.html', context)
