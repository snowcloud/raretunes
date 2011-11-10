from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    # url(r'^$', direct_to_template, { 'template': 'home/index.html' }, name='rarefm_home'),
    url(r'^r(?P<short_id>\w+)/$', 'recordings.views.short_recording_detail', name='short-recording'),

)