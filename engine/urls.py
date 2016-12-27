from django.conf.urls import url

from . import views, poller

import signal

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^status/$', views.status, name='status'),
    url(r'^teams/$', views.teams, name='teams'),
    url(r'^teams/([0-9]+)/$', views.team_detail, name='team_detail'),
    url(r'^services/$', views.services, name='services'),
    url(r'^credentials/$', views.default_creds, name='credentials'),
    url(r'^bulk_password/$', views.bulk_password, name='bulk_password'),
]
