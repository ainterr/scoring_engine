from django.conf.urls import url

import views, poller

import signal

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^status/$', views.status, name='status'),
]

# this code is executed only once on module load - so we start the poller
# thread here

poller.async().start()
