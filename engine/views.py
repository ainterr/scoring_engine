from django.shortcuts import render
from django.http import HttpResponse

import models

def index(request):
    return render(request, 'index.html', {})

def status(request):
    context = {
        'results': [
            {'service': 'HTTP', 'status': 'Passed', 'passed': 10, 'run': 10, 'percent': 100, 'style': 'success' },
            {'service': 'HTTPS', 'status': 'Failed', 'passed': 8, 'run': 10, 'percent': 80, 'style': 'danger'},
        ]
    }
    return render(request, 'status.html', context)
