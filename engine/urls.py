from django.conf.urls import url

from . import views, poller

import signal

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^status/$', views.status, name='status'),
    url(r'^status/([0-9]+)/$', views.status, name='status'),
]
